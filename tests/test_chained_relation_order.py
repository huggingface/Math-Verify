from math_verify import parse
from math_verify.grader import verify


def test_reversed_chained_relations_match():
    """The same chain written in the other direction is the same answer."""
    assert verify(parse(r"$1<x<3$"), parse(r"$3>x>1$"), timeout_seconds=None) is True
    assert (
        verify(
            parse(r"$1\leq x\leq 3$"), parse(r"$3\geq x\geq 1$"), timeout_seconds=None
        )
        is True
    )
    assert verify(parse(r"$x<y<z$"), parse(r"$z>y>x$"), timeout_seconds=None) is True
    assert verify(parse(r"$x=y=1$"), parse(r"$y=x=1$"), timeout_seconds=None) is True
    assert verify(parse(r"$1<x<3$"), parse(r"$1<x<3$"), timeout_seconds=None) is True


def test_different_chained_relations_stay_false():
    """A different condition, including a longer chain, is not a match."""
    assert (
        verify(
            parse(r"$1<x<3$"),
            parse(r"$3<x<1$"),
            timeout_seconds=None,
            raise_on_error=True,
        )
        is False
    )
    assert (
        verify(
            parse(r"$1<x<3$"),
            parse(r"$1<x<3<5$"),
            timeout_seconds=None,
            raise_on_error=True,
        )
        is False
    )
    assert (
        verify(
            parse(r"$x=y=1$"),
            parse(r"$x=y=2$"),
            timeout_seconds=None,
            raise_on_error=True,
        )
        is False
    )
