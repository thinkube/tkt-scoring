# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401
import app.main  # noqa: F401


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    # Control stand-in: accepts every token (implements get(), the one call
    # the production path makes, through a real httpx.Client).
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    return app


# WHY (INVARIANT): /api/v1/text refuses empty hypotheses with 422 and a
# message naming hypotheses.
def test_text_refuses_empty_hypotheses():
    with TestClient(_load()) as client:
        res = client.post(
            "/api/v1/text",
            json={"hypotheses": [], "references": [], "metrics": ["bleu"]},
            headers={"Authorization": "Bearer good-token"},
        )
    assert res.status_code == 422
    assert "hypotheses" in json.dumps(res.json())
