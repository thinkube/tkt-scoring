# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: exact match is 1 when the prediction's normalised text equals at
# least one accepted answer's normalised text, and 0 when it equals none.
from app.answers import exact_match


def test_exact_match_is_one_when_normalised_text_matches_an_accepted_answer():
    assert exact_match("The Eiffel Tower", ["eiffel tower", "la tour eiffel"]) == 1.0


def test_exact_match_is_zero_when_normalised_text_matches_none():
    assert exact_match("Big Ben", ["eiffel tower", "la tour eiffel"]) == 0.0
