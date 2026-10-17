# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys

import httpx
import pytest
from fastapi.testclient import TestClient

import app.auth  # noqa: F401  (the cut under test; each test reloads it fresh)
import app.main  # noqa: F401


# WHY (INVARIANT): the API's own documentation stays readable without a token.
@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_documentation_is_open(path):
    os.environ["THINKUBE_CONTROL_URL"] = "http://control.test"
    for name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
        del sys.modules[name]
    from app.auth import control_client
    from app.main import app

    app.dependency_overrides[control_client] = lambda: httpx.Client(
        transport=httpx.MockTransport(lambda req: httpx.Response(401))
    )
    with TestClient(app) as client:
        assert client.get(path).status_code == 200
