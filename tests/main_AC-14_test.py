# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
from fastapi.testclient import TestClient

os.environ.setdefault("THINKUBE_CONTROL_URL", "http://control.test")

from app.auth import control_client  # noqa: E402
from app.main import app  # noqa: E402

GOOD = {
    "metric": "bleu",
    "hypotheses_a": ["a b", "c d"],
    "hypotheses_b": ["a x", "c y"],
    "references": [["a b"], ["c d"]],
    "seed": 1,
}

HEADERS = {"Authorization": "Bearer good-token"}


def _control_accepts(request):
    # Stand-in for Thinkube Control's token verification: accepts the token.
    return httpx.Response(200, json={"valid": True})


# WHY (INVARIANT): /api/v1/compare refuses a samples count that is not a
# positive whole number with 422 and a message naming samples.
def test_compare_refuses_bad_samples_naming_it():
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(_control_accepts)
    )
    try:
        with TestClient(app) as client:
            for bad in (0, -3, 2.5, "ten", True):
                res = client.post(
                    "/api/v1/compare",
                    json=dict(GOOD, samples=bad),
                    headers=HEADERS,
                )
                assert res.status_code == 422, (bad, res.status_code, res.text)
                assert "samples" in json.dumps(res.json()), bad
    finally:
        app.dependency_overrides.pop(control_client, None)
