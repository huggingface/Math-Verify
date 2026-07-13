import multiprocessing
import os
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from math_verify import utils
from math_verify.errors import TimeoutException
from math_verify.grader import verify
from math_verify.parser import parse
from math_verify.utils import timeout


@patch("math_verify.parser.parse_expr")
def test_timeout_expr(mock_parse_expr):
    # Mock the parsing function to simulate a delay
    def delayed_parse(*args, **kwargs):
        time.sleep(5)  # Simulate a delay longer than the timeout
        return "parsed_expr"

    mock_parse_expr.side_effect = delayed_parse

    # Test that the timeout is triggered
    x = parse(
        "1+1",
        parsing_timeout=1,
        extraction_mode="first_match",
        fallback_mode="no_fallback",
    )
    assert x == []


@patch("math_verify.parser.latex2sympy")
def test_timeout_latex(mock_parse_latex):
    # Mock the parsing function to simulate a delay
    def delayed_parse(*args, **kwargs):
        time.sleep(5)  # Simulate a delay longer than the timeout
        return "parsed_expr"

    mock_parse_latex.side_effect = delayed_parse

    # Test that the timeout is triggered
    x = parse(
        "$1+1$",
        parsing_timeout=1,
        extraction_mode="first_match",
        fallback_mode="no_fallback",
    )
    assert x == []


@patch("math_verify.grader.sympy_expr_eq")
def test_timeout_verify(mock_verify):
    # Mock the verify function to simulate a delay
    def delayed_sympy_expr_eq(*args, **kwargs):
        time.sleep(5)  # Simulate a delay longer than the timeout
        return True

    mock_verify.side_effect = delayed_sympy_expr_eq

    gold = [parse("1+1")[0]]
    assert not verify(gold, gold, timeout_seconds=1)


def test_windows_timeout_supports_local_callables(monkeypatch):
    monkeypatch.setattr(utils, "os", SimpleNamespace(name="nt"))
    parent_pid = os.getpid()

    def noisy_local_callable():
        os.write(1, b"worker output must not corrupt the protocol")
        return os.getpid(), lambda value: value + 1

    child_pid, result = timeout(2)(noisy_local_callable)()

    assert child_pid != parent_pid
    assert result(2) == 3


def test_windows_timeout_supports_parse_and_verify(monkeypatch):
    monkeypatch.setattr(utils, "os", SimpleNamespace(name="nt"))

    assert {str(value) for value in parse(r"\boxed{4}", raise_on_error=True)} == {"4"}
    assert verify("4", "4", strict=True, timeout_seconds=2, raise_on_error=True)


def test_windows_timeout_terminates_child(monkeypatch):
    monkeypatch.setattr(utils, "os", SimpleNamespace(name="nt"))
    children_before = {child.pid for child in multiprocessing.active_children()}

    with pytest.raises(TimeoutException, match="Operation timed out"):
        timeout(0.1)(lambda: time.sleep(5))()

    children_after = {child.pid for child in multiprocessing.active_children()}
    assert children_after == children_before


def test_windows_timeout_propagates_child_timeout(monkeypatch):
    monkeypatch.setattr(utils, "os", SimpleNamespace(name="nt"))

    def raise_timeout():
        raise TimeoutException("child timeout")

    with pytest.raises(TimeoutException, match="child timeout"):
        timeout(2)(raise_timeout)()


@pytest.mark.skipif(sys.platform != "win32", reason="requires native taskkill")
def test_windows_timeout_terminates_descendants(tmp_path):
    pid_path = tmp_path / "descendant.pid"

    def spawn_descendant():
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
        )
        pid_path.write_text(str(child.pid))
        time.sleep(30)

    with pytest.raises(TimeoutException, match="Operation timed out"):
        timeout(1)(spawn_descendant)()

    descendant_pid = pid_path.read_text()
    tasklist = subprocess.run(
        ["tasklist", "/FI", f"PID eq {descendant_pid}"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert descendant_pid not in tasklist.stdout
