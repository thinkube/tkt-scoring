# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import math
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402
from app.retrieval import score_retrieval  # noqa: E402


# WHY (INVARIANT): nDCG@k uses grades as gains with a log2 rank discount,
# divided by the ideal ordering; grade order scores the top value.
def test_ndcg_is_one_in_grade_order_and_less_when_swapped():
    good = score_retrieval([(["a", "b"], {"a": 3.0, "b": 1.0})], [2])
    assert abs(good["ndcg_at_k"][2] - 1.0) < 1e-9

    swapped = score_retrieval([(["b", "a"], {"a": 3.0, "b": 1.0})], [2])
    dcg = 1 + 3 / math.log2(3)
    ideal = 3 + 1 / math.log2(3)
    assert abs(swapped["ndcg_at_k"][2] - dcg / ideal) < 1e-9

    cut = score_retrieval([(["b", "a"], {"a": 3.0, "b": 1.0})], [1])
    assert abs(cut["ndcg_at_k"][1] - 1 / 3) < 1e-9


# WHY (INVARIANT): a relevant id posted without a grade counts as grade one.
def test_ungraded_relevant_id_counts_as_grade_one():
    client = TestClient(app)

    def ndcg(relevant):
        res = client.post(
            "/api/v1/retrieval",
            json={
                "queries": [{"retrieved": ["x", "a"], "relevant": relevant}],
                "k": [2],
            },
        )
        assert res.status_code == 200
        return res.json()["ndcg_at_k"]["2"]

    ungraded = ndcg([{"id": "a"}])
    assert abs(ungraded - ndcg([{"id": "a", "grade": 1}])) < 1e-9
    assert abs(ungraded - (1 / math.log2(3))) < 1e-9
