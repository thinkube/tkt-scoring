# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import string

from app.answers import normalise_answer


# WHY (INVARIANT): normalising follows SQuAD's official script: lowercase,
# delete every punctuation character without leaving a space, remove the
# articles a, an, the, then collapse whitespace.
def test_normalising_follows_squads_official_script():
    assert normalise_answer("U.S.A.") == "usa"
    assert normalise_answer("Rock 'n' Roll") == "rock n roll"
    assert normalise_answer("A  Tale\tof   an  Apple, the End") == "tale of apple end"
    for mark in string.punctuation:
        assert normalise_answer(f"ab{mark}cd") == "abcd", mark
