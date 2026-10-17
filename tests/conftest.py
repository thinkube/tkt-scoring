# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os
import sys
from pathlib import Path

import httpx
import pytest

# The tests import the service as `app`, from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# The service refuses to start without the address of Thinkube Control
# (THINKUBE_CONTROL_URL). Tests that need it unset delete it themselves.
CONTROL_URL = "http://control.test:8123"
os.environ.setdefault("THINKUBE_CONTROL_URL", CONTROL_URL)

# The bearer token the existing route tests send; the fake Control accepts it.
TEST_TOKEN = "Bearer test-token"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "anonymous: send no default Authorization header from TestClient",
    )


class FakeControl:
    """Stands in for Thinkube Control's token verification.

    Every request the service makes to Control is recorded in `calls`.
    `status` is the answer (default 200 = token accepted); `error`, when set,
    is raised instead, as an unreachable Control would.
    """

    def __init__(self):
        self.calls: list[httpx.Request] = []
        self.status = 200
        self.error: Exception | None = None

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        if self.error is not None:
            raise self.error
        return httpx.Response(self.status, json={})

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self._handle))


def _app_modules() -> dict:
    return {n: m for n, m in sys.modules.items() if n == "app" or n.startswith("app.")}


@pytest.fixture(autouse=True)
def keep_app_modules():
    """Puts back the app modules a test removed from sys.modules.

    Some tests import the service fresh by deleting its modules. Without this,
    the next test's `from app.main import app` would get a new app object,
    while test files that made a TestClient when they were loaded still hold
    the first one, and the fake Control would be set on the wrong app.
    """
    kept = _app_modules()
    yield
    for name in _app_modules():
        del sys.modules[name]
    sys.modules.update(kept)


@pytest.fixture(autouse=True)
def fake_control(request, monkeypatch, keep_app_modules):
    """Routes the token check to a fake Control and gives requests a token."""
    from starlette.testclient import TestClient

    from app.auth import control_client
    from app.main import app

    fake = FakeControl()
    app.dependency_overrides[control_client] = fake.client
    app.state.control_url = CONTROL_URL

    # The auth checks decide for themselves which header each request carries.
    is_auth_check = Path(str(request.node.fspath)).name.startswith("auth_AC-")
    if request.node.get_closest_marker("anonymous") is None and not is_auth_check:
        original = TestClient.request

        def request_with_token(self, method, url, **kwargs):
            if not any(
                k.lower() == "authorization"
                for k in {**dict(self.headers), **(kwargs.get("headers") or {})}
            ):
                kwargs["headers"] = {
                    **(kwargs.get("headers") or {}),
                    "Authorization": TEST_TOKEN,
                }
            return original(self, method, url, **kwargs)

        monkeypatch.setattr(TestClient, "request", request_with_token)

    yield fake
    app.dependency_overrides.pop(control_client, None)
