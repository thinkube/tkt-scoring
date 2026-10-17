# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): a ranked list naming the same id twice is refused, naming
# the repeated id, and no number is produced.
def test_repeated_ranked_id_is_refused_and_named():
    with pytest.raises(ValueError) as err:
        score_retrieval([(["a", "dup-id", "b", "dup-id"], {"a": 1.0})], [2])
    assert "dup-id" in str(err.value)
