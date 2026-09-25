import pytest

pd = pytest.importorskip("pandas")

import evaluate_model_outputs  # noqa: E402


def fake_math_metric(**kwargs):
    """Stand-in for `math_metric` that keeps only the behaviour tested here.

    A gold wrapped in `$...$` is readable and graded by string equality. Any
    other gold raises the ValueError that `math_metric` raises when no gold
    target can be extracted.
    """

    def verify_func(golds, predictions):
        gold, pred = golds[0], predictions[0]
        if not (len(gold) > 1 and gold.startswith("$") and gold.endswith("$")):
            raise ValueError(
                f"No gold targets found for at least one gold. Gold: {golds}, "
                f"Pred: {predictions}"
            )
        grade = 1.0 if gold[1:-1] == pred else 0.0
        return grade, ([gold[1:-1]], [pred])

    return verify_func


@pytest.fixture
def evaluate(monkeypatch):
    monkeypatch.setattr(evaluate_model_outputs, "math_metric", fake_math_metric)

    def run(rows):
        df = pd.DataFrame(
            {
                "answer": [answer for answer, _ in rows],
                "gold": [gold for _, gold in rows],
            }
        )
        return evaluate_model_outputs.process_answers(df, gold_is_latex=True)

    return run


def test_unreadable_gold_rows_are_counted_as_incorrect(evaluate):
    results = evaluate([("42", "$42$"), ("7", "$8$"), ("5", "42"), ("6", "42")])

    assert list(results["is_correct"]) == [True, False, False, False]
    assert results.attrs["total_count"] == 4
    assert results.attrs["correct_count"] == 1
    assert results.attrs["accuracy"] == pytest.approx(0.25)


def test_printed_accuracy_matches_is_correct_column(evaluate, capsys):
    results = evaluate([("42", "$42$"), ("5", "42")])

    out = capsys.readouterr().out
    assert "Total examples: 2" in out
    assert "Correct answers: 1" in out
    assert "Accuracy: 50.00%" in out
    is_correct = list(results["is_correct"])
    assert results.attrs["accuracy"] == pytest.approx(sum(is_correct) / len(is_correct))


def test_all_rows_unreadable(evaluate):
    results = evaluate([("1", "1"), ("2", "2"), ("3", "3")])

    assert results.attrs["total_count"] == 3
    assert results.attrs["correct_count"] == 0
    assert results.attrs["accuracy"] == 0


def test_readable_golds_are_counted_once(evaluate):
    results = evaluate([("42", "$42$"), ("1", "$1$"), ("7", "$8$")])

    assert list(results["is_correct"]) == [True, True, False]
    assert results.attrs["total_count"] == 3
    assert results.attrs["correct_count"] == 2
    assert results.attrs["accuracy"] == pytest.approx(2 / 3)


def test_empty_input(evaluate):
    results = evaluate([])

    assert results.attrs["total_count"] == 0
    assert results.attrs["correct_count"] == 0
    assert results.attrs["accuracy"] == 0
