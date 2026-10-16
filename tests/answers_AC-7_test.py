# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.answers import NORMALISATION
from app.main import app


# INVARIANT: the answer states the normalisation applied -- case,
# punctuation, articles, whitespace -- so a reader of the response alone
# knows what was compared, without reading the module source.
def test_answers_route_states_the_normalisation_applied():
    payload = {"items": [{"prediction": "Paris", "answers": ["Paris"]}]}
    res = TestClient(app).post("/api/v1/answers", json=payload)
    assert res.status_code == 200
    assert res.json()["normalisation"] == NORMALISATION
