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
        "hypotheses_a": ["a cat"], "hypotheses_b": ["the cat"],
        "references": [["a cat"]], "metric": "bleu", "samples": 10, "seed": 1,
    },
    "/api/v1/retrieval": {"queries": [{"retrieved": ["d1"], "relevant": [{"id": "d1"}]}], "k": [1]},
}


# WHY (INVARIANT): the deployed service refuses a scoring request that carries
# no Authorization header with 401.
@pytest.mark.parametrize("path", list(BODIES))
def test_scoring_route_without_token_is_401(path):
    res = httpx.post(f"{os.environ['TANDEM_LIVE_URL']}{path}", json=BODIES[path], timeout=30)
    assert res.status_code == 401
