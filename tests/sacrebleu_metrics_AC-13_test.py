# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): POST /api/v1/text, given hypotheses, references and a
# chosen subset of the seven metrics, must answer one corpus score per
# metric asked (each paired with what produced it) and nothing for a metric
# that was not asked. It must also score a request whose hypotheses carry
# differing numbers of references each against its own references, refuse a
# request naming a metric outside the seven (naming the offender) with no
# scores answered at all, refuse a request whose reference-group count does
# not match its hypothesis count or whose hypotheses are empty, and answer a
# mixed sacreBLEU + ROUGE request in one response with independent
# provenance per metric. GET /health must still answer {"status": "ok"}.

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_text_answers_one_score_per_requested_metric_and_nothing_else():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat"],
            "references": [["the cat sat on the mat"]],
            "metrics": ["bleu", "chrf"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    metrics = body["metrics"]
    assert set(metrics.keys()) == {"bleu", "chrf"}
    for name in ("bleu", "chrf"):
        assert isinstance(metrics[name]["score"], float)
        assert isinstance(metrics[name]["provenance"], str)
        assert metrics[name]["provenance"].strip() != ""


def test_text_scores_each_hypothesis_against_its_own_reference_group():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
            "references": [
                ["the cat sat on the mat", "a cat sat on a mat"],
                ["a quick brown fox"],
            ],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code == 200
    assert "bleu" in res.json()["metrics"]


def test_text_refuses_metric_outside_the_seven_and_names_it():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat"],
            "references": [["the cat sat on the mat"]],
            "metrics": ["meteor"],
        },
    )
    assert res.status_code >= 400
    assert "meteor" in res.text
    assert "metrics" not in res.json() or res.json().get("metrics") in (None, {})


def test_text_refuses_mismatched_reference_group_count():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat", "a quick brown fox"],
            "references": [["the cat sat on the mat"]],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code >= 400


def test_text_refuses_empty_hypotheses():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": [],
            "references": [],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code >= 400


def test_text_answers_sacrebleu_and_rouge_metrics_together_with_own_provenance():
    res = client.post(
        "/api/v1/text",
        json={
            "hypotheses": ["the cat sat on the mat"],
            "references": [["the cat sat on the mat"]],
            "metrics": ["bleu", "rouge1"],
        },
    )
    assert res.status_code == 200
    metrics = res.json()["metrics"]
    assert set(metrics.keys()) == {"bleu", "rouge1"}
    assert metrics["bleu"]["provenance"] != metrics["rouge1"]["provenance"]


def test_health_still_answers_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
