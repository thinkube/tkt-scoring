# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""The service's settings, read from the environment at startup."""

from typing import Mapping


def control_url(environ: Mapping[str, str]) -> str:
    """The address of Thinkube Control, without a trailing slash.

    Refuses when THINKUBE_CONTROL_URL is missing, empty or only whitespace.
    """
    value = (environ.get("THINKUBE_CONTROL_URL") or "").strip()
    if not value:
        raise ValueError(
            "THINKUBE_CONTROL_URL is not set: give the address of Thinkube "
            "Control, such as https://control.<domain>"
        )
    return value.rstrip("/")
