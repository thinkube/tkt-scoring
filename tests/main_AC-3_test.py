# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app, score_text

BEARER = {"Authorization": "Bearer good-token"}


@pytest.fixture
def client(monkeypatch):
    """A client past the auth gate: Control (the seam) accepts the token."""
    monkeypatch.setitem(os.environ, "THINKUBE_CONTROL_URL", "http://control.test")

    def accept(request):
        return httpx.Response(200, json={})

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(accept)
    )
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): the /api/v1/text route is served by score_text, the
# function whose refusals this file judges.
def test_text_route_is_served_by_score_text():
    assert any(
        getattr(r, "path", None) == "/api/v1/text" and r.endpoint is score_text
        for r in app.routes
    )


# WHY (INVARIANT): /api/v1/text refuses an empty metrics list with 422 naming
# metrics, never answering an empty set of scores.
def test_text_refuses_empty_metrics_list(client):
    res = client.post(
        "/api/v1/text",
        json={"hypotheses": ["a"], "references": [["a"]], "metrics": []},
        headers=BEARER,
    )
    assert res.status_code == 422
    assert "metrics" in json.dumps(res.json())
    body = res.json()
    assert not (isinstance(body, dict) and body.get("metrics") == {})
