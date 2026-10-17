# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: a client of the deployed service that posts predicted labels with
# the matching true labels to /api/v1/classification gets back accuracy, the
# per-label precision, recall and F1, the macro and micro averages, and the
# confusion matrix with the label order it is written in (rows true, columns
# predicted), together with the statement of the definitions used.
import json
import os

import httpx

NUMBER_KEYS = ("accuracy", "per_label", "macro", "micro", "confusion_matrix")


def _url():
    return f"{os.environ['TANDEM_LIVE_URL']}/api/v1/classification"


def test_classification_scores_a_posted_set():
    payload = {
        "predicted": ["a", "a", "b", "c"],
        "true_labels": ["a", "b", "b", "b"],
    }

    res = httpx.post(_url(), json=payload, timeout=30)

    assert res.status_code == 200
    body = res.json()
    assert body["accuracy"] == 0.5
    labels = body["labels"]
    assert sorted(labels) == ["a", "b", "c"]
    matrix = body["confusion_matrix"]
    assert len(matrix) == len(labels)
    assert all(len(row) == len(labels) for row in matrix)
    # rows are the true label, columns the predicted label
    assert matrix[labels.index("b")][labels.index("a")] == 1
    assert matrix[labels.index("a")][labels.index("b")] == 0
    assert sum(sum(row) for row in matrix) == 4
    per_label = body["per_label"]
    assert set(per_label) == {"a", "b", "c"}
    for label in labels:
        assert set(per_label[label]) >= {"precision", "recall", "f1"}
    assert abs(per_label["a"]["precision"] - 0.5) < 1e-9
    assert abs(per_label["a"]["recall"] - 1.0) < 1e-9
    assert abs(per_label["b"]["recall"] - 1 / 3) < 1e-9
    assert per_label["c"]["f1"] == 0
    assert abs(body["macro"]["precision"] - 0.5) < 1e-9
    for key in ("precision", "recall", "f1"):
        assert abs(body["micro"][key] - 0.5) < 1e-9
        assert key in body["macro"]
    statement = body["statement"]
    assert "Macro average is the unweighted mean of the per-label values" in statement
    assert "Micro average is comput" in statement
    assert "pooled" in statement


def test_classification_refuses_mismatched_lengths_and_names_both_counts():
    payload = {"predicted": ["a"] * 5, "true_labels": ["a", "b"]}

    res = httpx.post(_url(), json=payload, timeout=30)

    assert 400 <= res.status_code < 500
    body = res.json()
    text = json.dumps(body)
    assert "5" in text
    assert "2" in text
    for key in NUMBER_KEYS:
        assert key not in body


def test_classification_refuses_empty_or_missing_fields_and_names_them():
    for payload in (
        {"predicted": [], "true_labels": []},
        {"predicted": ["a"]},
        {"true_labels": ["a"]},
        {},
    ):
        res = httpx.post(_url(), json=payload, timeout=30)

        assert 400 <= res.status_code < 500
        body = res.json()
        text = json.dumps(body)
        assert "predicted" in text
        assert "true" in text
        assert "non-empty list" in text
        assert "same length" in text
        for key in NUMBER_KEYS:
            assert key not in body


def test_classification_keeps_other_routes_answering():
    base_url = os.environ["TANDEM_LIVE_URL"]
    answers = httpx.post(
        f"{base_url}/api/v1/answers",
        json={"items": [{"prediction": "Big Ben", "answers": ["big ben"]}]},
        timeout=30,
    )
    assert answers.status_code == 200
    assert answers.json()["count"] == 1
