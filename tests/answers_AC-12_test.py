# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import normalise_answer


# WHY (INVARIANT): deleting punctuation outright means "The  Eiffel-Tower!"
# and "eiffeltower" are the same text, "eiffeltower".
def test_punctuated_and_plain_forms_normalise_to_the_same_text():
    assert normalise_answer("The  Eiffel-Tower!") == "eiffeltower"
    assert normalise_answer("eiffeltower") == "eiffeltower"
