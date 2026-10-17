# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app, score_classification_route

BEARER = {"Authorization": "Bearer good-token"}

CASES = [
    ({"true_labels": ["a"]}, "predicted"),
    ({"predicted": ["a"]}, "true_labels"),
    ({"predicted": [], "true_labels": ["a"]}, "predicted"),
    ({"predicted": ["a"], "true_labels": []}, "true_labels"),
]


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


# WHY (INVARIANT): the /api/v1/classification route is served by
# score_classification_route, the function whose refusals this file judges.
def test_classification_route_is_served_by_score_classification_route():
    assert any(
        getattr(r, "path", None) == "/api/v1/classification"
        and r.endpoint is score_classification_route
        for r in app.routes
    )


# WHY (INVARIANT): /api/v1/classification refuses a missing or empty
# predicted or true_labels with 422 and a message naming the field.
def test_classification_refuses_missing_or_empty_field_naming_it(client):
    for body, field in CASES:
        res = client.post("/api/v1/classification", json=body, headers=BEARER)
        assert res.status_code == 422, body
        assert field in json.dumps(res.json()), body
