# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import json
import os
import sys

import httpx
from fastapi.testclient import TestClient


def _load():
    """The app with Control stood in for by a transport that accepts tokens."""
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app, score_text

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(200))
    )
    return app, score_text


HEADERS = {"Authorization": "Bearer good-token"}


# WHY (INVARIANT): the /api/v1/text route is served by score_text, the
# function whose refusals this file judges.
def test_text_route_is_served_by_score_text():
    app, score_text = _load()
    assert any(
        getattr(r, "path", None) == "/api/v1/text" and r.endpoint is score_text
        for r in app.routes
    )


# WHY (INVARIANT): /api/v1/text refuses an unknown metric with 422 naming it,
# and answers no metric at all, known ones in the same request included.
def test_text_refuses_unknown_metric_and_answers_none():
    app, _ = _load()
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/text",
            headers=HEADERS,
            json={
                "hypotheses": ["a"],
                "references": [["a"]],
                "metrics": ["bleu", "zorblax"],
            },
        )
    assert res.status_code == 422
    assert "zorblax" in json.dumps(res.json())
    body = res.json()
    assert not (isinstance(body, dict) and "metrics" in body)
    assert "bleu" not in body.get("metrics", {}) if isinstance(body, dict) and isinstance(body.get("metrics"), dict) else True
