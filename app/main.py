# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""The scoring service: scores AI system outputs against references."""

from fastapi import FastAPI

app = FastAPI(title="Thinkube scoring")


@app.get("/health")
def health() -> dict:
    """Answers when the service is up; the platform's health check calls it."""
    return {"status": "ok"}
