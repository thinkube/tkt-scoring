# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

import app.compare as compare


class ScoreComputed(Exception):
    """Raised by the stand-in scorer: proves a score was attempted."""


@pytest.fixture(autouse=True)
def no_scoring(monkeypatch):
    def boom(*args, **kwargs):
        raise ScoreComputed("a score was computed")

    monkeypatch.setattr(compare, "_score", boom)


def _call(seed):
    return compare.compare_systems(
        "bleu",
        ["the cat sat"],
        ["a cat sat"],
        [["the cat sat"]],
        10,
        seed,
    )


# WHY (INVARIANT): a seed that is None, a boolean, a fraction or a string is
# refused with a ValueError that names seed and says to send a whole number,
# and it is refused before any score is computed.
@pytest.mark.parametrize("bad", [None, True, False, 1.5, 0.25, "7", "abc", ""])
def test_bad_seed_refused_before_scoring(bad):
    with pytest.raises(ValueError) as info:
        _call(bad)
    message = str(info.value).lower()
    assert "seed" in message
    assert "whole number" in message


# WHY (INVARIANT): the refusal is specific to the seed; a whole-number seed
# is not refused (it reaches scoring).
@pytest.mark.parametrize("good", [0, 7, -3])
def test_whole_number_seed_is_not_refused(good):
    with pytest.raises(ScoreComputed):
        _call(good)
