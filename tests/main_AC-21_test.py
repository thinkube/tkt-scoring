# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

HYP_A = ["a b c", "c d e", "x y z", "p q r", "m n o"]
HYP_B = ["a b x", "c y e", "x y z", "p z r", "m n q"]
REFS = [["a b c"], ["c d e"], ["x y z"], ["p q r"], ["m n o"]]


# WHY (INVARIANT): compare_systems with a whole-number seed still gives the
# same result for the same inputs and seed.
@pytest.mark.parametrize("metric", ["bleu", "chrf", "ter"])
@pytest.mark.parametrize("seed", [0, 7, 123456789, -3])
def test_compare_systems_is_repeatable_for_a_whole_number_seed(metric, seed):
    first = compare_systems(metric, HYP_A, HYP_B, REFS, 25, seed)
    second = compare_systems(metric, list(HYP_A), list(HYP_B),
                             [list(g) for g in REFS], 25, seed)
    assert first == second
    assert first["seed"] == seed
