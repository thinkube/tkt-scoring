# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import normalise_answer


# WHY (TRANSITION): a hyphen joining two words no longer splits them - done
# once "Eiffel-Tower" and "eiffel tower" normalise to different texts.
def test_hyphen_no_longer_splits_words():
    assert normalise_answer("Eiffel-Tower") != normalise_answer("eiffel tower")
    assert normalise_answer("Eiffel-Tower") == "eiffeltower"
    assert normalise_answer("eiffel tower") == "eiffel tower"
