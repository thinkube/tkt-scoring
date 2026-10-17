# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""Retrieval quality: recall@k, precision@k, MRR and nDCG@k.

One place computes them, so every caller gets the same numbers.
"""

import math
from collections.abc import Mapping, Sequence

DEFINITIONS = (
    "A ranked id is relevant when it is present in the query's relevant ids; "
    "presence alone decides relevance, and a grade never changes it. "
    "Grades are numbers on a scale from 0 upward; a relevant id posted "
    "without a grade (ungraded) defaults to grade 1. "
    "recall@k is the mean over queries of the share of the query's relevant "
    "ids that appear among its first k ranked ids. "
    "precision@k is the mean over queries of the relevant ids among the "
    "first k ranked ids divided by k itself, so a query that returned fewer "
    "than k ids is not rewarded for it. "
    "MRR is the mean over queries of 1 divided by the 1-based rank of the "
    "first relevant id; a query with no relevant id in its ranked list "
    "contributes 0. "
    "nDCG@k uses the grade as the gain, discounted at 1-based rank r by "
    "1/log2(r+1); DCG@k sums gain x discount over the first k ranked ids "
    "(an id that is not relevant has gain 0) and is divided by the ideal "
    "DCG@k, the same sum over the query's relevant grades in descending "
    "order, so a query ranked in grade order scores 1; nDCG@k is the mean "
    "over queries (a query whose ideal DCG is 0 contributes 0). "
    "All four numbers are on a 0 to 1 scale."
)


def _discount(rank: int) -> float:
    return 1.0 / math.log2(rank + 1)


def score_retrieval(
    queries: Sequence[tuple[Sequence[str], Mapping[str, float]]],
    k: Sequence[int],
) -> dict:
    """Scores ranked ids against relevant ids at each cut-off in `k`.

    Raises ValueError, naming the offender, before any number is produced.
    """
    if not queries:
        raise ValueError("queries must not be empty")
    if not k:
        raise ValueError("k (the cut-offs wanted) must not be empty")

    for cutoff in k:
        if isinstance(cutoff, bool) or not isinstance(cutoff, int) or cutoff < 1:
            raise ValueError(
                f"cut-off {cutoff!s} is not a positive whole number"
            )

    for position, (ranked, relevant) in enumerate(queries):
        if not relevant:
            raise ValueError(
                f"query {position} (counting from 0) lists no relevant ids"
            )
        seen = set()
        for item in ranked:
            if item in seen:
                raise ValueError(
                    f"ranked list of query {position} (counting from 0) "
                    f"repeats the id {item}"
                )
            seen.add(item)
        for item, grade in relevant.items():
            if grade < 0:
                raise ValueError(
                    f"grade {grade!s} of relevant id {item} in query "
                    f"{position} (counting from 0) is below 0"
                )

    cutoffs = sorted(set(k))
    recall = {c: 0.0 for c in cutoffs}
    precision = {c: 0.0 for c in cutoffs}
    ndcg = {c: 0.0 for c in cutoffs}
    mrr = 0.0

    for ranked, relevant in queries:
        for rank, item in enumerate(ranked, start=1):
            if item in relevant:
                mrr += 1.0 / rank
                break
        ideal_grades = sorted(relevant.values(), reverse=True)
        for c in cutoffs:
            hits = sum(1 for item in ranked[:c] if item in relevant)
            recall[c] += hits / len(relevant)
            precision[c] += hits / c
            dcg = sum(
                relevant.get(item, 0.0) * _discount(rank)
                for rank, item in enumerate(ranked[:c], start=1)
            )
            ideal = sum(
                grade * _discount(rank)
                for rank, grade in enumerate(ideal_grades[:c], start=1)
            )
            if ideal > 0:
                ndcg[c] += dcg / ideal

    n = len(queries)
    return {
        "recall_at_k": {c: v / n for c, v in recall.items()},
        "precision_at_k": {c: v / n for c, v in precision.items()},
        "ndcg_at_k": {c: v / n for c, v in ndcg.items()},
        "mrr": mrr / n,
        "count": n,
    }
