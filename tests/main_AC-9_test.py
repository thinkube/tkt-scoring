# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app


def _control(request):
    # Stand-in for Thinkube Control: accepts every token.
    return httpx.Response(200, json={"valid": True})


def _client():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(_control)
    )
    # Entering the context runs the lifespan, which sets app.state.control_url.
    return TestClient(app)


# WHY (INVARIANT): /api/v1/classification refuses predicted and true_labels
# of different lengths with 422, and the message gives both counts.
def test_classification_refuses_mismatched_lengths_with_both_counts():
    try:
        with _client() as client:
            res = client.post(
                "/api/v1/classification",
                headers={"Authorization": "Bearer good-token"},
                json={
                    "predicted": ["a", "b", "a"],
                    "true_labels": ["a", "b", "a", "b", "a", "b", "a"],
                },
            )
    finally:
        app.dependency_overrides.pop(control_client, None)
    assert res.status_code == 422
    text = json.dumps(res.json())
    assert "3" in text and "7" in text
