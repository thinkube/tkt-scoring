# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.main import app


# INVARIANT: an item missing its accepted answers, or missing its
# prediction field, is refused with an error naming what is missing, and no
# numbers are returned for the set.
def test_answers_route_refuses_an_item_missing_answers_or_prediction():
    client = TestClient(app)

    missing_answers = {"items": [{"prediction": "Paris"}]}
    res = client.post("/api/v1/answers", json=missing_answers)
    assert res.status_code == 422
    assert "exact_match" not in res.json()

    missing_prediction = {"items": [{"answers": ["Paris"]}]}
    res = client.post("/api/v1/answers", json=missing_prediction)
    assert res.status_code == 422
    assert "exact_match" not in res.json()
