# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
A = ["the cat sat on the mat", "a dog barked at the moon", "it rained all night", "we ate bread", "birds sing"]
B = ["a cat on a mat", "the dog barked", "it rained all day long", "bread and cheese", "birds at dawn"]
NONE = ["zzz yyy"] * 5


# WHY (INVARIANT): the difference is first minus second, and a result is
# marked significant exactly when its difference interval excludes zero.
@pytest.mark.parametrize("metric", ["bleu", "ter", "rouge1", "exact_match", "token_f1"])
@pytest.mark.parametrize("other", [B, NONE, REFS and [r[0] for r in REFS]])
def test_difference_and_significance(metric, other):
    r = compare_systems(metric, A, other, REFS, 300, 3)
    assert r["difference"]["score"] == pytest.approx(
        r["system_a"]["score"] - r["system_b"]["score"]
    )
    d = r["difference"]
    excludes = d["lower"] > 0 or d["upper"] < 0
    assert r["significant"] is excludes
