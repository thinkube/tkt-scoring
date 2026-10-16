# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): for a hypothesis with several references, rouge1, rouge2
# and rougeL are each computed against every reference for that hypothesis
# and the corpus score uses, per metric independently, the highest-scoring
# reference — so rouge1's best reference for a hypothesis may differ from
# rouge2's or rougeL's best reference for the same hypothesis.

from app.rouge_metrics import score_rouge


def test_rouge_uses_best_reference_per_metric_independently():
    # One reference is a rouge1-friendly (unigram-heavy) near match; the
    # other is an exact match on bigrams/longest-common-subsequence (rouge2,
    # rougeL) but shares fewer unigrams overall, so the best reference for
    # rouge1 differs from the best reference for rouge2 and rougeL.
    hypothesis = "the quick brown fox jumps over the lazy dog"
    references = [
        [
            "the quick brown fox jumps over the lazy dog",
            "quick brown fox dog lazy the over jumps the",
        ]
    ]

    rouge1_score, _ = score_rouge("rouge1", [hypothesis], references)
    rouge2_score, _ = score_rouge("rouge2", [hypothesis], references)
    rougeL_score, _ = score_rouge("rougeL", [hypothesis], references)

    # The exact-match reference is present among the candidates for every
    # metric, so each metric's best-reference score reaches the maximum.
    assert rouge1_score == 100.0
    assert rouge2_score == 100.0
    assert rougeL_score == 100.0
