from math_verify import parse
from math_verify.grader import verify


def test_absolute_value_matches_the_interval():
    """|e| < c is the same real condition as -c < e < c."""
    pairs = [
        (r"$|x|<1$", r"$-1<x<1$"),
        (r"$|x|\leq 1$", r"$-1\leq x\leq 1$"),
        (r"$1>|x|$", r"$-1<x<1$"),
        (r"$|x|<1$", r"$1>x>-1$"),
        (r"$|2x-1|<3$", r"$-3<2x-1<3$"),
        (r"$|x+y|<1$", r"$-1<x+y<1$"),
        (r"$|x|<\frac{1}{2}$", r"$-\frac{1}{2}<x<\frac{1}{2}$"),
        (r"$|x|>1$", r"$1<|x|$"),
        (r"$|x|\geq 1$", r"$1\leq |x|$"),
    ]
    for gold, pred in pairs:
        assert verify(parse(gold), parse(pred), timeout_seconds=None) is True
        assert verify(parse(pred), parse(gold), timeout_seconds=None) is True


def test_different_absolute_bounds_stay_false():
    """A smaller interval, a closed bound, or a different expression stays wrong."""
    pairs = [
        (r"$|x|<1$", r"$0<x<1$"),
        (r"$|x|<1$", r"$-1\leq x\leq 1$"),
        (r"$|x|\leq 1$", r"$-1<x<1$"),
        (r"$|x|<1$", r"$-2<x<2$"),
        (r"$|x|<1$", r"$|x|<2$"),
        (r"$|x|>1$", r"$-1<x<1$"),
        (r"$|x|<1$", r"$1<x<3<5$"),
        (r"$|x+y|<1$", r"$-1<x<1$"),
        (r"$|x|<1$", r"$|y|<1$"),
        (r"$|x|<0$", r"$-1<x<1$"),
    ]
    for gold, pred in pairs:
        assert (
            verify(parse(gold), parse(pred), timeout_seconds=None, raise_on_error=True)
            is False
        )
