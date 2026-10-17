# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): accuracy is the share of positions where predicted equals
# true, and each label's precision, recall and F1 treat that label as the
# positive class and every other label as the negative class.
def test_accuracy_and_per_label_precision_recall_f1_follow_the_definitions():
    result = score_classification(["a", "a", "b", "c"], ["a", "b", "b", "b"])

    assert result["accuracy"] == pytest.approx(0.5)
    per = result["per_label"]
    assert per["a"]["precision"] == pytest.approx(0.5)
    assert per["a"]["recall"] == pytest.approx(1.0)
    assert per["a"]["f1"] == pytest.approx(2 / 3)
    assert per["b"]["precision"] == pytest.approx(1.0)
    assert per["b"]["recall"] == pytest.approx(1 / 3)
    assert per["b"]["f1"] == pytest.approx(0.5)
    assert per["c"]["precision"] == pytest.approx(0.0)
    assert per["c"]["recall"] == pytest.approx(0.0)
    assert per["c"]["f1"] == pytest.approx(0.0)
