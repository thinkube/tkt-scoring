# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
PERFECT = [r[0] for r in REFS]
NONE = ["zzz yyy xxx"] * 5


# WHY (INVARIANT): a system that matches every reference clearly beats one that
# shares no words with them: positive difference, share 1, significant.
@pytest.mark.parametrize("metric", ["bleu", "rouge1", "exact_match"])
def test_perfect_beats_disjoint(metric):
    r = compare_systems(metric, PERFECT, NONE, REFS, 200, 9)
    assert r["difference"]["score"] > 0
    assert r["share_a_beats_b"] == 1
    assert r["significant"] is True
