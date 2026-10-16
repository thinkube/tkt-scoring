# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi.testclient import TestClient

from app.main import app


def test_health_answers_ok():
    res = TestClient(app).get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
