# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
A = ["the cat sat on the mat", "a dog barked at the moon", "it rained all night", "we ate bread", "birds sing"]
B = ["a cat on a mat", "the dog barked", "it rained all day long", "bread and cheese", "birds at dawn"]


# WHY (INVARIANT): every interval is well-formed (lower <= upper) and the
# share of samples in which the first system wins is a proportion in 0..1.
@pytest.mark.parametrize("metric", ["bleu", "chrf", "ter", "rouge2", "rougeL", "exact_match", "token_f1"])
def test_intervals_ordered_and_share_in_range(metric):
    r = compare_systems(metric, A, B, REFS, 200, 11)
    for key in ("system_a", "system_b", "difference"):
        assert r[key]["lower"] <= r[key]["upper"]
    assert 0 <= r["share_a_beats_b"] <= 1
