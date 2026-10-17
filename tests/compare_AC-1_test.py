# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
A = ["the cat sat on the mat", "a dog barked at the moon", "it rained all night", "we ate bread", "birds sing"]
B = ["a cat on a mat", "the dog barked", "it rained all day long", "bread and cheese", "birds at dawn"]


# WHY (INVARIANT): the same inputs, metric, sample count and seed always give
# an identical comparison, so a reported result can be reproduced.
@pytest.mark.parametrize("metric", ["bleu", "rouge1", "exact_match"])
def test_compare_is_deterministic(metric):
    first = compare_systems(metric, A, B, REFS, 200, 7)
    second = compare_systems(metric, A, B, REFS, 200, 7)
    assert first == second
