# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx


# WHY (TRANSITION): proves the deployed service was started with
# THINKUBE_CONTROL_URL filled in from the declared setting: it is running and
# its health check passes. Its job is done once the setting ships.
def test_deployed_service_is_up_and_healthy():
    res = httpx.get(f"{os.environ['TANDEM_LIVE_URL']}/health", timeout=30)
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
