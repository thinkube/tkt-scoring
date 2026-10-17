# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app

KEYS = ["bleu", "chrf", "chrf++", "ter", "rouge1", "rouge2", "rougeL",
        "exact_match", "token_f1"]


@pytest.fixture
def client(monkeypatch):
    # The lifespan refuses to start without the Control URL; Control accepts
    # every token.
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "http://control.test")
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): /api/v1/compare refuses an unknown metric with 422 and the
# message lists every accepted metric key.
def test_compare_refuses_unknown_metric_listing_accepted_keys(client):
    res = client.post(
        "/api/v1/compare",
        headers={"Authorization": "Bearer tk-test"},
        json={
            "metric": "zorblax",
            "samples": 5,
            "seed": 1,
            "hypotheses_a": ["a"],
            "hypotheses_b": ["b"],
            "references": [["a"]],
        },
    )
    assert res.status_code == 422
    text = json.dumps(res.json())
    for key in KEYS:
        assert key in text, key
