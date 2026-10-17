# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import pytest

from app.settings import control_url


# WHY (INVARIANT): the service must never run without knowing where Thinkube
# Control is, and the refusal must say which setting to give and what it is.
@pytest.mark.parametrize("environ", [{}, {"THINKUBE_CONTROL_URL": ""}, {"THINKUBE_CONTROL_URL": "   \t "}])
def test_missing_empty_or_blank_setting_is_refused_naming_it(environ):
    with pytest.raises(Exception) as caught:
        control_url(environ)
    message = str(caught.value)
    assert "THINKUBE_CONTROL_URL" in message
    assert "address of thinkube control" in message.lower()


# WHY (INVARIANT): the refusal must also stop the app itself from starting
# when the setting is empty, not only the bare reader.
def test_app_refuses_to_start_when_the_setting_is_blank(monkeypatch):
    import importlib
    import sys

    from fastapi.testclient import TestClient

    monkeypatch.setenv("THINKUBE_CONTROL_URL", "   ")
    for name in [n for n in sys.modules if n in ("app.main", "app.settings")]:
        del sys.modules[name]
    app = importlib.import_module("app.main").app
    with pytest.raises(Exception) as caught:
        with TestClient(app):
            pass
    assert "THINKUBE_CONTROL_URL" in str(caught.value)
