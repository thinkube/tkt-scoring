# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import math
import os

import httpx


# WHY (INVARIANT): posting ranked ids, relevant ids (graded or not) and cut-offs
# answers recall@k, precision@k and nDCG@k for exactly those cut-offs, MRR for
# the set, and the number of queries scored.
def test_retrieval_scores_posted_queries():
    payload = {
        "queries": [
            {
                "retrieved": ["a", "b", "c", "d"],
                "relevant": [{"id": "a"}, {"id": "c"}],
            },
            {
                "retrieved": ["x", "y"],
                "relevant": [{"id": "y", "grade": 1}],
            },
        ],
        "k": [1, 2, 3],
    }

    res = httpx.post(
        f"{os.environ['TANDEM_LIVE_URL']}/api/v1/retrieval",
        json=payload,
        headers={"Authorization": f"Bearer {os.environ['THINKUBE_API_TOKEN']}"},
        timeout=30,
    )

    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2
    assert abs(body["mrr"] - 0.75) < 1e-6

    expected_recall = {"1": 0.25, "2": 0.75, "3": 1.0}
    expected_precision = {"1": 0.5, "2": 0.5, "3": 0.5}
    d2 = 1 / math.log2(3)
    expected_ndcg = {"1": 0.5, "2": (1 / (1 + d2) + d2) / 2}

    for name, expected in (
        ("recall_at_k", expected_recall),
        ("precision_at_k", expected_precision),
    ):
        got = {str(key): value for key, value in body[name].items()}
        assert set(got) == set(expected)
        for key, value in expected.items():
            assert abs(got[key] - value) < 1e-6

    ndcg = {str(key): value for key, value in body["ndcg_at_k"].items()}
    assert set(ndcg) == {"1", "2", "3"}
    for key, value in expected_ndcg.items():
        assert abs(ndcg[key] - value) < 1e-6
    assert 0.0 <= ndcg["3"] <= 1.0
    assert isinstance(body["definitions"], str) and body["definitions"]
