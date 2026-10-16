# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""Corpus-level ROUGE-1, ROUGE-2 and ROUGE-L through rouge-score.

One place computes these three metrics so every caller gets the same
numbers and the same statement of the implementation and version that
produced them.
"""

import importlib.metadata

from rouge_score import rouge_scorer

ROUGE_METRICS: frozenset[str] = frozenset({"rouge1", "rouge2", "rougeL"})

_IMPLEMENTATION = "rouge-score"
_VERSION = importlib.metadata.version("rouge-score")


def score_rouge(
    metric: str, hypotheses: list[str], references: list[list[str]]
) -> tuple[float, str]:
    """Scores a corpus on one ROUGE metric.

    `references[i]` is the list of references for `hypotheses[i]`. Each
    hypothesis is scored against every one of its references, and the
    highest-scoring reference for that hypothesis is kept; the corpus
    score is the mean of those per-hypothesis best scores. Returns the
    corpus score and the name and version of the implementation that
    produced it. Raises ValueError, naming the metric, when it is not one
    this family computes.
    """
    if metric not in ROUGE_METRICS:
        raise ValueError(f"ROUGE does not implement metric '{metric}'")

    scorer = rouge_scorer.RougeScorer([metric], use_stemmer=True)

    best_scores = []
    for hypothesis, refs in zip(hypotheses, references):
        per_reference = [
            scorer.score(reference, hypothesis)[metric].fmeasure for reference in refs
        ]
        best_scores.append(max(per_reference))

    corpus_score = sum(best_scores) / len(best_scores) * 100
    provenance = f"{_IMPLEMENTATION} {_VERSION}"
    return corpus_score, provenance
