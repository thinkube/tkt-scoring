# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest
from fastapi.testclient import TestClient

from app.compare import compare_systems
from app.main import app

client = TestClient(app)


# WHY (INVARIANT): the route adds nothing of its own to the numbers: it
# answers exactly what compare_systems gives for the same inputs.
@pytest.mark.parametrize("metric", ["bleu", "ter", "rouge1", "exact_match"])
def test_route_numbers_equal_module(metric):
    a = ["the cat sat", "a dog barked", "birds sing", "one two"]
    b = ["a cat", "the dog", "zzz", "one two"]
    refs = [["the cat sat"], ["a dog barked"], ["birds sing"], ["one two"]]
    expected = compare_systems(metric, a, b, refs, 120, 8)
    res = client.post(
        "/api/v1/compare",
        json={"hypotheses_a": a, "hypotheses_b": b, "references": refs,
              "metric": metric, "samples": 120, "seed": 8},
    )
    assert res.status_code == 200
    body = res.json()
    for key in ("system_a", "system_b", "difference"):
        for field in ("score", "lower", "upper"):
            assert body[key][field] == pytest.approx(expected[key][field])
    assert body["share_a_beats_b"] == pytest.approx(expected["share_a_beats_b"])
    assert body["significant"] is expected["significant"]
