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


# WHY (INVARIANT): a token Control rejects (401 or 403) is refused with 401 and
# nothing is scored.
@pytest.mark.parametrize("status", [401, 403])
def test_rejected_token_is_401_and_nothing_scored(status):
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(status))
    )
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/text", json=GOOD, headers={"Authorization": "Bearer nope"}
        )
    assert res.status_code == 401
    assert "metrics" not in res.json()
