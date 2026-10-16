# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import score_answers


# INVARIANT: the set-level numbers are the mean of the per-prediction exact
# match and token F1 over the whole set, reported on the 0-100 scale SQuAD
# uses (not 0-1).
def test_score_answers_is_the_mean_over_the_set_on_a_0_to_100_scale():
    items = [
        ("eiffel tower", ["eiffel tower"]),  # exact_match=1, f1=1
        ("banana", ["eiffel tower"]),  # exact_match=0, f1=0
    ]
    result = score_answers(items)
    assert result["exact_match"] == 50
    assert result["token_f1"] == 50
