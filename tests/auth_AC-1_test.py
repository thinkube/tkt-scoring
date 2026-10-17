# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401

OPEN = {"/health", "/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}


def _load(handler):
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    calls = []

    def seen(req):
        calls.append(req)
        return handler(req)

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(seen)
    )
    return app, calls


# WHY (INVARIANT): every route except /health and the documentation refuses a
# request with no Authorization header with 401, and scores nothing.
def test_every_protected_route_answers_401_without_a_token():
    app, calls = _load(lambda req: httpx.Response(200))
    routes = [
        r for r in app.routes if isinstance(r, APIRoute) and r.path not in OPEN
    ]
    protected = [r for r in routes if r.path != "/health"]
    assert len(protected) >= 5
    with TestClient(app) as client:
        for route in protected:
            for method in route.methods:
                res = client.request(method, route.path, json={})
                assert res.status_code == 401, (method, route.path)
                body = res.json()
                assert "metrics" not in body and "exact_match" not in body
    assert calls == []
