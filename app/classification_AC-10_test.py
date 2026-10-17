# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): lists of different lengths are refused as a request error
# naming both counts, and no numbers come back.
def test_route_refuses_mismatched_lengths_naming_both_counts():
    res = TestClient(app).post(
        "/api/v1/classification",
        json={
            "predicted": ["a", "b", "a", "b", "a"],
            "true_labels": ["a", "b"],
        },
    )

    assert 400 <= res.status_code < 500
    text = json.dumps(res.json())
    assert "5" in text
    assert "2" in text
    body = res.json()
    for key in ("accuracy", "macro", "micro", "per_label", "confusion_matrix"):
        assert key not in body
