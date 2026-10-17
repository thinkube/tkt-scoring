# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth import control_client
from app.compare import compare_systems
from app.main import app

GOOD = {
    "hypotheses_a": ["the cat", "a dog"],
    "hypotheses_b": ["a cat", "the dog"],
    "references": [["the cat"], ["a dog"]],
    "metric": "bleu",
    "samples": 20,
    "seed": 1,
}

TOKEN = {"Authorization": "Bearer test-token"}


class _AcceptingControl:
    """Stands in for Thinkube Control: accepts every token."""

    def get(self, url, headers=None):
        return httpx.Response(200, json={"valid": True})

    def close(self):
        pass


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "http://control.test")
    app.dependency_overrides[control_client] = lambda: _AcceptingControl()
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(control_client, None)


def _post(client, **changes):
    return client.post(
        "/api/v1/compare", json={**GOOD, **changes}, headers=TOKEN
    )


def _detail(res):
    assert res.status_code == 422
    return str(res.json()["detail"])


# WHY (INVARIANT): bad requests are refused with 422 and a message that says
# what to send, rather than a number or a bare validation error.
def test_empty_outputs(client):
    assert (
        _detail(_post(client, hypotheses_a=[], hypotheses_b=[], references=[]))
        != ""
    )


def test_unknown_metric_lists_accepted_keys(client):
    detail = _detail(_post(client, metric="bogus"))
    for key in ("bleu", "chrf", "ter", "rouge1", "rougeL", "exact_match", "token_f1"):
        assert key in detail


def test_systems_of_different_lengths_name_counts(client):
    detail = _detail(_post(client, hypotheses_b=["a cat", "the dog", "x"]))
    assert "2" in detail and "3" in detail


def test_references_of_different_length_name_counts(client):
    detail = _detail(_post(client, references=[["the cat"]]))
    assert "1" in detail and "2" in detail


def test_route_refuses_what_compare_systems_refuses(client):
    with pytest.raises(ValueError):
        compare_systems("bleu", ["a"], ["a", "b"], [["a"]], 10, 1)
    assert _post(client, hypotheses_b=["a cat"]).status_code == 422


@pytest.mark.parametrize("samples", [0, -5])
def test_samples_must_be_positive(client, samples):
    assert "samples" in _detail(_post(client, samples=samples))


# WHY (INVARIANT): the seed is required; a missing or non-whole seed is
# refused naming seed, and no seed of 0 is ever filled in.
def test_missing_seed_is_refused_and_not_defaulted(client):
    body = {k: v for k, v in GOOD.items() if k != "seed"}
    res = client.post("/api/v1/compare", json=body, headers=TOKEN)
    assert "seed" in _detail(res)
    assert "scores" not in res.json()


@pytest.mark.parametrize("seed", [1.5, "seven", True])
def test_route_refuses_a_seed_that_is_not_whole(client, seed):
    assert "seed" in _detail(_post(client, seed=seed))


@pytest.mark.parametrize("seed", [None, True, 1.5, "7"])
def test_compare_systems_refuses_a_bad_seed(seed):
    with pytest.raises(ValueError) as err:
        compare_systems("bleu", ["a"], ["b"], [["a"]], 10, seed)
    assert "seed" in str(err.value)
    assert "whole number" in str(err.value)


def test_compare_systems_same_seed_same_result():
    args = ("bleu", ["the cat", "a dog"], ["a cat", "the dog"],
            [["the cat"], ["a dog"]], 20, 3)
    assert compare_systems(*args) == compare_systems(*args)


# WHY (INVARIANT): the README and the how-to pages say 422, never 400.
def test_docs_say_422_and_not_400():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    pages = [root / "README.md"] + sorted((root / "docs").glob("i-can-*.md"))
    assert pages
    for page in pages:
        text = page.read_text(encoding="utf-8")
        assert "422" in text, page.name
        assert "400" not in text, page.name
    compare = (
        root / "docs" / "i-can-compare-two-systems-and-see-whether-the-difference-is-real.md"
    ).read_text(encoding="utf-8")
    assert "seed" in compare and "required" in compare
