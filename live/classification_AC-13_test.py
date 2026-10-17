# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx


# WHY (INVARIANT): the deployed service keeps nothing of a classification
# request; a client can only see that the answer is complete and a repeat
# post is independent. Inspecting the service's logs and stores is an
# operator check and is not provable from the client side.
def test_classification_answer_is_complete_and_leaves_no_trace_in_later_answers():
    base_url = os.environ["TANDEM_LIVE_URL"]
    marker = "zq" + os.urandom(4).hex()
    payload = {"predicted": [marker, "x"], "true_labels": [marker, marker]}

    headers = {"Authorization": f"Bearer {os.environ['THINKUBE_API_TOKEN']}"}

    first = httpx.post(
        f"{base_url}/api/v1/classification", json=payload, headers=headers, timeout=30
    )
    assert first.status_code == 200
    assert first.json()["accuracy"] == 0.5

    other = httpx.post(
        f"{base_url}/api/v1/classification",
        json={"predicted": ["x"], "true_labels": ["x"]},
        headers=headers,
        timeout=30,
    )
    assert other.status_code == 200
    assert marker not in other.text
    assert other.json()["labels"] == ["x"]
