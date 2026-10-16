# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# INVARIANT: posting hypotheses, their references and a list of metrics
# chosen among bleu, chrf, chrf++, ter, rouge1, rouge2 and rougeL answers one
# corpus score per metric asked, each paired with what produced it, and
# nothing for a metric that was not asked.
def test_text_scores_asked_metrics_only():
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
def test_text_scores_each_hypothesis_against_its_own_references():
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
def test_text_mixes_sacrebleu_and_rouge_with_separate_provenance():
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
# number of hypotheses, or whose hypotheses are empty, is refused with a
# message saying what to correct, and no scores at all are answered.
def test_mismatched_reference_groups_refused():
    payload = {
        "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["bleu"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 400
    assert "reference" in res.json()["detail"].lower()
    assert "hypothes" in res.json()["detail"].lower()


def test_empty_hypotheses_refused():
    payload = {"hypotheses": [], "references": [], "metrics": ["bleu"]}
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 400
    assert "hypothes" in res.json()["detail"].lower()


# INVARIANT: a request naming a metric outside those seven is refused with a
# message that names the offending metric, and no scores at all are
# answered.
def test_unknown_metric_names_the_offender():
    payload = {
        "hypotheses": ["the cat sat on the mat"],
        "references": [["the cat sat on the mat"]],
        "metrics": ["bleu", "meteor"],
    }
    res = client.post("/api/v1/text", json=payload)
    assert res.status_code == 400
    assert "meteor" in res.json()["detail"]


# INVARIANT: GET /health still answers {"status": "ok"} so the platform's
# health check keeps passing.
def test_health_still_answers_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
