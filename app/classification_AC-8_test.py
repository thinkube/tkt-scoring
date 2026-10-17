# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): posting predicted with matching true labels answers
# accuracy, per-label precision/recall/F1, macro and micro averages, and the
# confusion matrix.
def test_post_classification_answers_all_the_numbers():
    res = TestClient(app).post(
        "/api/v1/classification",
        json={
            "predicted": ["a", "a", "b", "c"],
            "true_labels": ["a", "b", "b", "b"],
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert body["accuracy"] == pytest.approx(0.5)
    assert set(body["per_label"]) == {"a", "b", "c"}
    for label in ("a", "b", "c"):
        assert set(body["per_label"][label]) >= {"precision", "recall", "f1"}
    for avg in ("macro", "micro"):
        assert set(body[avg]) >= {"precision", "recall", "f1"}
    assert body["macro"]["precision"] == pytest.approx(0.5)
    assert body["micro"]["f1"] == pytest.approx(0.5)
    assert len(body["confusion_matrix"]) == 3
