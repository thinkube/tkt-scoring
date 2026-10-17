# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402


# WHY (INVARIANT): posting queries and cut-offs answers recall/precision/nDCG
# per cut-off, MRR for the set, and the number of queries scored.
def test_retrieval_route_answers_the_four_numbers_and_count():
    res = TestClient(app).post(
        "/api/v1/retrieval",
        json={
            "queries": [
                {
                    "retrieved": ["a", "b", "c", "d"],
                    "relevant": [{"id": "a"}, {"id": "c", "grade": 2}],
                },
                {"retrieved": ["x", "y"], "relevant": [{"id": "y"}]},
            ],
            "k": [2, 4],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2
    assert set(body["recall_at_k"]) == {"2", "4"}
    assert set(body["precision_at_k"]) == {"2", "4"}
    assert set(body["ndcg_at_k"]) == {"2", "4"}
    # k=2: q1 recall 1/2, q2 recall 1 -> 0.75
    assert abs(body["recall_at_k"]["2"] - 0.75) < 1e-9
    # k=2 precision: q1 1/2, q2 1/2 -> 0.5
    assert abs(body["precision_at_k"]["2"] - 0.5) < 1e-9
    # mrr: q1 1, q2 1/2 -> 0.75
    assert abs(body["mrr"] - 0.75) < 1e-9
    assert isinstance(body["definitions"], str)
