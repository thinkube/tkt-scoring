# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx
from fastapi.testclient import TestClient

os.environ.setdefault("THINKUBE_CONTROL_URL", "http://control.test")

from app.auth import control_client  # noqa: E402
from app.main import app  # noqa: E402

BASE = {"metric": "bleu", "samples": 5, "seed": 1}
HEADERS = {"Authorization": "Bearer good-token"}


def _control_accepts(request):
    # Stand-in for Control: it accepts every token.
    return httpx.Response(200, json={})


def _client():
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(_control_accepts)
    )
    return TestClient(app)


# WHY (INVARIANT): /api/v1/compare refuses empty outputs and empty reference
# groups with 422.
def test_compare_refuses_empty_outputs_and_empty_reference_groups():
    empty_outputs = dict(BASE, hypotheses_a=[], hypotheses_b=[], references=[])
    empty_group = dict(
        BASE,
        hypotheses_a=["a", "b"],
        hypotheses_b=["a", "c"],
        references=[["a"], []],
    )
    try:
        with _client() as client:
            for body in (empty_outputs, empty_group):
                res = client.post("/api/v1/compare", json=body, headers=HEADERS)
                assert res.status_code == 422, (body, res.status_code, res.text)
    finally:
        app.dependency_overrides.pop(control_client, None)
