# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

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
    assert body["count"] == 2
    assert body["exact_match"] == 50.0
    assert 0.0 <= body["token_f1"] <= 100.0

    statement = body["normalisation"].lower()
    assert "case" in statement or "lower" in statement
    assert "punctuation" in statement
    assert "article" in statement
    assert "whitespace" in statement or "space" in statement
