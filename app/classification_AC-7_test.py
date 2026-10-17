# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.classification import DEFINITIONS, score_classification


# WHY (INVARIANT): the result carries a statement saying how macro and micro
# averages are formed, so a reader of the result alone knows what was computed.
def test_statement_says_how_macro_and_micro_are_formed():
    result = score_classification(["a", "b"], ["a", "a"])

    for text in (result["statement"], DEFINITIONS):
        assert "Macro average is the unweighted mean of the per-label values" in text
        assert (
            "Micro average is computed from the pooled true/false positive "
            "and false negative counts across all labels."
        ) in text
