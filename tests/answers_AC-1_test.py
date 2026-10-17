# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import NORMALISATION, exact_match, normalise_answer


# WHY (INVARIANT): normalising follows SQuAD's official script: it lowercases,
# deletes punctuation outright (no space left behind), removes the articles a,
# an and the, and collapses whitespace, so answers differing only in those
# ways compare equal.
def test_normalise_matches_casing_punctuation_articles_and_whitespace():
    assert normalise_answer("The  Eiffel-Tower!") == "eiffeltower"
    assert normalise_answer("eiffeltower") == "eiffeltower"
    assert normalise_answer("U.S.A.") == "usa"
    assert normalise_answer("Rock 'n' Roll") == "rock n roll"
    assert normalise_answer("Eiffel-Tower") != normalise_answer("eiffel tower")
    assert exact_match("The  Eiffel-Tower!", ["eiffeltower"]) == 1


# WHY (INVARIANT): the method statement returned with results says punctuation
# is deleted without leaving a space, and still names the other steps.
def test_normalisation_statement_describes_deletion():
    text = NORMALISATION.lower()
    assert "deletes punctuation without leaving a space" in text
    assert "lowercase" in text
    assert "article" in text
    assert "whitespace" in text
