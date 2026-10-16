# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""Corpus-level BLEU, chrF, chrF++ and TER through sacreBLEU.

One place computes these four metrics so every caller gets the same
numbers and the same sacreBLEU signature describing how they were made.
"""

import sacrebleu

SACREBLEU_METRICS: frozenset[str] = frozenset({"bleu", "chrf", "chrf++", "ter"})


def score_sacrebleu(
    metric: str, hypotheses: list[str], references: list[list[str]]
) -> tuple[float, str]:
    """Scores a corpus on one sacreBLEU metric.

    `references[i]` is the list of references for `hypotheses[i]`. Returns
    the corpus score and the sacreBLEU signature that produced it. Raises
    ValueError, naming the metric, when it is not one this family computes.
    """
    if metric not in SACREBLEU_METRICS:
        raise ValueError(f"sacreBLEU does not implement metric '{metric}'")

    # sacreBLEU takes references transposed: one list per reference slot,
    # each as long as the hypotheses, padded with None for short groups.
    width = max(len(group) for group in references)
    transposed = [
        [group[i] if i < len(group) else None for group in references]
        for i in range(width)
    ]

    if metric == "bleu":
        scorer = sacrebleu.BLEU()
    elif metric == "chrf":
        scorer = sacrebleu.CHRF()
    elif metric == "chrf++":
        scorer = sacrebleu.CHRF(word_order=2)
    elif metric == "ter":
        scorer = sacrebleu.TER()

    score = scorer.corpus_score(hypotheses, transposed).score
    signature = str(scorer.get_signature())
    return score, signature
