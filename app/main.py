# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""The scoring service: scores AI system outputs against references."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.rouge_metrics import ROUGE_METRICS, score_rouge
from app.sacrebleu_metrics import SACREBLEU_METRICS, score_sacrebleu

TEXT_METRICS = SACREBLEU_METRICS | ROUGE_METRICS

app = FastAPI(title="Thinkube scoring")


@app.get("/health")
def health() -> dict:
    """Answers when the service is up; the platform's health check calls it."""
    return {"status": "ok"}


class TextScoreRequest(BaseModel):
    hypotheses: list[str]
    references: list[list[str]]
    metrics: list[str]


class MetricScore(BaseModel):
    score: float
    provenance: str


class TextScoreResponse(BaseModel):
    metrics: dict[str, MetricScore]


@app.post("/api/v1/text")
def score_text(request: TextScoreRequest) -> TextScoreResponse:
    """Scores a corpus of hypotheses against their references.

    `references[i]` is the list of references for `hypotheses[i]`, of
    length one when there is a single reference. Answers one corpus score
    per metric asked, each paired with what produced it.
    """
    if not request.hypotheses:
        raise HTTPException(status_code=400, detail="hypotheses must not be empty")

    if len(request.references) != len(request.hypotheses):
        raise HTTPException(
            status_code=400,
            detail=(
                "the number of reference groups "
                f"({len(request.references)}) must match the number of "
                f"hypotheses ({len(request.hypotheses)})"
            ),
        )

    unknown = [name for name in request.metrics if name not in TEXT_METRICS]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"unknown metric(s) requested: {', '.join(unknown)}",
        )

    scores: dict[str, MetricScore] = {}
    for name in request.metrics:
        if name in SACREBLEU_METRICS:
            value, provenance = score_sacrebleu(
                name, request.hypotheses, request.references
            )
        else:
            value, provenance = score_rouge(
                name, request.hypotheses, request.references
            )
        scores[name] = MetricScore(score=value, provenance=provenance)

    return TextScoreResponse(metrics=scores)
