# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import importlib
import sys

from fastapi.testclient import TestClient


# WHY (INVARIANT): with the setting given, the service starts and its health
# check answers ok.
def test_starting_with_the_setting_succeeds_and_health_answers(monkeypatch):
    monkeypatch.setenv("THINKUBE_CONTROL_URL", "https://control.example.org")
    for name in [n for n in sys.modules if n == "app.main" or n == "app.settings"]:
        del sys.modules[name]
    app = importlib.import_module("app.main").app
    with TestClient(app) as client:
        res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
