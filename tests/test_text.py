# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import httpx
import pytest
from fastapi.testclient import TestClient

import app.auth as auth
from app.main import app

HEADERS = {"Authorization": "Bearer test-token"}


class _Client:
    """Posts and gets with the bearer token on every call."""

    def __init__(self, inner):
        self._inner = inner

    def post(self, url, **kw):
        return self._inner.post(url, headers=HEADERS, **kw)

    def get(self, url, **kw):
        return self._inner.get(url, **kw)


@pytest.fixture(autouse=True)
def client(monkeypatch):
    # A fake Control that accepts every token; the lifespan runs because the
    # TestClient is entered, so the configured address is in place.
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "http://control.test")
    fake = lambda: httpx.Client(  # noqa: E731
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    app.dependency_overrides[auth.control_client] = fake
    try:
        with TestClient(app) as inner:
            yield _Client(inner)
    finally:
        app.dependency_overrides.pop(auth.control_client, None)


# INVARIANT: posting hypotheses, their references and a list of metrics
# chosen among bleu, chrf, chrf++, ter, rouge1, rouge2 and rougeL answers one
# corpus score per metric asked, each paired with what produced it, and
# nothing for a metric that was not asked.
def test_text_scores_asked_metrics_only(client):
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["bleu", "rouge1"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert set(body["metrics"].keys()) == {"bleu", "rouge1"}

    for name in ("bleu", "rouge1"):
        assert isinstance(body["metrics"][name]["score"], float)
        assert isinstance(body["metrics"][name]["provenance"], str)
        assert body["metrics"][name]["provenance"] != ""


# INVARIANT: a request that gives several references for one hypothesis and
# a single reference for another is scored, each hypothesis against its own
# references.
def test_text_scores_each_hypothesis_against_its_own_references(client):
    payload = {
        "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
        "references": [
            ["the cat sat on the mat", "a cat sat on the mat"],
            ["a quick brown fox"],
        ],
        "metrics": ["bleu", "rouge1", "rougeL", "chrf", "chrf++", "ter", "rouge2"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert set(body["metrics"].keys()) == {
        "bleu",
        "rouge1",
        "rougeL",
        "chrf",
        "chrf++",
        "ter",
        "rouge2",
    }


# INVARIANT: a request asking for both a sacreBLEU metric and a ROUGE metric
# answers both in one response, each with its own provenance.
def test_text_mixes_sacrebleu_and_rouge_with_separate_provenance(client):
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["chrf++", "rougeL"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 200

    body = res.json()
    sacrebleu_provenance = body["metrics"]["chrf++"]["provenance"]
    rouge_provenance = body["metrics"]["rougeL"]["provenance"]
    assert sacrebleu_provenance != rouge_provenance
    assert "2.6.0" in sacrebleu_provenance
    assert "rouge" in rouge_provenance.lower()


# INVARIANT: a request whose number of reference groups does not match its
# number of hypotheses, or whose hypotheses are empty, is refused with 422 and
# a message saying what to correct, and no scores at all are answered.
def test_mismatched_reference_groups_refused(client):
    payload = {
        "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["bleu"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert "reference" in detail.lower()
    assert "hypothes" in detail.lower()
    assert "2" in detail and "1" in detail
    assert "metrics" not in res.json()


def test_empty_hypotheses_refused(client):
    payload = {"hypotheses": [], "references": [], "metrics": ["bleu"]}
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    assert "hypothes" in res.json()["detail"].lower()
    assert "metrics" not in res.json()


# INVARIANT: an empty metrics list is refused with 422 naming metrics, never
# answered with an empty set of scores.
def test_empty_metrics_refused(client):
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
        "metrics": [],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    assert "metrics" in res.json()["detail"].lower()
    assert "metrics" not in res.json()


# INVARIANT: an empty reference group is refused with 422 naming its position
# counting from 0, and no score is computed.
def test_empty_reference_group_names_its_position(client):
    payload = {
        "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
        "references": [["the cat sat on the mat"], []],
        "metrics": ["bleu"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    assert "1" in res.json()["detail"]
    assert "metrics" not in res.json()


# INVARIANT: a request missing its metrics field is refused with 422 and a
# refusal naming metrics.
def test_missing_metrics_field_refused(client):
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    assert "metrics" in res.text.lower()
    assert "metrics" not in res.json()


# INVARIANT: a request naming a metric outside those seven is refused with a
# 422 message that names the offending metric, and no scores at all are
# answered, the known metrics in the same request included.
def test_unknown_metric_names_the_offender(client):
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["bleu", "meteor"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 422
    assert "meteor" in res.json()["detail"]
    assert "metrics" not in res.json()


# INVARIANT: GET /health still answers {"status": "ok"} so the platform's
# health check keeps passing.
def test_health_still_answers_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
