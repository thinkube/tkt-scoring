# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402


# WHY (INVARIANT): a query listing no relevant ids is refused naming the
# query (its position), never scored as zero.
def test_query_without_relevant_ids_is_refused_naming_the_query():
    res = TestClient(app).post(
        "/api/v1/retrieval",
        json={
            "queries": [
                {"retrieved": ["a"], "relevant": [{"id": "a"}]},
                {"retrieved": ["b"], "relevant": []},
                {"retrieved": ["c"], "relevant": [{"id": "c"}]},
            ],
            "k": [1],
        },
    )
    assert 400 <= res.status_code < 500
    text = res.text.lower()
    assert "relevant" in text
    assert "query" in text
    # position of the offender: 0-based 1 or 1-based 2
    assert "1" in text or "2" in text
    body = res.json()
    for key in ("recall_at_k", "precision_at_k", "ndcg_at_k", "mrr"):
        assert key not in body
