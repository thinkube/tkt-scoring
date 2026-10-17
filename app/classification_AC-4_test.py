# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import score_classification


# WHY (INVARIANT): the confusion matrix is square, rows are the true label,
# columns the predicted label, and it comes with the label order it is written in.
def test_confusion_matrix_is_square_true_by_row_predicted_by_column_with_its_labels():
    result = score_classification(["a", "a", "b", "c"], ["a", "b", "b", "b"])

    labels = result["labels"]
    matrix = result["confusion_matrix"]
    assert sorted(labels) == ["a", "b", "c"]
    assert len(matrix) == len(labels)
    assert all(len(row) == len(labels) for row in matrix)

    def cell(true, pred):
        return matrix[labels.index(true)][labels.index(pred)]

    assert cell("a", "a") == 1
    assert cell("b", "a") == 1
    assert cell("b", "b") == 1
    assert cell("b", "c") == 1
    assert cell("a", "b") == 0
    assert sum(sum(row) for row in matrix) == 4
