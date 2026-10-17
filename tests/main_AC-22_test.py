# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json

import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app

GOOD = {
    "metric": "bleu",
    "hypotheses_a": ["a b", "c d"],
    "hypotheses_b": ["a x", "c y"],
    "references": [["a b"], ["c d"]],
    "samples": 5,
}


class _Response:
    status_code = 200
    is_success = True


class _ControlDouble:
    """Stands in for the httpx client that asks Control to verify a token."""

    def get(self, url, headers=None):
        return _Response()

    def close(self):
        pass


def _fake_client():
    yield _ControlDouble()


@pytest.fixture
def client():
    had_url = hasattr(app.state, "control_url")
    old_url = getattr(app.state, "control_url", None)
    app.state.control_url = "http://control.invalid"
    app.dependency_overrides[control_client] = _fake_client
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(control_client, None)
        if had_url:
            app.state.control_url = old_url
        else:
            del app.state.control_url


# WHY (INVARIANT): /api/v1/compare refuses a seed that is not a whole number
# (1.5, "seven", true) with 422 and a message naming seed.
@pytest.mark.parametrize("bad", [1.5, "seven", True])
def test_compare_route_refuses_non_whole_seed_naming_it(client, bad):
    res = client.post(
        "/api/v1/compare",
        json=dict(GOOD, seed=bad),
        headers={"Authorization": "Bearer good-token"},
    )
    assert res.status_code == 422, (bad, res.status_code, res.text)
    assert "seed" in json.dumps(res.json()), bad
