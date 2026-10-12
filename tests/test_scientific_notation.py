# Regression tests for scientific notation in ExprExtractionConfig.
#
# The expr number regex used to stop right after the mantissa, so "1.5e3"
# was extracted as 1.5 (and "6.02e23" as 6.02), making e.g.
# verify("The answer is 1.5e3.", "The answer is 1500.") fail although the
# two answers are numerically identical.


from math_verify import parse, verify
from math_verify.parser import ExprExtractionConfig


CFG = (ExprExtractionConfig(),)


def test_positive_exponent():
    parsed = parse("The answer is 1.5e3.", CFG)
    # NB: compare as float; sympy Float carries the mantissa's precision,
    # so `Float('1.5e3') == 1500` is False by sympy's precision semantics.
    assert float(parsed[0]) == 1500.0


def test_large_exponent():
    parsed = parse("The answer is 6.02e23.", CFG)
    assert float(parsed[0]) == 6.02e23


def test_negative_exponent():
    parsed = parse("The answer is 2e-4.", CFG)
    assert float(parsed[0]) == 2e-4


def test_uppercase_exponent():
    parsed = parse("The answer is 2E-4.", CFG)
    assert float(parsed[0]) == 2e-4


def test_scientific_notation_verifies_equal_to_plain():
    gold = parse("The answer is 1500.", CFG)
    pred = parse("The answer is 1.5e3.", CFG)
    assert verify(gold, pred) is True


def test_trailing_e_without_digits_is_not_exponent():
    # "word1e" has no digits after e: the trailing "1" must not be extracted
    # as a standalone number.
    parsed = parse("The answer is word1e.", CFG)
    assert parsed == []
