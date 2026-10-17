# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

QUERY = {"retrieved": ["a"], "relevant": [{"id": "a"}]}
NUMBERS = ("recall_at_k", "precision_at_k", "ndcg_at_k", "mrr")


# WHY (INVARIANT): a cut-off that is not a positive whole number is refused
# with a message naming it, and no number comes back.
def test_route_refuses_bad_cutoff_and_names_it():
    client = TestClient(app)
    for bad in (0, -7, 2.5):
        res = client.post("/api/v1/retrieval", json={"queries": [QUERY], "k": [1, bad]})
        assert 400 <= res.status_code < 500
        assert str(bad) in res.text
        assert not any(key in res.json() for key in NUMBERS)


# WHY (INVARIANT): a ranked list repeating an id is refused with a message
# naming the repeated id, and no number comes back.
def test_route_refuses_repeated_ranked_id_and_names_it():
    res = TestClient(app).post(
        "/api/v1/retrieval",
        json={
            "queries": [{"retrieved": ["a", "twice-id", "twice-id"], "relevant": [{"id": "a"}]}],
            "k": [2],
        },
    )
    assert 400 <= res.status_code < 500
    assert "twice-id" in res.text
    assert not any(key in res.json() for key in NUMBERS)
