# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401

GOOD = {
    "hypotheses": ["the cat sat on the mat"],
    "references": [["the cat sat on the mat"]],
    "metrics": ["bleu", "rouge1"],
}


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    return app


# WHY (INVARIANT): once Control accepts the token, a scoring route answers as
# it does without authentication: 200 with its scores for a good body, and its
# own refusal (not 401/503) for a bad body.
def test_accepted_token_leaves_scoring_unchanged():
    headers = {"Authorization": "Bearer good"}
    with TestClient(_load()) as client:
        ok = client.post("/api/v1/text", json=GOOD, headers=headers)
        assert ok.status_code == 200
        assert set(ok.json()["metrics"]) == {"bleu", "rouge1"}

        bad = client.post(
            "/api/v1/text", json={**GOOD, "metrics": ["bogus"]}, headers=headers
        )
        assert bad.status_code in (400, 422)
        assert "bogus" in str(bad.json()["detail"])
