from sympy import Integer

from math_verify import parse


def test_failed_latex_does_not_supply_an_embedded_number():
    expression = r"\sum_{k=0}^n\bigl(k\bigr)"
    for text in [f"${expression}$", f"Final answer is ${expression}$. I hope."]:
        assert all(not isinstance(value, Integer) for value in parse(text))


def test_failed_latex_retains_independent_fallbacks():
    text = r"Final answer is $\sum_{k=0}^n\bigl(k\bigr)$. I hope. "
    for suffix in ["42", "$42$", "1/2"]:
        expected = parse(suffix)[0]
        assert parse(text + suffix)[0] == expected
        assert parse(text + suffix, extraction_mode="first_match")[0] != expected


def test_same_priority_and_multiple_latex_groups():
    assert parse(r"$\sum_{k=0}^n\bigl(k\bigr)$ and $42$")[0] == Integer(42)
    assert parse(r"$42$ and $\sum_{k=0}^n\bigl(k\bigr)$")[0] == Integer(42)
    assert (
        parse(r"$1$ and $2$")[0]
        == parse(r"$1$ and $2$", extraction_mode="first_match")[0]
    )
    assert parse("42")[0] == Integer(42)
