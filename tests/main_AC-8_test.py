# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os
import sys

import httpx
from fastapi.testclient import TestClient


def _load():
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    # Control stand-in: accepts the token. Client is a real httpx.Client over
    # a mock transport, so every method the production path calls exists.
    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    return app


def _post(items):
    with TestClient(_load()) as client:
        return client.post(
            "/api/v1/answers",
            json={"items": items},
            headers={"Authorization": "Bearer good-token"},
        )


# WHY (INVARIANT): /api/v1/answers refuses an item with no accepted answers
# with 422 naming that item's position counting from 0, and answers no
# exact_match or token_f1.
def test_answers_refuses_item_with_empty_answers_naming_position():
    res = _post(
        [
            {"prediction": "a", "answers": ["a"]},
            {"prediction": "b", "answers": ["b"]},
            {"prediction": "c", "answers": []},
            {"prediction": "d", "answers": ["d"]},
        ]
    )
    assert res.status_code == 422
    body = res.json()
    assert "2" in json.dumps(body)
    assert "exact_match" not in json.dumps(body)
    assert "token_f1" not in json.dumps(body)


# WHY (INVARIANT): position counts from 0, so an empty first item is item 0.
def test_answers_refuses_empty_first_item_as_position_zero():
    res = _post(
        [
            {"prediction": "a", "answers": []},
            {"prediction": "b", "answers": ["b"]},
        ]
    )
    assert res.status_code == 422
    assert "0" in json.dumps(res.json())
    assert "exact_match" not in res.json()
    assert "token_f1" not in res.json()
