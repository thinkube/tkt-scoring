# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402


# WHY (INVARIANT): a request with no queries is refused with a message naming
# what to fix, and no number comes back.
def test_no_queries_is_refused_naming_queries():
    res = TestClient(app).post("/api/v1/retrieval", json={"queries": [], "k": [1]})
    assert 400 <= res.status_code < 500
    assert "queries" in res.text
    body = res.json()
    for key in ("recall_at_k", "precision_at_k", "ndcg_at_k", "mrr"):
        assert key not in body
