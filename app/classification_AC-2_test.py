# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): the macro average is the unweighted mean of the per-label
# values, so a rare label counts as much as a common one.
def test_macro_average_is_the_unweighted_mean_of_per_label_values():
    result = score_classification(["a", "a", "b", "c"], ["a", "b", "b", "b"])

    macro = result["macro"]
    assert macro["precision"] == pytest.approx((0.5 + 1.0 + 0.0) / 3)
    assert macro["recall"] == pytest.approx((1.0 + 1 / 3 + 0.0) / 3)
    assert macro["f1"] == pytest.approx((2 / 3 + 0.5 + 0.0) / 3)
