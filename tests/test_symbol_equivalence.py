import pytest
from sympy import E, Symbol

from math_verify import parse, verify


@pytest.mark.parametrize(
    "gold, pred",
    [
        (r"$x$", r"$2x - x$"),
        (r"$x$", r"$x + 0$"),
        (r"$x$", r"$1 \cdot x$"),
        (r"$x$", r"$\frac{2x}{2}$"),
        (r"$2x - x$", r"$x$"),
        (r"$y$", r"$3y - 2y$"),
        (r"$x$", r"$x(\sin^2(t) + \cos^2(t))$"),
    ],
)
def test_symbol_equivalent_expression_matches(gold: str, pred: str) -> None:
    gold_parsed = parse(gold, parsing_timeout=None)
    pred_parsed = parse(pred, parsing_timeout=None)
    assert verify(gold_parsed, pred_parsed, timeout_seconds=None) is True


@pytest.mark.parametrize(
    "gold, pred, strict, expected",
    [
        (r"$x$", r"$2x$", True, False),
        (r"$x$", r"$x + 1$", True, False),
        (r"$x$", r"$x^2$", True, False),
        (r"$x$", r"$y$", True, False),
        (r"$x$", r"$y$", False, True),
        (r"$\text{answer}$", r"$answer$", True, True),
    ],
)
def test_symbol_non_regression(
    gold: str, pred: str, strict: bool, expected: bool
) -> None:
    gold_parsed = parse(gold, parsing_timeout=None)
    pred_parsed = parse(pred, parsing_timeout=None)
    assert (
        verify(gold_parsed, pred_parsed, strict=strict, timeout_seconds=None)
        is expected
    )


def test_symbol_special_comparisons_preserved() -> None:
    assert verify(Symbol("e"), E, timeout_seconds=None) is True
    assert verify(Symbol("ABC"), Symbol("abc"), timeout_seconds=None) is True
    assert verify(Symbol("x"), Symbol("X"), strict=True, timeout_seconds=None) is False
