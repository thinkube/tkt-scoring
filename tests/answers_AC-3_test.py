# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import token_f1


# INVARIANT: token F1 against the best-scoring accepted answer is 1 for a
# token-for-token repeat, 0 for no shared token, and strictly between the
# two for a partial overlap.
def test_token_f1_scores_full_none_and_partial_overlap():
    assert token_f1("eiffel tower", ["The Eiffel Tower"]) == 1
    assert token_f1("banana", ["eiffel tower"]) == 0

    partial = token_f1("the eiffel", ["the eiffel tower"])
    assert 0 < partial < 1
