# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): precision@k is measured against k itself, so returning
# fewer than k ids cannot reach the top score.
def test_precision_at_k_divides_by_k_even_when_fewer_ids_returned():
    out = score_retrieval([(["a"], {"a": 1.0})], [3])
    assert abs(out["precision_at_k"][3] - 1 / 3) < 1e-9


# WHY (INVARIANT): precision@k is the mean over queries of relevant-in-first-k over k.
def test_precision_at_k_is_mean_over_queries():
    queries = [
        (["a", "b", "c", "d"], {"a": 1.0, "c": 1.0}),
        (["x", "y", "z", "w"], {"q": 1.0}),
    ]
    out = score_retrieval(queries, [2, 4])
    assert abs(out["precision_at_k"][2] - 0.25) < 1e-9
    assert abs(out["precision_at_k"][4] - 0.25) < 1e-9
