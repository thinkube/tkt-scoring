# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import importlib
import sys

import pytest
from fastapi.testclient import TestClient


def _fresh_app():
    for name in [n for n in sys.modules if n == "app.main" or n == "app.settings"]:
        del sys.modules[name]
    return importlib.import_module("app.main").app


# WHY (INVARIANT): a service that does not know where Control is must fail at
# start, before answering anything, and the error must name the setting.
def test_starting_without_the_setting_fails_naming_it(monkeypatch):
    monkeypatch.delenv("THINKUBE_CONTROL_URL", raising=False)
    app = _fresh_app()
    with pytest.raises(Exception) as caught:
        with TestClient(app) as client:
            client.get("/health")
    assert "THINKUBE_CONTROL_URL" in str(caught.value)
