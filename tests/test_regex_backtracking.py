import time

import pytest

from math_verify.parser import parse


# Unclosed display environments followed by many \boxed{} used to backtrack super-linearly
# in the boxed-context regex, so parse() timed out and lost the answer (issue #91).
@pytest.mark.parametrize(
    "text",
    [
        "$$\n" + "\\boxed{5940}\n" * 2000,
        "$$x$$\n" + "\\boxed{5940}\n" * 2000,
        "\\[\n" + "\\boxed{5940}\n" * 2000,
        "\\[\\boxed{5940}\n" * 300,
    ],
    ids=[
        "unclosed_dollar",
        "closed_then_boxes",
        "unclosed_bracket",
        "many_unclosed_brackets",
    ],
)
def test_unclosed_display_env_with_many_boxes(text):
    start = time.perf_counter()
    result = parse(text)
    elapsed = time.perf_counter() - start
    assert [str(x) for x in result] == ["5940", "5940"]
    assert elapsed < 2


@pytest.mark.parametrize(
    "text",
    [
        "So $$\\boxed{5940}$$",
        "So \\[\\boxed{5940}\\]",
        "So $$x = \\boxed{5940}$$ and more text",
        "So \\[ x = 1 \\] then \\[\\boxed{5940}\\]",
    ],
)
def test_closed_display_env_still_extracts_boxed(text):
    assert [str(x) for x in parse(text)] == ["5940", "5940"]
