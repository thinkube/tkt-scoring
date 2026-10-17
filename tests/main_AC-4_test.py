# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json

import httpx
import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.auth import control_client

BEARER = {"Authorization": "Bearer tk-abc.123"}


@pytest.fixture
def client(monkeypatch):
    # Control stand-in: accepts every token. httpx.Client is what the
    # production path calls (get), so a real client over a mock transport
    # implements every method.
    main.app.state.control_url = "http://control.test"
    main.app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={}))
    )
    yield TestClient(main.app)
    main.app.dependency_overrides.pop(control_client, None)


def _spy_scorers(monkeypatch):
    calls = []

    def spy(*args, **kwargs):
        calls.append(args)
        return 50.0, "spy"

    monkeypatch.setattr(main, "score_sacrebleu", spy)
    monkeypatch.setattr(main, "score_rouge", spy)
    return calls


# WHY (INVARIANT): /api/v1/text refuses an empty reference group with 422,
# naming its position counting from 0, and computes no score.
@pytest.mark.parametrize("metric", ["bleu", "rouge1"])
def test_text_refuses_empty_reference_group_naming_position(
    client, monkeypatch, metric
):
    calls = _spy_scorers(monkeypatch)
    res = client.post(
        "/api/v1/text",
        headers=BEARER,
        json={
            "hypotheses": ["a", "b", "c", "d"],
            "references": [["a"], ["b"], [], ["d"]],
            "metrics": [metric],
        },
    )
    assert res.status_code == 422
    assert "2" in json.dumps(res.json())
    assert "metrics" not in res.json()
    assert calls == []


# WHY (INVARIANT): the position is counted from 0, so an empty first group
# is named as position 0.
def test_text_names_position_zero_for_first_group(client, monkeypatch):
    calls = _spy_scorers(monkeypatch)
    res = client.post(
        "/api/v1/text",
        headers=BEARER,
        json={
            "hypotheses": ["a", "b"],
            "references": [[], ["b"]],
            "metrics": ["bleu"],
        },
    )
    assert res.status_code == 422
    assert "0" in json.dumps(res.json())
    assert calls == []
