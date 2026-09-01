import pytest
import sympy

from math_verify import ExprExtractionConfig, parse, verify

EXPR_EXTRACTION = (ExprExtractionConfig(),)


def test_parse_positive_mixed_number_as_complete_value():
    # Given
    prediction = "4 4/9"
    expected_value = sympy.Rational(40, 9)
    expected_fallback = "4 4/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


def test_parse_negative_mixed_number_as_negative_complete_value():
    # Given
    prediction = "-4 4/9"
    expected_value = sympy.Rational(-40, 9)
    expected_fallback = "-4 4/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


@pytest.mark.parametrize(
    ("prediction", "expected_fallback"),
    [
        pytest.param("11 5/6", "11 5/6", id="unsigned"),
        pytest.param("+11 5/6", "+11 5/6", id="explicit-positive"),
    ],
)
def test_parse_mixed_number_with_optional_positive_sign(prediction, expected_fallback):
    # Given
    expected_value = sympy.Rational(71, 6)

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


def test_extract_mixed_number_from_answer_sentence():
    # Given
    prediction = "The answer is 4 4/9."
    expected_value = sympy.Rational(40, 9)
    expected_fallback = "4 4/9"

    # When
    parsed = parse(prediction)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


def test_mixed_number_is_equivalent_to_improper_fraction():
    # Given
    gold = parse("40/9", EXPR_EXTRACTION)
    prediction = parse("The answer is 4 4/9.", EXPR_EXTRACTION)
    expected = True

    # When
    equivalent = verify(gold, prediction)

    # Then
    assert equivalent is expected


def test_mixed_number_does_not_match_only_its_whole_number_prefix():
    # Given
    gold = parse("4", EXPR_EXTRACTION)
    prediction = parse("The answer is 4 4/9.", EXPR_EXTRACTION)
    expected = False

    # When
    equivalent = verify(gold, prediction)

    # Then
    assert equivalent is expected


def test_parse_mixed_number_with_zero_whole_part():
    # Given
    prediction = "0 4/9"
    expected_value = sympy.Rational(4, 9)
    expected_fallback = "0 4/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


def test_parse_mixed_number_with_zero_numerator_as_whole_value():
    # Given
    prediction = "4 0/9"
    expected_value = sympy.Integer(4)
    expected_fallback = "4 0/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert verify([expected_value], parsed) is True
    assert parsed[1] == expected_fallback


def test_parse_mixed_number_with_spaced_thousands_whole_part():
    # Given
    prediction = "1 000 4/9"
    expected_value = sympy.Rational(9004, 9)
    expected_fallback = "1 000 4/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected_value) == 0
    assert parsed[1] == expected_fallback


@pytest.mark.parametrize(
    ("prediction", "expected_fallback", "finite_candidates"),
    [
        pytest.param("4 4/0", "4 4/0", ("4", "0"), id="zero-denominator"),
        pytest.param("4 0/0", "4 0/0", ("4", "0"), id="zero-over-zero"),
        pytest.param("-4 0/0", "-4 0/0", ("-4", "0"), id="negative"),
        pytest.param("0 0/0", "0 0/0", ("0",), id="zero-whole"),
        pytest.param("1 000 0/0", "1 000 0/0", ("1000", "0"), id="spaced-thousands"),
        pytest.param(
            "-1 000 0/0",
            "-1 000 0/0",
            ("-1000", "0"),
            id="negative-spaced-thousands",
        ),
        pytest.param(
            "11 6/6",
            "11 6/6",
            ("11", "1", "12", "10"),
            id="fraction-equal-to-one",
        ),
        pytest.param(
            "11 7/6",
            "11 7/6",
            ("11", "7/6", "73/6", "59/6"),
            id="improper-fraction",
        ),
        pytest.param(
            "The answer is 11 6/6.",
            "11 6/6",
            ("11", "1", "12", "10"),
            id="answer-anchored-improper",
        ),
        pytest.param(
            "The answer is 4 0/0.",
            "4 0/0",
            ("4", "0"),
            id="answer-anchored-zero-denominator",
        ),
    ],
)
def test_invalid_mixed_number_has_no_finite_component_equivalence(
    prediction, expected_fallback, finite_candidates
):
    # Given
    finite_values = [parse(value, EXPR_EXTRACTION) for value in finite_candidates]
    expected_equivalences = [False] * len(finite_values)

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)
    equivalences = [verify(finite_value, parsed) for finite_value in finite_values]

    # Then
    assert equivalences == expected_equivalences
    assert parsed[1] == expected_fallback


@pytest.mark.parametrize(
    ("prediction", "inserted_operation_values"),
    [
        pytest.param("11/10 4/9", ("139/90", "59/90"), id="fractional-whole"),
        pytest.param("11.0 4/9", ("103/9", "95/9"), id="decimal-whole"),
        pytest.param("(11) 4/9", ("103/9", "95/9"), id="parenthesized-whole"),
        pytest.param(
            "11/10\n4/9",
            ("139/90", "59/90"),
            id="line-separated-fractions",
        ),
    ],
)
def test_non_mixed_syntax_does_not_gain_an_implicit_operation(
    prediction, inserted_operation_values
):
    # Given
    incorrectly_combined_values = [
        parse(value, EXPR_EXTRACTION) for value in inserted_operation_values
    ]
    expected_equivalences = [False] * len(incorrectly_combined_values)

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)
    equivalences = [
        verify(incorrectly_combined, parsed)
        for incorrectly_combined in incorrectly_combined_values
    ]

    # Then
    assert equivalences == expected_equivalences


@pytest.mark.parametrize(
    "line_separator",
    [pytest.param("\n", id="newline"), pytest.param("\r\n", id="crlf")],
)
def test_line_separator_does_not_form_a_mixed_number(line_separator):
    # Given
    prediction = f"11{line_separator}5/6"
    incorrectly_combined = parse("71/6", EXPR_EXTRACTION)
    existing_non_mixed_value = parse("5", EXPR_EXTRACTION)

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)
    matches_mixed_number = verify(incorrectly_combined, parsed)
    preserves_existing_value = verify(existing_non_mixed_value, parsed)

    # Then
    assert matches_mixed_number is False
    assert preserves_existing_value is True


def test_explicit_addition_and_subtraction_remain_distinct():
    # Given
    addition = "11 + 4/9"
    subtraction = "11 - 4/9"
    expected_addition = sympy.Rational(103, 9)
    expected_subtraction = sympy.Rational(95, 9)

    # When
    parsed_addition = parse(addition, EXPR_EXTRACTION)
    parsed_subtraction = parse(subtraction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed_addition[0] - expected_addition) == 0
    assert sympy.simplify(parsed_subtraction[0] - expected_subtraction) == 0
    assert verify(parsed_addition, parsed_subtraction) is False


@pytest.mark.parametrize(
    "suffix",
    [
        pytest.param("%", id="symbol"),
        pytest.param(" %", id="spaced-symbol"),
        pytest.param("percent", id="percent"),
        pytest.param(" percent", id="spaced-percent"),
        pytest.param("percentage", id="percentage"),
        pytest.param(" percentage", id="spaced-percentage"),
        pytest.param("pct", id="pct"),
        pytest.param(" pct", id="spaced-pct"),
    ],
)
def test_mixed_number_percentage_applies_to_complete_value(suffix):
    # Given
    prediction = f"4 4/9{suffix}"
    percentage_value = parse("40/900", EXPR_EXTRACTION)
    unscaled_value = parse("40/9", EXPR_EXTRACTION)
    expected_fallback = "4 4/9"

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)
    matches_percentage = verify(percentage_value, parsed)
    matches_unscaled_value = verify(unscaled_value, parsed)

    # Then
    assert matches_percentage is True
    assert matches_unscaled_value is False
    assert parsed[1] == expected_fallback


@pytest.mark.parametrize(
    ("prediction", "expected_value"),
    [
        pytest.param("4 + 4/9", sympy.Rational(40, 9), id="sum"),
        pytest.param("10/2", sympy.Integer(5), id="fraction"),
        pytest.param("1 000", sympy.Integer(1000), id="spaced-thousands"),
        pytest.param("$5.00", sympy.Integer(5), id="currency-decimal"),
        pytest.param("28%", sympy.Rational(7, 25), id="percentage"),
        pytest.param(
            "There are 4 objects and 4/9 remain.",
            sympy.Rational(4, 9),
            id="independent-numbers",
        ),
        pytest.param(
            "4 4/9 2",
            sympy.Integer(2),
            id="mixed-looking-sequence-followed-by-independent-number",
        ),
    ],
)
def test_existing_expression_syntax_is_unchanged(prediction, expected_value):
    # Given
    expected = expected_value

    # When
    parsed = parse(prediction, EXPR_EXTRACTION)

    # Then
    assert sympy.simplify(parsed[0] - expected) == 0
