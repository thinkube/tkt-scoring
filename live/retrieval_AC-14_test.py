# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import uuid

import httpx


# WHY (INVARIANT): a scored request leaves no trace of its ids, grades or
# cut-offs. Only the client side is observable here: the response must not
# echo the posted ids, and a later request must not surface them.
def test_retrieval_leaves_no_client_visible_trace_of_posted_ids():
    base_url = os.environ["TANDEM_LIVE_URL"]
    tag = uuid.uuid4().hex
    ranked = f"rank-{tag}"
    relevant = f"rel-{tag}"
    payload = {
        "queries": [
            {
                "retrieved": [ranked, relevant],
                "relevant": [{"id": relevant, "grade": 2}],
            }
        ],
        "k": [2],
    }

    res = httpx.post(f"{base_url}/api/v1/retrieval", json=payload, timeout=30)
    assert res.status_code == 200
    assert ranked not in res.text and relevant not in res.text

    again = httpx.post(
        f"{base_url}/api/v1/retrieval",
        json={"queries": [{"retrieved": ["z"], "relevant": [{"id": "z"}]}], "k": [1]},
        timeout=30,
    )
    assert again.status_code == 200
    assert ranked not in again.text and relevant not in again.text
