# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
import pytest
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401

GOOD = {
    "hypotheses": ["the cat sat on the mat"],
    "references": [["the cat sat on the mat"]],
    "metrics": ["bleu"],
}


def _unreachable(req):
    raise httpx.ConnectError("control is down", request=req)


# WHY (INVARIANT): when Control cannot be reached or fails with a server error,
# the answer is 503 saying the token could not be checked - never 200, never
# 401 - and nothing is scored.
@pytest.mark.parametrize(
    "handler",
    [_unreachable, lambda req: httpx.Response(500), lambda req: httpx.Response(503)],
)
def test_control_failure_is_503_and_nothing_scored(handler):
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(handler)
    )
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/text", json=GOOD, headers={"Authorization": "Bearer t"}
        )
    assert res.status_code == 503
    detail = str(res.json()["detail"]).lower()
    assert "token" in detail and "check" in detail
    assert "metrics" not in res.json()
