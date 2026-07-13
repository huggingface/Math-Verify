"""Subprocess entry point for Windows timeout execution."""

from __future__ import annotations

import contextlib
import sys

import cloudpickle


def main() -> None:
    try:
        func, args, kwargs = cloudpickle.loads(sys.stdin.buffer.read())
        try:
            with contextlib.redirect_stdout(sys.stderr):
                response = (True, func(*args, **kwargs))
        except BaseException as exc:
            response = (False, exc)
    except BaseException as exc:
        response = (False, RuntimeError(f"Unable to start timeout worker: {exc}"))

    try:
        payload = cloudpickle.dumps(response)
    except BaseException as exc:
        payload = cloudpickle.dumps(
            (False, RuntimeError(f"Unable to serialize timeout worker response: {exc}"))
        )
    sys.stdout.buffer.write(payload)


if __name__ == "__main__":
    main()
