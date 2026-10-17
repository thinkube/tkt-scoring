# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401


# WHY (INVARIANT): /health stays open - 200 {"status": "ok"} with no token, and
# Control is never asked.
def test_health_is_open_and_control_is_not_asked():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    calls = []

    def seen(req):
        calls.append(req)
        return httpx.Response(200)

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(seen)
    )
    with TestClient(app) as client:
        res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    assert calls == []
