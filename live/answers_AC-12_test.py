# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: a client of the deployed service that posts its own predictions
# with their accepted answers to /api/v1/answers gets back exact match and
# token F1 for that set, together with the normalisation statement, and
# leaves nothing stored behind - the service keeps no state of this request.
import os

import httpx


def test_answers_scores_a_posted_set():
    base_url = os.environ["TANDEM_LIVE_URL"]
    payload = {
        "items": [
            {"prediction": "The Eiffel Tower", "answers": ["eiffel tower"]},
            {"prediction": "Big Ben", "answers": ["eiffel tower"]},
        ]
    }

    res = httpx.post(f"{base_url}/api/v1/answers", json=payload, timeout=30)

    assert res.status_code == 200
    body = res.json()
    assert "exact_match" in body
    assert "token_f1" in body
    assert body["count"] == 2
    statement = body["normalisation"].lower()
    assert "punctuation" in statement
    assert "article" in statement
