# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.answers import score_answers
from app.compare import compare_systems
from app.rouge_metrics import score_rouge
from app.sacrebleu_metrics import score_sacrebleu

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
A = ["the cat sat on the mat", "a dog barked at the moon", "it rained all night", "we ate bread", "birds sing"]
B = ["a cat on a mat", "the dog barked", "it rained all day long", "bread and cheese", "birds at dawn"]


def _family(metric, hyps):
    if metric in ("bleu", "chrf", "chrf++", "ter"):
        return score_sacrebleu(metric, hyps, REFS)[0]
    if metric in ("rouge1", "rouge2", "rougeL"):
        return score_rouge(metric, hyps, REFS)[0]
    return score_answers(list(zip(hyps, REFS)))[metric]


# WHY (INVARIANT): each system's score in a comparison is the very number the
# metric's own family module gives on the full set, on the same scale.
@pytest.mark.parametrize(
    "metric",
    ["bleu", "chrf", "chrf++", "ter", "rouge1", "rouge2", "rougeL", "exact_match", "token_f1"],
)
def test_scores_equal_family_scores(metric):
    result = compare_systems(metric, A, B, REFS, 50, 1)
    assert result["system_a"]["score"] == pytest.approx(_family(metric, A))
    assert result["system_b"]["score"] == pytest.approx(_family(metric, B))
