# MIT License

# Copyright (c) 2024 The HuggingFace Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import functools
import logging
import os
import subprocess
import sys

import cloudpickle

from math_verify.errors import TimeoutException

TIMEOUT_WARNING_SHOWN = False
logger = logging.getLogger(__name__)


def _terminate_process(process: subprocess.Popen) -> None:
    """Terminate a timeout worker and its descendants."""
    if process.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if process.poll() is None:
        process.kill()
    process.wait()


def timeout(timeout_seconds: int | None = 10):  # noqa: C901
    """A decorator that applies a timeout to the decorated function.

    Args:
        timeout_seconds (int): Number of seconds before timing out the decorated function.
            Defaults to 10 seconds.

    Notes:
        On Unix systems, uses a signal-based alarm approach which is more efficient as it doesn't require spawning a new process.
        On Windows systems, uses a subprocess since signal.alarm is not available. This will incur a performance penalty.
    """
    if timeout_seconds is None or timeout_seconds <= 0:

        def no_timeout_decorator(func):
            return func

        return no_timeout_decorator

    if os.name == "posix":
        # Unix-like approach: signal.alarm
        import signal

        def decorator(func):
            def handler(signum, frame):
                raise TimeoutException("Operation timed out!")

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                old_handler = signal.getsignal(signal.SIGALRM)
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(timeout_seconds)
                try:
                    return func(*args, **kwargs)
                finally:
                    # Cancel the alarm and restore previous handler
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

            return wrapper

        return decorator

    else:

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                payload = cloudpickle.dumps((func, args, kwargs))
                process = subprocess.Popen(
                    [sys.executable, "-m", "math_verify.timeout_worker"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    creationflags=(
                        getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                        if sys.platform == "win32"
                        else 0
                    ),
                )

                try:
                    output, _ = process.communicate(payload, timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    _terminate_process(process)
                    process.communicate()
                    raise TimeoutException("Operation timed out!") from None

                if process.returncode:
                    raise RuntimeError(
                        f"Timeout worker exited with code {process.returncode}"
                    )
                try:
                    success, value = cloudpickle.loads(output)
                except Exception as exc:
                    raise RuntimeError(
                        "Timeout worker returned an invalid response"
                    ) from exc

                if success:
                    return value
                if isinstance(value, BaseException):
                    raise value
                raise RuntimeError("Timeout worker returned an invalid exception")

            return wrapper

        return decorator
