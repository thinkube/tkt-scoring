# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): MRR is the mean of 1/rank of the first relevant id, and a
# query with no relevant id in its list contributes zero.
def test_mrr_is_mean_reciprocal_rank_and_missing_contributes_zero():
    queries = [
        (["x", "y", "a"], {"a": 1.0}),
        (["z"], {"nope": 1.0}),
    ]
    out = score_retrieval(queries, [1])
    assert abs(out["mrr"] - (1 / 3) / 2) < 1e-9
