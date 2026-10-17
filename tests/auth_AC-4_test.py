# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401


# WHY (INVARIANT): with a bearer token the service asks Control, at the
# configured address, and forwards the caller's own Authorization header
# unchanged.
def test_token_is_checked_with_control_with_callers_header():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test:8123/"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    calls = []

    def seen(req):
        calls.append(req)
        return httpx.Response(200, json={})

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(seen)
    )
    with TestClient(app) as client:
        client.post(
            "/api/v1/text", json={}, headers={"Authorization": "Bearer tk-abc.123"}
        )
    assert len(calls) == 1
    assert calls[0].url.host == "control.test"
    assert calls[0].url.port == 8123
    assert calls[0].headers["authorization"] == "Bearer tk-abc.123"
