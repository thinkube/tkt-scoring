# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.auth import control_client
from app.main import app

HEADERS = {"Authorization": "Bearer good-token"}


def _accepting_control():
    # A fake Control that accepts every token.
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    )
    try:
        yield client
    finally:
        client.close()


# WHY (INVARIANT): adding the classification route must not change the health
# check, the text route or the answers route (apart from the 422 refusal and
# the bearer token every route but /health now needs).
def test_health_text_and_answers_still_answer_as_before(monkeypatch):
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "http://control.test")
    app.dependency_overrides[control_client] = _accepting_control
    try:
        with TestClient(app) as client:
            health = client.get("/health")
            assert health.status_code == 200
            assert health.json() == {"status": "ok"}

            answers = client.post(
                "/api/v1/answers",
                json={
                    "items": [
                        {"prediction": "The Eiffel Tower", "answers": ["eiffel tower"]}
                    ]
                },
                headers=HEADERS,
            )
            assert answers.status_code == 200
            body = answers.json()
            assert body["count"] == 1
            assert body["exact_match"] == 100.0
            assert "normalisation" in body

            text_empty = client.post(
                "/api/v1/text",
                json={"hypotheses": [], "references": [], "metrics": ["bleu"]},
                headers=HEADERS,
            )
            assert text_empty.status_code == 422
            assert "hypotheses" in text_empty.json()["detail"]

            # No token: refused with 401 before anything is scored.
            no_token = client.post("/api/v1/answers", json={"items": []})
            assert no_token.status_code == 401

            # Compare with no seed: refused with 422 naming seed, no 0 filled in.
            no_seed = client.post(
                "/api/v1/compare",
                json={
                    "metric": "bleu",
                    "hypotheses_a": ["a b c"],
                    "hypotheses_b": ["a b d"],
                    "references": [["a b c"]],
                    "samples": 10,
                },
                headers=HEADERS,
            )
            assert no_seed.status_code == 422
            assert "seed" in str(no_seed.json()["detail"])
    finally:
        app.dependency_overrides.pop(control_client, None)
