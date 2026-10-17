# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app


# WHY (INVARIANT): the response names the label order of the confusion matrix,
# and that order has as many labels as the matrix has rows and columns.
def test_response_label_order_matches_matrix_size():
    res = TestClient(app).post(
        "/api/v1/classification",
        json={
            "predicted": ["cat", "dog", "cat", "bird"],
            "true_labels": ["cat", "cat", "dog", "dog"],
        },
    )

    assert res.status_code == 200
    body = res.json()
    labels = body["labels"]
    matrix = body["confusion_matrix"]
    assert sorted(labels) == ["bird", "cat", "dog"]
    assert len(matrix) == len(labels)
    assert all(len(row) == len(labels) for row in matrix)
    # true cat row, predicted cat column: one correct cat
    assert matrix[labels.index("cat")][labels.index("cat")] == 1
    # true dog predicted cat: one
    assert matrix[labels.index("dog")][labels.index("cat")] == 1
