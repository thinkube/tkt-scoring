# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): asking the ROUGE family for a metric name it does not
# implement must be refused with a message naming the name asked for, and no
# number is invented for it.

import pytest

from app.rouge_metrics import score_rouge


def test_unknown_metric_is_refused_and_names_the_metric():
    hypotheses = ["the cat sat on the mat"]
    references = [["the cat sat on the mat"]]

    with pytest.raises(Exception) as excinfo:
        score_rouge("bleu", hypotheses, references)

    assert "bleu" in str(excinfo.value)
