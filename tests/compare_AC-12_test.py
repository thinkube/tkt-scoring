# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.compare import METHOD, compare_systems
from app.main import app

client = TestClient(app)


# WHY (INVARIANT): a reader of the response alone knows how it was computed:
# the route returns the module's METHOD unchanged plus the metric's provenance.
def test_route_returns_method_and_provenance():
    a, b = ["the cat sat", "a dog"], ["a cat", "zzz"]
    refs = [["the cat sat"], ["a dog"]]
    res = client.post(
        "/api/v1/compare",
        json={"hypotheses_a": a, "hypotheses_b": b, "references": refs,
              "metric": "rouge1", "samples": 30, "seed": 1},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["method"] == METHOD
    assert body["provenance"] == compare_systems("rouge1", a, b, refs, 30, 1)["provenance"]
    assert body["provenance"] != ""
