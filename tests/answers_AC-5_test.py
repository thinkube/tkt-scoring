# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.answers import NORMALISATION


# INVARIANT: the stated normalisation sentence names all four steps that
# are actually applied -- case, punctuation, articles, whitespace -- so a
# reader of the constant alone knows what normalise_answer does.
def test_normalisation_statement_names_all_four_steps():
    statement = NORMALISATION.lower()
    assert "case" in statement or "lower" in statement
    assert "punctuation" in statement
    assert "article" in statement
    assert "whitespace" in statement or "space" in statement
