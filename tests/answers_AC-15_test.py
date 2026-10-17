# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import exact_match


# WHY (INVARIANT): exact match compares after punctuation is deleted, so
# "The  Eiffel-Tower!" scores 1 against the accepted answer "eiffeltower".
def test_exact_match_scores_one_when_punctuation_deleted_matches():
    assert exact_match("The  Eiffel-Tower!", ["eiffeltower"]) == 1
