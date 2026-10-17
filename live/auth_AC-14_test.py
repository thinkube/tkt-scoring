# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import os

import httpx
import pytest


# WHY (INVARIANT): the deployed service keeps /health and /docs open - 200
# without any token.
@pytest.mark.parametrize("path", ["/health", "/docs"])
def test_open_paths_answer_without_token(path):
    res = httpx.get(f"{os.environ['TANDEM_LIVE_URL']}{path}", timeout=30)
    assert res.status_code == 200
