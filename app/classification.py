# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""Classification numbers: one place computes them, so every caller gets
the same accuracy, per-label scores, averages and confusion matrix."""

from collections import Counter
from collections.abc import Sequence

DEFINITIONS = (
    "Accuracy is the share of positions where the predicted label equals the "
    "true label. "
    "Per-label precision is TP / (TP + FP), recall is TP / (TP + FN), and F1 "
    "is their harmonic mean, treating that label as the positive class and "
    "every other label as the negative class; a value whose denominator is "
    "zero is 0.0. "
    "Macro average is the unweighted mean of the per-label values. "
    "Micro average is computed from the pooled true/false positive and false "
    "negative counts across all labels. "
    "The confusion matrix has one row per true label and one column per "
    "predicted label, in the order given by labels."
)


def _divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return _divide(2 * precision * recall, precision + recall)


def score_classification(
    predicted: Sequence[str], true_labels: Sequence[str]
) -> dict:
    """Scores predicted labels against true labels, position by position."""
    if len(predicted) != len(true_labels):
        raise ValueError(
            f"{len(predicted)} predicted labels but {len(true_labels)} true "
            "labels: the two lists must be the same length"
        )

    labels = sorted(set(predicted) | set(true_labels))
    index = {label: i for i, label in enumerate(labels)}
    pairs = Counter(zip(true_labels, predicted))

    matrix = [[0] * len(labels) for _ in labels]
    for (true, pred), count in pairs.items():
        matrix[index[true]][index[pred]] = count

    total = len(predicted)
    correct = sum(matrix[i][i] for i in range(len(labels)))

    per_label: dict[str, dict[str, float]] = {}
    for i, label in enumerate(labels):
        tp = matrix[i][i]
        fp = sum(row[i] for row in matrix) - tp
        fn = sum(matrix[i]) - tp
        precision = _divide(tp, tp + fp)
        recall = _divide(tp, tp + fn)
        per_label[label] = {
            "precision": precision,
            "recall": recall,
            "f1": _f1(precision, recall),
        }

    macro = {
        key: _divide(sum(v[key] for v in per_label.values()), len(per_label))
        for key in ("precision", "recall", "f1")
    }

    # Pooled over all labels: every wrong position is one FP and one FN.
    wrong = total - correct
    micro_precision = _divide(correct, correct + wrong)
    micro_recall = _divide(correct, correct + wrong)
    micro = {
        "precision": micro_precision,
        "recall": micro_recall,
        "f1": _f1(micro_precision, micro_recall),
    }

    return {
        "accuracy": _divide(correct, total),
        "per_label": per_label,
        "macro": macro,
        "micro": micro,
        "labels": labels,
        "confusion_matrix": matrix,
        "statement": DEFINITIONS,
    }
