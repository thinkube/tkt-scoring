# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: GET /health still answers {"status": "ok"} at the same path,
# unchanged by adding the answers route.
from fastapi.testclient import TestClient

from app.main import app


def test_health_still_answers_ok():
    res = TestClient(app).get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
