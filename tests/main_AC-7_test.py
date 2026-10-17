# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.main import app


@pytest.fixture
def client():
    """A client whose bearer token Control (a mock transport) accepts."""
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(control_client, None)


# WHY (INVARIANT): /api/v1/answers refuses an empty items list with 422 and
# answers no exact_match.
def test_answers_refuses_empty_items(client):
    res = client.post(
        "/api/v1/answers",
        json={"items": []},
        headers={"Authorization": "Bearer good-token"},
    )
    assert res.status_code == 422
    assert "exact_match" not in res.text
