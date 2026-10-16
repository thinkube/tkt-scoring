# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: normalising an answer lowercases it, strips punctuation and
# articles (a, an, the), and collapses whitespace runs, so two answers that
# differ only in case, punctuation, articles or spacing compare equal.
from app.answers import normalise_answer


def test_normalise_matches_casing_punctuation_articles_and_whitespace():
    assert normalise_answer("The  Eiffel-Tower!") == normalise_answer("eiffel tower")
