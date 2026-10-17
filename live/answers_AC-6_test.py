# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

# WHY (INVARIANT): against the deployed service, a client that posts the
# prediction "The  Eiffel-Tower!" with accepted answer "eiffeltower" to
# /api/v1/answers gets exact_match 100.
import os

import httpx


def test_deployed_answers_deletes_punctuation_before_matching():
    base_url = os.environ["TANDEM_LIVE_URL"]
    payload = {
        "items": [{"prediction": "The  Eiffel-Tower!", "answers": ["eiffeltower"]}]
    }
    headers = {"Authorization": f"Bearer {os.environ['THINKUBE_API_TOKEN']}"}

    res = httpx.post(
        f"{base_url}/api/v1/answers", json=payload, headers=headers, timeout=30
    )

    assert res.status_code == 200
    assert res.json()["exact_match"] == 100
