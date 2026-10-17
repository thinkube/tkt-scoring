# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): a cut-off that is not a positive whole number is refused,
# naming it, and no number is produced.
@pytest.mark.parametrize("bad", [0, -2, 2.5])
def test_non_positive_whole_cutoff_is_refused_and_named(bad):
    with pytest.raises(ValueError) as err:
        score_retrieval([(["a"], {"a": 1.0})], [1, bad])
    assert str(bad) in str(err.value)
