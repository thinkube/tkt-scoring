# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.answers import NORMALISATION
from app.compare import METHOD, compare_systems
from app.rouge_metrics import score_rouge
from app.sacrebleu_metrics import score_sacrebleu

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"]]
A = ["the cat sat on the mat", "a dog barked", "it rained"]
B = ["a cat", "the dog barked at the moon", "it rained all day"]


# WHY (INVARIANT): a comparison says what produced its numbers: the metric's
# provenance and the plain statement of the method travel with the result.
def test_provenance_and_method_carried():
    assert compare_systems("bleu", A, B, REFS, 20, 1)["provenance"] == score_sacrebleu("bleu", A, REFS)[1]
    assert compare_systems("rouge1", A, B, REFS, 20, 1)["provenance"] == score_rouge("rouge1", A, REFS)[1]
    for metric in ("exact_match", "token_f1"):
        r = compare_systems(metric, A, B, REFS, 20, 1)
        assert r["provenance"] == NORMALISATION
    assert compare_systems("ter", A, B, REFS, 20, 1)["method"] == METHOD


# WHY (INVARIANT): the METHOD text alone states pairing, 95% percentile
# intervals, strict-win/no-tie counting, and significance as excluding zero.
def test_method_states_the_four_things():
    m = METHOD.lower()
    assert "same" in m and "resampl" in m
    assert "95" in m and "percentile" in m and "2.5" in m and "97.5" in m
    assert "strictly" in m and "tie" in m
    assert "zero" in m and "significant" in m
