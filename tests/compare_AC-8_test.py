# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.compare import compare_systems

H = ["the cat", "a dog", "birds sing"]
R = [["the cat"], ["a dog"], ["birds sing"]]


# WHY (INVARIANT): bad input is refused with a ValueError that names the
# offender, before any number is produced.
def test_unknown_metric_is_named():
    with pytest.raises(ValueError, match="bogus_metric"):
        compare_systems("bogus_metric", H, H, R, 10, 1)


def test_systems_of_different_lengths():
    with pytest.raises(ValueError):
        compare_systems("bleu", H, H[:2], R, 10, 1)


def test_references_length_names_both_counts():
    with pytest.raises(ValueError) as e:
        compare_systems("bleu", H, H, R[:2], 10, 1)
    assert "2" in str(e.value) and "3" in str(e.value)


def test_empty_outputs():
    with pytest.raises(ValueError):
        compare_systems("bleu", [], [], [], 10, 1)


def test_empty_reference_group_position_from_zero():
    with pytest.raises(ValueError) as e:
        compare_systems("bleu", H, H, [["the cat"], [], ["birds sing"]], 10, 1)
    assert "1" in str(e.value)


@pytest.mark.parametrize("samples", [0, -5, 2.5])
def test_samples_must_be_positive_whole(samples):
    with pytest.raises(ValueError, match="samples"):
        compare_systems("bleu", H, H, R, samples, 1)
