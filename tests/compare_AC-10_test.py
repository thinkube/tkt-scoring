# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.compare import compare_systems
from app.main import app

client = TestClient(app)


# WHY (INVARIANT): posting two systems' outputs, references, a metric, a
# sample count and a seed to /api/v1/compare answers 200 with both scores and
# intervals, the difference and interval, the share, and the significance.
def test_compare_answers_scores_and_intervals():
    payload = {
        "hypotheses_a": ["the cat sat", "a dog barked", "birds sing"],
        "hypotheses_b": ["a cat", "the dog", "zzz"],
        "references": [["the cat sat"], ["a dog barked"], ["birds sing"]],
        "metric": "bleu",
        "samples": 100,
        "seed": 4,
    }
    res = client.post("/api/v1/compare", json=payload)
    assert res.status_code == 200
    body = res.json()
    for key in ("system_a", "system_b", "difference"):
        for field in ("score", "lower", "upper"):
            assert isinstance(body[key][field], (int, float))
    assert 0 <= body["share_a_beats_b"] <= 1
    assert isinstance(body["significant"], bool)
    expected = compare_systems(
        "bleu", payload["hypotheses_a"], payload["hypotheses_b"], payload["references"], 100, 4
    )
    assert body["system_a"]["score"] == expected["system_a"]["score"]
    assert body["significant"] == expected["significant"]
