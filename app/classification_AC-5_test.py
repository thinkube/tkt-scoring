# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): a label seen only among predictions, or only among true
# labels, still gets its own row, column and per-label numbers.
def test_labels_seen_on_only_one_side_get_row_column_and_per_label_scores():
    result = score_classification(["a", "a", "p"], ["a", "t", "a"])

    labels = result["labels"]
    assert sorted(labels) == ["a", "p", "t"]
    assert len(result["confusion_matrix"]) == 3
    assert all(len(r) == 3 for r in result["confusion_matrix"])
    for label in ("p", "t"):
        assert set(result["per_label"][label]) >= {"precision", "recall", "f1"}
    assert result["per_label"]["p"]["precision"] == pytest.approx(0.0)
    assert result["per_label"]["t"]["recall"] == pytest.approx(0.0)
    assert result["per_label"]["a"]["precision"] == pytest.approx(0.5)
    assert result["per_label"]["a"]["recall"] == pytest.approx(0.5)
