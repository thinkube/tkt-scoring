# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.answers import score_answers
from app.main import app


# INVARIANT: the numbers the route answers for a set are exactly the
# numbers the scoring module gives for that same set; the route adds no
# arithmetic of its own, only the normalisation statement and count.
def test_answers_route_numbers_match_the_scoring_module_directly():
    items = [
        ("eiffel tower", ["Eiffel Tower", "The Eiffel Tower"]),
        ("the great wall", ["Great Wall of China"]),
    ]
    expected = score_answers(items)

    payload = {
        "items": [
            {"prediction": p, "answers": list(a)} for p, a in items
        ]
    }
    res = TestClient(app).post("/api/v1/answers", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["exact_match"] == expected["exact_match"]
    assert body["token_f1"] == expected["token_f1"]
