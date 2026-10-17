# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): micro averages come from pooled counts, so with one
# predicted and one true label per position they all equal accuracy.
def test_micro_precision_recall_f1_and_accuracy_are_the_same_number():
    result = score_classification(["a", "a", "b", "c"], ["a", "b", "b", "b"])

    micro = result["micro"]
    assert result["accuracy"] == pytest.approx(0.5)
    assert micro["precision"] == pytest.approx(result["accuracy"])
    assert micro["recall"] == pytest.approx(result["accuracy"])
    assert micro["f1"] == pytest.approx(result["accuracy"])
