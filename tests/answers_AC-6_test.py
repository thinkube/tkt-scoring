# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.main import app


# INVARIANT: posting a set of predictions with their accepted answers to
# /api/v1/answers answers with that set's exact match, token F1 and the
# number of predictions scored.
def test_answers_route_returns_exact_match_token_f1_and_count():
    payload = {
        "items": [
            {"prediction": "eiffel tower", "answers": ["Eiffel Tower"]},
            {"prediction": "banana", "answers": ["Eiffel Tower"]},
        ]
    }
    res = TestClient(app).post("/api/v1/answers", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["exact_match"] == 50
    assert body["count"] == 2
    assert "token_f1" in body
