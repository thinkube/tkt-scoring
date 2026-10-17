# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx

BODY = {"hypotheses": ["a cat"], "references": [["a cat"]], "metrics": ["bleu"]}


# WHY (INVARIANT): the deployed service refuses a made-up bearer token with 401.
def test_made_up_token_is_401():
    res = httpx.post(
        f"{os.environ['TANDEM_LIVE_URL']}/api/v1/text",
        json=BODY,
        headers={"Authorization": "Bearer not-a-real-token-0000"},
        timeout=30,
    )
    assert res.status_code == 401
