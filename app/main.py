# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""The scoring service: scores AI system outputs against references."""

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.auth import require_thinkube_token
from app.answers import NORMALISATION, score_answers
from app.classification import score_classification
from app.compare import compare_systems
from app.rouge_metrics import ROUGE_METRICS, score_rouge
from app.retrieval import DEFINITIONS, score_retrieval
from app.sacrebleu_metrics import SACREBLEU_METRICS, score_sacrebleu
from app.settings import control_url

TEXT_METRICS = SACREBLEU_METRICS | ROUGE_METRICS



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Refuses to start without THINKUBE_CONTROL_URL."""
    app.state.control_url = control_url(os.environ)
    yield


app = FastAPI(title="Thinkube scoring", lifespan=lifespan)

# Every route but /health carries this; the documentation stays open.
AUTH = [Depends(require_thinkube_token)]


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


@app.post("/api/v1/text", dependencies=AUTH)
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


class AnswersItem(BaseModel):
    prediction: str
    answers: list[str]


class AnswersRequest(BaseModel):
    items: list[AnswersItem]


class AnswersResponse(BaseModel):
    exact_match: float
    token_f1: float
    count: int
    normalisation: str


@app.post("/api/v1/answers", dependencies=AUTH)
def score_answers_route(payload: AnswersRequest) -> AnswersResponse:
    """Scores a set of predictions against their accepted answers.

    Each item pairs a prediction with the answers accepted for it.
    Answers with the set's exact match and token F1, on the 0-100
    scale SQuAD reports, the number of predictions scored, and the
    normalisation that was applied.
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="items must not be empty")

    scores = score_answers(
        [(item.prediction, item.answers) for item in payload.items]
    )

    return AnswersResponse(
        exact_match=scores["exact_match"],
        token_f1=scores["token_f1"],
        count=scores["count"],
        normalisation=NORMALISATION,
    )


class ClassificationRequest(BaseModel):
    # Absent fields default to empty so the route can refuse them in one
    # message that says what to send.
    predicted: list[str] = []
    true_labels: list[str] = []


class LabelScore(BaseModel):
    precision: float
    recall: float
    f1: float


class ClassificationResponse(BaseModel):
    accuracy: float
    per_label: dict[str, LabelScore]
    macro: LabelScore
    micro: LabelScore
    labels: list[str]
    confusion_matrix: list[list[int]]
    statement: str


@app.post("/api/v1/classification", dependencies=AUTH)
def score_classification_route(
    payload: ClassificationRequest,
) -> ClassificationResponse:
    """Scores predicted labels against true labels.

    Answers accuracy, per-label precision, recall and F1, their macro and
    micro averages, and the confusion matrix with the label order it is
    written in. Nothing of the request is kept.
    """
    if not payload.predicted or not payload.true_labels:
        raise HTTPException(
            status_code=400,
            detail=(
                "predicted and true_labels are both required (true labels "
                "are sent as 'true_labels'); each must be a non-empty list "
                "of the same length"
            ),
        )

    try:
        scores = score_classification(payload.predicted, payload.true_labels)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return ClassificationResponse(**scores)


class CompareRequest(BaseModel):
    hypotheses_a: list[str] = []
    hypotheses_b: list[str] = []
    references: list[list[str]] = []
    metric: str
    # Any, so a bad sample count is refused with a 400 that says what to send.
    samples: Any
    seed: int = 0


class IntervalScore(BaseModel):
    score: float
    lower: float
    upper: float


class CompareResponse(BaseModel):
    metric: str
    samples: int
    seed: int
    system_a: IntervalScore
    system_b: IntervalScore
    difference: IntervalScore
    share_a_beats_b: float
    significant: bool
    provenance: str
    method: str


@app.post("/api/v1/compare", dependencies=AUTH)
def compare_route(payload: CompareRequest) -> CompareResponse:
    """Compares two systems on one metric by paired bootstrap.

    Answers each system's score with its 95% interval, the difference
    (first minus second) with its interval, the share of samples in which
    the first beats the second, the significance, the provenance of the
    metric and the method. Nothing of the request is kept.
    """
    try:
        result = compare_systems(
            payload.metric,
            payload.hypotheses_a,
            payload.hypotheses_b,
            payload.references,
            payload.samples,
            payload.seed,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return CompareResponse(**result)


class RelevantId(BaseModel):
    id: str
    grade: float = 1.0


class RetrievalQuery(BaseModel):
    retrieved: list[str]
    relevant: list[RelevantId]


class RetrievalRequest(BaseModel):
    queries: list[RetrievalQuery]
    k: list[int]


class RetrievalResponse(BaseModel):
    recall_at_k: dict[int, float]
    precision_at_k: dict[int, float]
    ndcg_at_k: dict[int, float]
    mrr: float
    count: int
    definitions: str


@app.post("/api/v1/retrieval", dependencies=AUTH)
def score_retrieval_route(payload: RetrievalRequest) -> RetrievalResponse:
    """Scores ranked ids against relevant ids, per query, averaged.

    Answers recall@k, precision@k and nDCG@k for each cut-off asked, MRR,
    the number of queries scored and the definitions used. Nothing of the
    request is kept.
    """
    if not payload.queries:
        raise HTTPException(
            status_code=400,
            detail="queries must not be empty: send at least one query",
        )
    if not payload.k:
        raise HTTPException(
            status_code=400,
            detail="k must not be empty: send at least one cut-off",
        )

    try:
        scores = score_retrieval(
            [
                (query.retrieved, {r.id: r.grade for r in query.relevant})
                for query in payload.queries
            ],
            payload.k,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return RetrievalResponse(**scores, definitions=DEFINITIONS)
