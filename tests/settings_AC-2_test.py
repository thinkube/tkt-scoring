# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from app.settings import control_url


# WHY (INVARIANT): the address is used to build paths on Control, so a trailing
# slash must never survive the reader.
def test_trailing_slash_is_removed():
    assert control_url({"THINKUBE_CONTROL_URL": "https://control.example.org/"}) == "https://control.example.org"
    assert control_url({"THINKUBE_CONTROL_URL": "https://control.example.org"}) == "https://control.example.org"


# WHY (INVARIANT): the app must hand paths to Control built from the cleaned
# address, so starting with a slash-ended value must still succeed.
def test_app_starts_with_a_trailing_slash_address(monkeypatch):
    import importlib
    import sys

    from fastapi.testclient import TestClient

    monkeypatch.setenv("THINKUBE_CONTROL_URL", "https://control.example.org/")
    for name in [n for n in sys.modules if n in ("app.main", "app.settings")]:
        del sys.modules[name]
    app = importlib.import_module("app.main").app
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
