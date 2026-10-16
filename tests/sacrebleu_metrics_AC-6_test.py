# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): a corpus whose hypotheses repeat their references word for
# word must score the maximum on rouge1, rouge2 and rougeL, and a corpus
# sharing no word with its references must score zero on all three.

from app.rouge_metrics import score_rouge


def test_rouge_scores_maximum_on_a_word_for_word_match():
    hypotheses = ["the cat sat on the mat", "a quick brown fox jumps"]
    references = [["the cat sat on the mat"], ["a quick brown fox jumps"]]

    for metric in ("rouge1", "rouge2", "rougeL"):
        score, _provenance = score_rouge(metric, hypotheses, references)
        assert score == 100.0


def test_rouge_scores_zero_when_no_word_is_shared_with_the_references():
    hypotheses = ["zzxxqq wwvvyy", "aabbcc ddeeff"]
    references = [["the cat sat on the mat"], ["a quick brown fox jumps"]]

    for metric in ("rouge1", "rouge2", "rougeL"):
        score, _provenance = score_rouge(metric, hypotheses, references)
        assert score == 0.0
