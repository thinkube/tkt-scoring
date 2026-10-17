# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): recall@k is the mean over queries of the share of a query's
# relevant ids found among its first k ranked ids.
def test_recall_at_k_is_mean_share_of_relevant_ids_in_first_k():
    queries = [
        (["a", "b", "c", "d"], {"a": 1.0, "c": 1.0}),
        (["x", "y", "z"], {"z": 1.0}),
    ]
    out = score_retrieval(queries, [2, 4])
    # k=2: q1 1/2, q2 0 -> 0.25 ; k=4: q1 1, q2 1 -> 1.0
    assert abs(out["recall_at_k"][2] - 0.25) < 1e-9
    assert abs(out["recall_at_k"][4] - 1.0) < 1e-9
