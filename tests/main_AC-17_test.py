# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401
import app.main  # noqa: F401

QUERY = {"retrieved": ["d1", "d2"], "relevant": [{"id": "d1"}]}
TOKEN = {"Authorization": "Bearer good-token"}


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    # Stand-in for Control: it accepts the token (the auth seam's get()).
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    return app


def _names_cutoff(body) -> bool:
    text = json.dumps(body).lower()
    return "cut-off" in text or '"k"' in text


# WHY (INVARIANT): /api/v1/retrieval refuses a cut-off that is not a positive
# whole number with 422 and a message naming it.
def test_retrieval_refuses_bad_cutoff_with_422_naming_it():
    with TestClient(_load()) as client:
        for bad in ([0], [-1], [1, 0], [2.5], ["ten"], [1, -3]):
            res = client.post(
                "/api/v1/retrieval",
                json={"queries": [QUERY], "k": bad},
                headers=TOKEN,
            )
            assert res.status_code == 422, (bad, res.status_code, res.text)
            assert _names_cutoff(res.json()), (bad, res.text)
