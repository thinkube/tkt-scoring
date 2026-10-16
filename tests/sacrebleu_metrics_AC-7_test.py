# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): a hypothesis sharing no word with any of its references
# must score zero bleu, so a complete mismatch is never scored above zero.

from app.sacrebleu_metrics import score_sacrebleu


def test_bleu_scores_zero_for_a_hypothesis_sharing_no_word_with_its_references():
    hypotheses = ["zzxxqq wwvvyy rrttuu"]
    references = [["the cat sat on the mat", "a dog ran in the park"]]

    score, _signature = score_sacrebleu("bleu", hypotheses, references)

    assert score == 0.0
