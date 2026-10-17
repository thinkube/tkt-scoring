# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx


# WHY (INVARIANT): a client of the deployed service that posts a compare
# request without a seed gets 422 naming the seed, and no scores.
def test_compare_without_seed_is_refused_on_the_deployed_service():
    base_url = os.environ["TANDEM_LIVE_URL"]
    token = os.environ["THINKUBE_API_TOKEN"]
    payload = {
        "metric": "bleu",
        "hypotheses_a": ["a b", "c d"],
        "hypotheses_b": ["a x", "c y"],
        "references": [["a b"], ["c d"]],
        "samples": 5,
    }

    res = httpx.post(
        f"{base_url}/api/v1/compare",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    assert res.status_code == 422
    assert "seed" in res.text
    body = res.json()
    for key in ("system_a", "system_b", "difference"):
        assert key not in body
