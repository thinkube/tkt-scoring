# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""Paired bootstrap comparison of two systems on one metric.

One place runs the comparison so every caller gets the same numbers. Each
score comes from the metric's own family module.
"""

import random

from app.answers import NORMALISATION, score_answers
from app.rouge_metrics import ROUGE_METRICS, score_rouge
from app.sacrebleu_metrics import SACREBLEU_METRICS, score_sacrebleu

ANSWER_METRICS: frozenset[str] = frozenset({"exact_match", "token_f1"})

ACCEPTED_METRICS: tuple[str, ...] = (
    "bleu",
    "chrf",
    "chrf++",
    "ter",
    "rouge1",
    "rouge2",
    "rougeL",
    "exact_match",
    "token_f1",
)

METHOD = (
    "Paired bootstrap. Both systems are scored on the same resampled items "
    "in every sample (paired resampling): each sample draws the items with "
    "replacement, from the seed, and the same drawn items, with their "
    "references, score both systems. Each system's score is its score on "
    "the full set, on the metric's own scale; the difference is the first "
    "system's score minus the second's. The intervals are 95% percentile "
    "intervals, with bounds at the 2.5th and 97.5th percentiles of the "
    "samples. The first system 'beats' the second in a sample only when its "
    "score is strictly higher, or strictly lower for ter, where lower is "
    "better; ties are not counted as beats. The share is the samples in "
    "which it beats the second divided by the number of samples. The result "
    "is significant only when the difference interval excludes zero."
)


def _score(metric: str, hyps: list[str], refs: list[list[str]]) -> tuple[float, str]:
    if metric in SACREBLEU_METRICS:
        return score_sacrebleu(metric, hyps, refs)
    if metric in ROUGE_METRICS:
        return score_rouge(metric, hyps, refs)
    return float(score_answers(list(zip(hyps, refs)))[metric]), NORMALISATION


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q / 100
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def _interval(score: float, values: list[float]) -> dict:
    return {
        "score": float(score),
        "lower": float(_percentile(values, 2.5)),
        "upper": float(_percentile(values, 97.5)),
    }


def compare_systems(
    metric: str,
    hypotheses_a: list[str],
    hypotheses_b: list[str],
    references: list[list[str]],
    samples: int,
    seed: int,
) -> dict:
    """Compares two systems on one metric by paired bootstrap.

    Raises ValueError, naming the offender, before any number is produced.
    """
    if metric not in ACCEPTED_METRICS:
        raise ValueError(
            f"unknown metric '{metric}': send one of {', '.join(ACCEPTED_METRICS)}"
        )
    if not hypotheses_a or not hypotheses_b:
        raise ValueError(
            "outputs must not be empty: send at least one output per system"
        )
    if len(hypotheses_a) != len(hypotheses_b):
        raise ValueError(
            f"the two systems must have the same number of outputs "
            f"(first has {len(hypotheses_a)}, second has {len(hypotheses_b)})"
        )
    if len(references) != len(hypotheses_a):
        raise ValueError(
            f"the number of reference groups ({len(references)}) must match "
            f"the number of outputs ({len(hypotheses_a)})"
        )
    for position, group in enumerate(references):
        if not group:
            raise ValueError(
                f"reference group at position {position} (counting from 0) "
                "is empty: send at least one reference per item"
            )
    if isinstance(samples, bool) or not isinstance(samples, int) or samples < 1:
        raise ValueError(
            f"samples must be a positive whole number, got {samples!r}"
        )

    score_a, provenance = _score(metric, hypotheses_a, references)
    score_b, _ = _score(metric, hypotheses_b, references)

    rng = random.Random(seed)
    count = len(hypotheses_a)
    lower_is_better = metric == "ter"
    scores_a: list[float] = []
    scores_b: list[float] = []
    diffs: list[float] = []
    wins = 0
    for _ in range(samples):
        indices = [rng.randrange(count) for _ in range(count)]
        refs = [references[i] for i in indices]
        a, _p = _score(metric, [hypotheses_a[i] for i in indices], refs)
        b, _p = _score(metric, [hypotheses_b[i] for i in indices], refs)
        scores_a.append(a)
        scores_b.append(b)
        diffs.append(a - b)
        if (a < b) if lower_is_better else (a > b):
            wins += 1

    difference = _interval(score_a - score_b, diffs)
    return {
        "metric": metric,
        "samples": samples,
        "seed": seed,
        "system_a": _interval(score_a, scores_a),
        "system_b": _interval(score_b, scores_b),
        "difference": difference,
        "share_a_beats_b": float(wins / samples),
        "significant": bool(difference["lower"] > 0 or difference["upper"] < 0),
        "provenance": provenance,
        "method": METHOD,
    }
