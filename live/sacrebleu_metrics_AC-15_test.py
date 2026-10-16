# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (TRANSITION): proves the deployed service's new POST /api/v1/text
# route is actually live and reachable by a client that posts its own
# hypotheses and references, and reads back, for every metric it asked, the
# corpus score and the sacreBLEU signature or ROUGE implementation and
# version that produced it. This check's job is done once the route is
# confirmed live; it does not import repository code and keeps nothing
# stored behind.

import os

import httpx


def test_text_scores_a_posted_corpus():
    base_url = os.environ["TANDEM_LIVE_URL"]

    payload = {
        "hypotheses": ["the cat sat on the mat", "a quick brown fox jumps"],
        "references": [
            ["the cat sat on the mat"],
            ["a quick brown fox jumps", "a fast brown fox leaps"],
        ],
        "metrics": ["bleu", "chrf", "rouge1"],
    }

    res = httpx.post(f"{base_url}/api/v1/text", json=payload, timeout=30.0)
    assert res.status_code == 200

    body = res.json()
    metrics = body["metrics"]
    assert set(metrics.keys()) == {"bleu", "chrf", "rouge1"}
    for name in ("bleu", "chrf", "rouge1"):
        assert isinstance(metrics[name]["score"], (int, float))
        assert isinstance(metrics[name]["provenance"], str)
        assert metrics[name]["provenance"].strip() != ""
