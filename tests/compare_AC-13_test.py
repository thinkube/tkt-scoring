# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest
from fastapi.testclient import TestClient

from app.compare import compare_systems
from app.main import app

client = TestClient(app)

GOOD = {
    "hypotheses_a": ["the cat", "a dog"],
    "hypotheses_b": ["a cat", "the dog"],
    "references": [["the cat"], ["a dog"]],
    "metric": "bleu",
    "samples": 20,
    "seed": 1,
}


def _post(**changes):
    return client.post("/api/v1/compare", json={**GOOD, **changes})


def _detail(res):
    assert res.status_code == 400
    return str(res.json()["detail"])


# WHY (INVARIANT): bad requests are refused with 400 and a message that says
# what to send, rather than a number or a bare validation error.
def test_empty_outputs():
    assert _detail(_post(hypotheses_a=[], hypotheses_b=[], references=[])) != ""


def test_unknown_metric_lists_accepted_keys():
    detail = _detail(_post(metric="bogus"))
    for key in ("bleu", "chrf", "ter", "rouge1", "rougeL", "exact_match", "token_f1"):
        assert key in detail


def test_systems_of_different_lengths_name_counts():
    detail = _detail(_post(hypotheses_b=["a cat", "the dog", "x"]))
    assert "2" in detail and "3" in detail


def test_references_of_different_length_name_counts():
    detail = _detail(_post(references=[["the cat"]]))
    assert "1" in detail and "2" in detail


def test_route_refuses_what_compare_systems_refuses():
    with pytest.raises(ValueError):
        compare_systems("bleu", ["a"], ["a", "b"], [["a"]], 10, 1)
    assert _post(hypotheses_b=["a cat"]).status_code == 400


@pytest.mark.parametrize("samples", [0, -5])
def test_samples_must_be_positive(samples):
    assert "samples" in _detail(_post(samples=samples))
