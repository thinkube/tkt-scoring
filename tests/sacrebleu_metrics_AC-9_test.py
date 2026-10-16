# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): rouge1, rouge2 and rougeL each answer a corpus score over
# the whole set of hypotheses together with the name of the ROUGE
# implementation and its version, so every rouge number is traceable to the
# library that produced it.

from app.rouge_metrics import score_rouge


def test_rouge1_rouge2_rougeL_return_score_and_provenance():
    hypotheses = ["the cat sat on the mat", "a quick brown fox jumps"]
    references = [["the cat sat on the mat"], ["a quick brown fox jumps"]]

    for metric in ("rouge1", "rouge2", "rougeL"):
        score, provenance = score_rouge(metric, hypotheses, references)
        assert isinstance(score, float)
        assert isinstance(provenance, str)
        assert provenance.strip() != ""
