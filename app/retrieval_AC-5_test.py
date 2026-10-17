# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): every cut-off asked for is answered, and none that was not asked.
def test_exactly_the_cutoffs_asked_for_are_answered():
    out = score_retrieval([(["a", "b", "c"], {"a": 1.0})], [1, 3])
    for key in ("recall_at_k", "precision_at_k", "ndcg_at_k"):
        assert set(out[key]) == {1, 3}
