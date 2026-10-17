# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
from fastapi.testclient import TestClient

import app.auth  # noqa: F401
import app.main  # noqa: F401


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    # Control stands in as a double that accepts every token.
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    return app


# WHY (INVARIANT): /api/v1/compare refuses systems with different numbers of
# outputs with 422, and the message gives both counts.
def test_compare_refuses_different_output_counts_with_both_counts():
    body = {
        "metric": "bleu",
        "samples": 5,
        "seed": 1,
        "hypotheses_a": ["a", "b", "c"],
        "hypotheses_b": ["a", "b", "c", "d", "e", "f", "g"],
        "references": [["a"], ["b"], ["c"]],
    }
    with TestClient(_load()) as client:
        res = client.post(
            "/api/v1/compare",
            json=body,
            headers={"Authorization": "Bearer good"},
        )
    assert res.status_code == 422
    text = str(res.json())
    assert "3" in text and "7" in text
