# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""The bearer-token check every scoring route goes through.

The token is checked by asking Thinkube Control's token verification, which
accepts a Keycloak token of the platform's realm or a Thinkube API token.
Nothing is kept: every request is checked with Control, no token and no
verification result outlives it.
"""

from fastapi import Depends, Header, HTTPException, Request
import httpx

VERIFY_PATH = "/api/v1/tokens/verify"

MISSING = (
    "A Thinkube token is required: send it as `Authorization: Bearer <token>`"
)


def _refuse(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"}
    )


def verify_with_control(
    control_url: str, authorization: str, client: httpx.Client
) -> bool:
    """True when Control accepts the token, False when it rejects it.

    The caller's Authorization header is forwarded unchanged. Raises a 503
    when Control cannot be reached or answers with a server error.
    """
    try:
        response = client.get(
            control_url + VERIFY_PATH, headers={"Authorization": authorization}
        )
    except httpx.HTTPError:
        raise _unchecked()
    if response.status_code >= 500:
        raise _unchecked()
    if response.status_code in (401, 403):
        return False
    return response.is_success


def _unchecked() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail="The token could not be checked: Thinkube Control is unavailable",
    )


def control_client():
    """A fresh HTTP client for one request's check with Control."""
    client = httpx.Client(timeout=10.0)
    try:
        yield client
    finally:
        client.close()


def require_thinkube_token(
    request: Request,
    authorization: str | None = Header(None),
    client: httpx.Client = Depends(control_client),
) -> None:
    """Refuses with 401 unless Control accepts the request's bearer token."""
    parts = (authorization or "").split(None, 1)
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1].strip():
        raise _refuse(MISSING)
    if not verify_with_control(request.app.state.control_url, authorization, client):
        raise _refuse(
            "Thinkube Control did not accept the token: send a valid Thinkube "
            "token as `Authorization: Bearer <token>`"
        )
