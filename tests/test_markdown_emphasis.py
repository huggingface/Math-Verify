# MIT License

# Copyright (c) 2024 The HuggingFace Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A final answer in Markdown bold (`**129**`) must be read as 129.

`\\*` is an operator character for plain expressions, so `129**` used to match as an
expression, fail to parse, and leave the value to an earlier number in the response.
"""

import pytest

from math_verify import parse, verify

DRAFT_THEN_BOLD = "ANSWER: 18\nWait, I made an error.\nANSWER: **129**"


@pytest.mark.parametrize(
    "pred,gold,expected",
    [
        # a withdrawn draft must not win over the bold final answer
        (DRAFT_THEN_BOLD, "129", True),
        (DRAFT_THEN_BOLD, "18", False),
        ("ANSWER: 18\nWait, I made an error.\n**ANSWER: 129**", "129", True),
        ("ANSWER: 18\nWait, I made an error.\n**ANSWER: 129**", "18", False),
        (
            "The answer is 18. Wait, I made an error. The final answer is **129**.",
            "129",
            True,
        ),
        (
            "The answer is 18. Wait, I made an error. The final answer is **129**.",
            "18",
            False,
        ),
        # bold alone, numbers and expressions
        ("ANSWER: **129**", "129", True),
        ("ANSWER: **-7**", "-7", True),
        ("ANSWER: **0.25**", "0.25", True),
        ("ANSWER: **3/4**", "3/4", True),
        ("The answer is **2*3**.", "6", True),
        # unchanged: plain expressions and numbers
        ("The answer is 2*3.", "6", True),
        ("ANSWER: 18\nWait, I made an error.\nANSWER: 129", "129", True),
    ],
)
def test_bold_final_answer(pred, gold, expected):
    assert verify(parse(gold), parse(pred)) == expected


@pytest.mark.parametrize("pred", ["ANSWER: **129**", DRAFT_THEN_BOLD])
def test_bold_final_answer_first_match(pred):
    # with extraction_mode="first_match" (as lighteval's math scorer uses) the bold
    # answer used to come back only as the unparsed string "129**"
    parsed = parse(pred, extraction_mode="first_match")
    assert verify(parse("129"), parsed)
    assert "129**" not in parsed
