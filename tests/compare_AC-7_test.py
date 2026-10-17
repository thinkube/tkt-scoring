# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.compare import compare_systems

REFS = [["the cat sat on the mat"], ["a dog barked at the moon"], ["it rained all day long"], ["we ate bread and cheese"], ["birds sing at dawn"]]
PERFECT = [r[0] for r in REFS]
NONE = ["zzz yyy xxx"] * 5


# WHY (INVARIANT): for TER, where lower is better, the first system counts as
# beating the second when its TER is lower; the difference stays first minus
# second on TER's own scale (so it is negative when the first is better).
def test_ter_lower_is_a_win():
    r = compare_systems("ter", PERFECT, NONE, REFS, 200, 2)
    assert r["share_a_beats_b"] == 1
    assert r["difference"]["score"] < 0
    assert r["significant"] is True

    swapped = compare_systems("ter", NONE, PERFECT, REFS, 200, 2)
    assert swapped["share_a_beats_b"] == 0
    assert swapped["difference"]["score"] > 0
