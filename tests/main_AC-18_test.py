# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app

HEADERS = {"Authorization": "Bearer good-token"}


def _post(body):
    """Posts through the real auth dependency, with Control stood in for."""
    os.environ.setdefault("THINKUBE_CONTROL_URL", "http://control.test")
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    try:
        with TestClient(app) as client:
            return client.post("/api/v1/retrieval", json=body, headers=HEADERS)
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): /api/v1/retrieval refuses a request missing k with 422 and
# a refusal naming k.
def test_retrieval_refuses_missing_k_naming_k():
    res = _post(
        {"queries": [{"retrieved": ["d1"], "relevant": [{"id": "d1"}]}]}
    )
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert any(
        isinstance(item, dict) and "k" in (item.get("loc") or [])
        for item in detail
    ), json.dumps(detail)
