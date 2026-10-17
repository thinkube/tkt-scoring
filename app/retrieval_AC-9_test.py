# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402


# WHY (INVARIANT): the response alone states what counts as relevant, how a
# grade feeds nDCG's gain, and the grade scale with ungraded = 1.
def test_definitions_field_names_relevance_gain_and_grade_scale():
    res = TestClient(app).post(
        "/api/v1/retrieval",
        json={"queries": [{"retrieved": ["a"], "relevant": [{"id": "a"}]}], "k": [1]},
    )
    assert res.status_code == 200
    text = res.json()["definitions"].lower()
    assert "relevant" in text
    assert "present" in text or "presence" in text or "listed" in text
    assert "grade" in text
    assert "gain" in text
    assert "ndcg" in text
    assert "ungraded" in text or "without a grade" in text or "default" in text
    assert "1" in text
    assert "0" in text  # the scale's lower bound
