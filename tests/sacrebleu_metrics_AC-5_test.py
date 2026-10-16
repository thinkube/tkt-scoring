# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): chrf and chrf++ must answer different numbers and
# different signatures, with the chrf++ signature stating a word order of 2
# (sacreBLEU's "w:2" marker), so a caller can tell the two metrics apart from
# their provenance alone, not only from their score.

from app.sacrebleu_metrics import score_sacrebleu


def test_chrf_and_chrfpp_differ_in_score_and_signature():
    hypotheses = ["the cat sat on the mat", "a quick brown fox jumps"]
    references = [["the dog sat on the rug"], ["a slow brown fox walks"]]

    chrf_score, chrf_signature = score_sacrebleu("chrf", hypotheses, references)
    chrfpp_score, chrfpp_signature = score_sacrebleu("chrf++", hypotheses, references)

    assert chrf_score != chrfpp_score
    assert chrf_signature != chrfpp_signature
    assert "w:2" in chrfpp_signature
