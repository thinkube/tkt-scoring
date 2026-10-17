# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("THINKUBE_CONTROL_URL", "http://control.test")

from app.auth import control_client  # noqa: E402
from app.main import app  # noqa: E402

GOOD = {
    "metric": "bleu",
    "hypotheses_a": ["a b", "c d"],
    "hypotheses_b": ["a x", "c y"],
    "references": [["a b"], ["c d"]],
    "samples": 5,
    "seed": 1,
}

AUTHORIZED = {"Authorization": "Bearer good-token"}


@pytest.fixture
def client():
    # Control is stood in for by a transport that accepts every token; the
    # double serves the one method production calls on it (get).
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): /api/v1/compare refuses a request missing metric, samples
# or seed with 422 naming the missing field; no scores, intervals or seed are
# answered, so no seed of 0 is ever filled in.
@pytest.mark.parametrize("field", ["metric", "samples", "seed"])
def test_compare_refuses_missing_field_naming_it(client, field):
    body = {k: v for k, v in GOOD.items() if k != field}
    res = client.post("/api/v1/compare", json=body, headers=AUTHORIZED)
    assert res.status_code == 422, res.text
    payload = res.json()
    assert field in json.dumps(payload)
    if isinstance(payload, dict):
        for key in (
            "system_a",
            "system_b",
            "difference",
            "seed",
            "lower",
            "upper",
            "score",
        ):
            assert key not in payload, key
