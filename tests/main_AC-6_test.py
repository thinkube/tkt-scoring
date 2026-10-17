# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app


def _client_accepting_token():
    # Control stand-in: accepts any token. Implements get() through a real
    # httpx.Client on a mock transport, so close() etc. also exist.
    return httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )


def _post(payload):
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    app.dependency_overrides[control_client] = _client_accepting_token
    try:
        # The context manager runs the lifespan, which sets control_url.
        with TestClient(app) as client:
            return client.post(
                "/api/v1/text",
                json=payload,
                headers={"Authorization": "Bearer good-token"},
            )
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): /api/v1/text refuses a request missing metrics with 422
# and a refusal naming metrics.
def test_text_refuses_missing_metrics_field():
    res = _post({"hypotheses": ["a"], "references": [["a"]]})
    assert res.status_code == 422
    assert "metrics" in json.dumps(res.json())
