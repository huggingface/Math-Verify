from unittest.mock import patch

import pytest
import sympy

from math_verify import parse
from math_verify.grader import verify


def test_verify_raise_on_error():
    """
    When the internal comparison raises an error, `verify` should:

    1. return False if `raise_on_error=False`.
    2. propagate the original exception if `raise_on_error=True`.
    """
    with patch("math_verify.grader.sympy_expr_eq", side_effect=ValueError("boom")):
        # Should silently fail and return False
        assert not verify(sympy.Integer(1), sympy.Integer(1), raise_on_error=False)

        # Should re-raise the underlying error
        with pytest.raises(ValueError, match="boom"):
            verify(sympy.Integer(1), sympy.Integer(1), raise_on_error=True)


def test_chained_relations_of_different_length_compare_false():
    """A shorter chain is a wrong answer, including when errors are raised."""
    short = parse("$1<x<3$")
    long = parse("$1<x<3<5$")
    assert verify(short, long, raise_on_error=False) is False
    assert verify(short, long, raise_on_error=True) is False
    assert verify(long, short, raise_on_error=True) is False
    assert verify(short, short, raise_on_error=True) is True
