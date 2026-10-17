# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    return app


# WHY (INVARIANT): a caller with no token is told how to authenticate: 401, a
# WWW-Authenticate: Bearer challenge, and a detail saying to send a Thinkube
# token as Authorization: Bearer <token>.
def test_missing_token_gets_challenge_and_instruction():
    with TestClient(_load()) as client:
        res = client.post("/api/v1/text", json={})
    assert res.status_code == 401
    assert res.headers["www-authenticate"] == "Bearer"
    detail = str(res.json()["detail"])
    assert "Authorization: Bearer <token>" in detail
    assert "Thinkube" in detail
