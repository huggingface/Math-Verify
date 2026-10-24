"""Test equation comparisons for relations with and without free symbols.

Regression test for: https://github.com/huggingface/math-verify/issues/87
Prevents vacuous all([]) equality matches on symbol-free equations with empty solution sets
and prevents false equivalence on constant numerical relations with matching differences.
"""

from math_verify import parse, verify


def test_symbol_free_different_equations_fail():
    """Verify that different equations without free symbols do not falsely verify as True."""
    # Issue #87 OlympiadBench case
    gold = parse(r"$I_{e}(0)=\gamma I_{i}(0)$")
    pred = parse(r"$I_{i}(0) = I_{e}(0)$")
    assert not verify(gold=gold, target=pred)

    # Contradictory numerical equations (same difference: 3 - 4 == 1 - 2 == -1)
    gold_num = parse(r"$3 = 4$")
    pred_num = parse(r"$1 = 2$")
    assert not verify(gold=gold_num, target=pred_num)

    # Different numerical equations (different difference: 3 - 4 == -1, 1 - 3 == -2)
    gold_diff = parse(r"$3 = 4$")
    pred_diff = parse(r"$1 = 3$")
    assert not verify(gold=gold_diff, target=pred_diff)


def test_symbol_free_identical_and_flipped_equations_pass():
    """Verify that identical and flipped equations without free symbols still verify as True."""
    gold = parse(r"$I_{e}(0)=\gamma I_{i}(0)$")
    pred_identical = parse(r"$I_{e}(0)=\gamma I_{i}(0)$")
    assert verify(gold=gold, target=pred_identical)

    pred_flipped = parse(r"$\gamma I_{i}(0) = I_{e}(0)$")
    assert verify(gold=gold, target=pred_flipped)


def test_numerical_relations_direct_and_flipped():
    """Verify numerical relations compare values directly or inverted rather than false difference matching."""
    # Equalities
    gold_eq = parse(r"$3 = 4$")
    assert verify(gold=gold_eq, target=parse(r"$3 = 4$"))
    assert verify(gold=gold_eq, target=parse(r"$4 = 3$"))
    assert verify(gold=gold_eq, target=parse(r"$1 + 2 = 4$"))

    # Inequalities
    gold_lt = parse(r"$1 < 2$")
    assert verify(gold=gold_lt, target=parse(r"$1 < 2$"))
    assert verify(gold=gold_lt, target=parse(r"$2 > 1$"))
    assert not verify(gold=gold_lt, target=parse(r"$3 < 4$"))


def test_equations_with_symbols_still_solve_and_compare():
    """Verify that equations with free symbols continue to solve and match equivalent solutions."""
    gold = parse(r"$x = 5$")
    pred = parse(r"$2x = 10$")
    assert verify(gold=gold, target=pred)

    gold_diff = parse(r"$x = 5$")
    pred_diff = parse(r"$x = 7$")
    assert not verify(gold=gold_diff, target=pred_diff)

    # Multi-variable equations
    gold_multi = parse(r"$x + y = 5$")
    pred_multi = parse(r"$2x + 2y = 10$")
    assert verify(gold=gold_multi, target=pred_multi)

    pred_multi_diff = parse(r"$x + y = 6$")
    assert not verify(gold=gold_multi, target=pred_multi_diff)
