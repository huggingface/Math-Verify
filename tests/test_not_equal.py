from math_verify import parse
from math_verify.grader import verify


def test_reversed_not_equal_matches():
    """The two sides of a not-equal can be written in either order."""
    pairs = [
        (r"$x \neq 1$", r"$1 \neq x$"),
        (r"$x \neq y$", r"$y \neq x$"),
        (r"$1 \neq 2$", r"$2 \neq 1$"),
        (r"$x \ne 1$", r"$1 \neq x$"),
    ]
    for gold, pred in pairs:
        assert (
            verify(parse(gold), parse(pred), timeout_seconds=None, raise_on_error=True)
            is True
        )
        assert (
            verify(parse(pred), parse(gold), timeout_seconds=None, raise_on_error=True)
            is True
        )


def test_different_not_equal_stays_false():
    """A different value, or an equality, is not the same answer."""
    pairs = [
        (r"$x \neq 1$", r"$x \neq 2$"),
        (r"$x \neq 1$", r"$x = 1$"),
        (r"$1 \neq 2$", r"$1 \neq 3$"),
        (r"$x \neq y$", r"$x \neq z$"),
    ]
    for gold, pred in pairs:
        assert (
            verify(parse(gold), parse(pred), timeout_seconds=None, raise_on_error=True)
            is False
        )
