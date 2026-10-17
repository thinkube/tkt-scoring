# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
A = ["the cat sat on the mat", "a dog barked at the moon", "it rained all night", "we ate bread", "birds sing"]


# WHY (INVARIANT): when both systems give identical outputs the comparison
# shows no difference at all (0, interval [0, 0], share 0, not significant),
# which proves both are scored on the same resampled items in every sample.
@pytest.mark.parametrize("metric", ["bleu", "ter", "rouge1", "exact_match"])
def test_identical_systems_show_no_difference(metric):
    r = compare_systems(metric, A, list(A), REFS, 200, 5)
    assert r["difference"]["score"] == 0
    assert r["difference"]["lower"] == 0
    assert r["difference"]["upper"] == 0
    assert r["share_a_beats_b"] == 0
    assert r["significant"] is False
