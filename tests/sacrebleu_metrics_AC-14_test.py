# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): a request whose number of reference groups does not match
# its number of hypotheses, or whose hypotheses are empty, must be refused
# with a message saying what to correct, rather than silently scored or
# padded. This test is distinct from AC-13's broader /api/v1/text coverage:
# it isolates the exact wording requirement ("saying what to correct").

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mismatched_reference_groups_message_says_what_to_correct():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
            "references": [["the cat sat on the mat"]],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code >= 400
    body_text = res.text.lower()
    assert "reference" in body_text or "hypothes" in body_text


def test_empty_hypotheses_message_says_what_to_correct():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": [],
            "references": [],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code >= 400
    body_text = res.text.lower()
    assert "hypothes" in body_text or "empty" in body_text
