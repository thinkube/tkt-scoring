# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
import pytest
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
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
    return app, calls


# WHY (INVARIANT): an Authorization header that is not a bearer token (another
# scheme, or Bearer with nothing after it) is refused with 401 without asking
# Control.
@pytest.mark.parametrize("header", ["Basic dXNlcjpwYXNz", "Bearer", "Bearer ", "Token abc"])
def test_non_bearer_header_is_401_and_control_is_not_asked(header):
    app, calls = _load()
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/text", json={}, headers={"Authorization": header}
        )
    assert res.status_code == 401
    assert calls == []
