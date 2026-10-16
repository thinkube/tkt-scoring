# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): bleu answers a corpus score plus a sacreBLEU signature
# stating sacreBLEU version 2.6.0, so every bleu number is traceable to the
# sacreBLEU release that produced it.

from app.sacrebleu_metrics import score_sacrebleu


def test_bleu_returns_score_and_signature_with_sacrebleu_version():
    hypotheses = ["the cat sat on the mat", "a quick brown fox"]
    references = [["the cat sat on the mat"], ["a quick brown fox"]]

    score, signature = score_sacrebleu("bleu", hypotheses, references)

    assert isinstance(score, float)
    assert isinstance(signature, str)
    assert "2.6.0" in signature
