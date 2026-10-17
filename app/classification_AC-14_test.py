# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): adding the classification route must not change the health
# check, the text route or the answers route.
def test_health_text_and_answers_still_answer_as_before():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    answers = client.post(
        "/api/v1/answers",
        json={"items": [{"prediction": "The Eiffel Tower", "answers": ["eiffel tower"]}]},
    )
    assert answers.status_code == 200
    body = answers.json()
    assert body["count"] == 1
    assert body["exact_match"] == 100.0
    assert "normalisation" in body

    text_empty = client.post(
        "/api/v1/text", json={"hypotheses": [], "references": [], "metrics": ["bleu"]}
    )
    assert text_empty.status_code == 400
    assert text_empty.json()["detail"] == "hypotheses must not be empty"
