# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.main import app


# INVARIANT: an empty set of predictions is refused rather than answered
# with a made-up zero -- there is no such thing as the exact match of
# nothing.
def test_answers_route_refuses_an_empty_set_of_predictions():
    res = TestClient(app).post("/api/v1/answers", json={"items": []})
    assert res.status_code >= 400
    assert "exact_match" not in res.json()
