# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx
import pytest

BODIES = {
    "/api/v1/text": {"hypotheses": ["a cat"], "references": [["a cat"]], "metrics": ["bleu"]},
    "/api/v1/answers": {"items": [{"prediction": "Big Ben", "answers": ["big ben"]}]},
    "/api/v1/classification": {"predicted": ["a", "b"], "true_labels": ["a", "b"]},
    "/api/v1/compare": {
        "hypotheses_a": ["a cat", "a dog"], "hypotheses_b": ["the cat", "the dog"],
        "references": [["a cat"], ["a dog"]], "metric": "bleu", "samples": 10, "seed": 1,
    },
    "/api/v1/retrieval": {"queries": [{"retrieved": ["d1"], "relevant": [{"id": "d1"}]}], "k": [1]},
}


# WHY (INVARIANT): the deployed service accepts the Thinkube API token as a
# bearer token and answers 200 with scores from each scoring route.
@pytest.mark.parametrize("path", list(BODIES))
def test_scoring_route_with_token_is_200(path):
    token = os.environ["THINKUBE_API_TOKEN"]
    res = httpx.post(
        f"{os.environ['TANDEM_LIVE_URL']}{path}",
        json=BODIES[path],
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    assert res.status_code == 200, res.text
    assert res.json()
