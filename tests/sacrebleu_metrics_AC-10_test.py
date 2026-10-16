# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): a corpus whose hypotheses repeat their references word for
# word must score the maximum on rouge1, rouge2 and rougeL, and a corpus
# sharing no word with its references must score zero on all three.

from app.rouge_metrics import score_rouge


def test_rouge_scores_maximum_on_perfect_match_and_zero_on_no_overlap():
    hypotheses = ["the cat sat on the mat", "a quick brown fox jumps"]
    perfect_references = [["the cat sat on the mat"], ["a quick brown fox jumps"]]

    for metric in ("rouge1", "rouge2", "rougeL"):
        score, _provenance = score_rouge(metric, hypotheses, perfect_references)
        assert score == 100.0

    no_overlap_hypotheses = ["zzxxqq wwvvyy", "aabbcc ddeeff"]
    no_overlap_references = [["the cat sat on the mat"], ["a quick brown fox jumps"]]

    for metric in ("rouge1", "rouge2", "rougeL"):
        score, _provenance = score_rouge(metric, no_overlap_hypotheses, no_overlap_references)
        assert score == 0.0
