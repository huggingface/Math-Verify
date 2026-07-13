"""Subprocess entry point for Windows timeout execution."""

from __future__ import annotations

import sys
from pathlib import Path

import cloudpickle


def main() -> None:
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    try:
        func, args, kwargs = cloudpickle.loads(input_path.read_bytes())
        try:
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
    output_path.write_bytes(payload)


if __name__ == "__main__":
    main()
