# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# INVARIANT: a client of the deployed service that posts its own two systems'
# outputs and references to /api/v1/compare reads back both scores with their
# intervals, the difference with its interval, the share and the significance.
import os

import httpx


def test_compare_two_posted_systems():
    payload = {
        "hypotheses_a": ["the cat sat on the mat", "a dog barked", "birds sing at dawn"],
        "hypotheses_b": ["zzz yyy", "xxx www", "vvv uuu"],
        "references": [["the cat sat on the mat"], ["a dog barked"], ["birds sing at dawn"]],
        "metric": "bleu",
        "samples": 200,
        "seed": 3,
    }

    res = httpx.post(
        f"{os.environ['TANDEM_LIVE_URL']}/api/v1/compare", json=payload, timeout=60
    )

    assert res.status_code == 200
    body = res.json()
    for key in ("system_a", "system_b", "difference"):
        assert body[key]["lower"] <= body[key]["upper"]
        assert isinstance(body[key]["score"], (int, float))
    assert body["difference"]["score"] > 0
    assert body["share_a_beats_b"] == 1
    assert body["significant"] is True
    assert body["method"] and body["provenance"]
