# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): lists of different lengths are refused, the refusal names
# both counts, and no numbers are produced.
def test_mismatched_lengths_are_refused_naming_both_counts():
    with pytest.raises(ValueError) as err:
        score_classification(["a", "b", "a", "b", "a"], ["a", "b"])

    message = str(err.value)
    assert "5" in message
    assert "2" in message
