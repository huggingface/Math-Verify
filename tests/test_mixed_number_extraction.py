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


def test_zero_denominator_does_not_fall_back_to_whole_number_prefix():
    # Given
    invalid_mixed_number = "4 4/0"
    whole_number = parse("4", EXPR_EXTRACTION)
    expected = False

    # When
    parsed = parse(invalid_mixed_number, EXPR_EXTRACTION)
    equivalent = verify(whole_number, parsed)

    # Then
    assert equivalent is expected
    assert parsed[1] == invalid_mixed_number


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
