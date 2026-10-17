# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): the response carries a statement saying how macro and micro
# averages are formed.
def test_route_response_statement_explains_macro_and_micro():
    res = TestClient(app).post(
        "/api/v1/classification",
        json={"predicted": ["a", "b"], "true_labels": ["a", "a"]},
    )

    assert res.status_code == 200
    statement = res.json()["statement"]
    assert isinstance(statement, str)
    assert "Macro average is the unweighted mean of the per-label values" in statement
    assert "Micro average is computed from the pooled" in statement
    assert "across all labels" in statement
