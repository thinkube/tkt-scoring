# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): empty lists or a missing field are refused with a 4xx whose
# message names the required fields and says each must be a non-empty list of
# the same length.
@pytest.mark.parametrize(
    "payload",
    [
        {"predicted": [], "true_labels": []},
        {"true_labels": ["a"]},
        {"predicted": ["a"]},
        {},
    ],
)
def test_route_refuses_empty_or_missing_lists_saying_what_to_fix(payload):
    res = TestClient(app).post("/api/v1/classification", json=payload)

    assert 400 <= res.status_code < 500
    text = json.dumps(res.json())
    assert "predicted" in text
    assert "true" in text
    assert "non-empty list" in text
    assert "same length" in text
