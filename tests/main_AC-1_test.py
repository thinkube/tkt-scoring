# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app, score_text


@pytest.fixture
def client(monkeypatch):
    # Control accepts the token; the lifespan sets app.state.control_url.
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "http://control.test")
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
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


# WHY (INVARIANT): /api/v1/text refuses hypotheses and reference groups of
# different lengths with 422 giving both counts, and answers no metrics.
def test_text_refuses_mismatched_lengths_with_both_counts(client):
    res = client.post(
        "/api/v1/text",
        headers={"Authorization": "Bearer good-token"},
        json={
            "hypotheses": ["a", "b"],
            "references": [["a"], ["b"], ["c"], ["d"], ["e"]],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code == 422
    text = json.dumps(res.json())
    assert "2" in text and "5" in text
    assert "metrics" not in res.json()
