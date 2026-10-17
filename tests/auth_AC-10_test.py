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
    "metrics": ["bleu"],
}


# WHY (INVARIANT): nothing is kept between requests - the same token sent twice
# is checked with Control twice (no cache).
def test_same_token_is_checked_with_control_each_time():
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
    headers = {"Authorization": "Bearer same"}
    with TestClient(app) as client:
        assert client.post("/api/v1/text", json=GOOD, headers=headers).status_code == 200
        assert client.post("/api/v1/text", json=GOOD, headers=headers).status_code == 200
    assert len(calls) == 2
