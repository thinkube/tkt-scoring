# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): chrf answers a corpus score plus a sacreBLEU signature
# stating sacreBLEU version 2.6.0, so every chrf number is traceable to the
# sacreBLEU release that produced it.

from app.sacrebleu_metrics import score_sacrebleu


def test_chrf_returns_score_and_signature_with_sacrebleu_version():
    hypotheses = ["the cat sat on the mat", "a quick brown fox"]
    references = [["the cat sat on the mat"], ["a quick brown fox"]]

    score, signature = score_sacrebleu("chrf", hypotheses, references)

    assert isinstance(score, float)
    assert isinstance(signature, str)
    assert "2.6.0" in signature
