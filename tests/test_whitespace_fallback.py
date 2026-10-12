# Regression tests for whitespace handling in the fallback string comparison.
#
# When a LaTeX answer cannot be converted to a sympy expression (e.g. "28 \%"),
# grader.verify falls back to comparing the extracted strings. The same answer
# can be extracted with or without internal spaces depending on the source:
# "28 \%" from "$28 \%$" vs "28\%" from "\boxed{28\%}". The fallback used to
# compare with `==` after only stripping the ends, so these compared unequal.


from math_verify import parse, verify
from math_verify.parser import LatexExtractionConfig


def test_fallback_string_comparison_ignores_internal_whitespace():
    gold = parse(r"The final answer is $28 \%$.", (LatexExtractionConfig(),))
    pred = parse(r"The answer is $\boxed{28\%}$.", (LatexExtractionConfig(),))
    assert verify(gold, pred) is True


def test_fallback_string_comparison_still_rejects_different_strings():
    gold = parse(r"The final answer is $28 \%$.", (LatexExtractionConfig(),))
    pred = parse(r"The answer is $\boxed{29\%}$.", (LatexExtractionConfig(),))
    assert verify(gold, pred) is False


def test_fallback_string_comparison_rejects_empty():
    # Whitespace-only strings must never compare equal to anything.
    assert verify("  ", "28\\%") is False
    assert verify("28\\%", "   ") is False
    assert verify("   ", "  ") is False
