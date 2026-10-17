# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

"""SQuAD-style answer scoring: exact match and token F1.

One place normalises answers and computes exact match and token F1 so
every caller compares predictions to accepted answers the same way.
"""

import re
import string
from collections.abc import Sequence

NORMALISATION = (
    "lowercases the text, deletes punctuation without leaving a space, "
    "removes the articles a, an and the, and collapses whitespace into "
    "single spaces"
)

_ARTICLES_RE = re.compile(r"\b(a|an|the)\b")
_WHITESPACE_RE = re.compile(r"\s+")
_PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def normalise_answer(text: str) -> str:
    """Normalises an answer the way SQuAD scoring compares answers.

    Lowercases the text, deletes punctuation without leaving a space,
    removes the articles a, an and the, and collapses runs of whitespace into single spaces.
    """
    lowered = text.lower()
    # Punctuation is deleted outright, as in SQuAD's script, so a
    # hyphen joins the words it sits between ("Eiffel-Tower" -> "eiffeltower").
    no_punctuation = lowered.translate(_PUNCTUATION_TABLE)
    no_articles = _ARTICLES_RE.sub(" ", no_punctuation)
    return _WHITESPACE_RE.sub(" ", no_articles).strip()


def exact_match(prediction: str, answers: Sequence[str]) -> float:
    """Scores 1 when the normalised prediction equals a normalised answer.

    Scores 0 when it equals none of the accepted answers.
    """
    normalised_prediction = normalise_answer(prediction)
    return float(
        any(normalised_prediction == normalise_answer(answer) for answer in answers)
    )


def _token_f1(prediction_tokens: list[str], answer_tokens: list[str]) -> float:
    if not prediction_tokens and not answer_tokens:
        return 1.0
    if not prediction_tokens or not answer_tokens:
        return 0.0

    common = {}
    for token in prediction_tokens:
        common[token] = min(
            prediction_tokens.count(token), answer_tokens.count(token)
        )
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0

    precision = num_same / len(prediction_tokens)
    recall = num_same / len(answer_tokens)
    return 2 * precision * recall / (precision + recall)


def token_f1(prediction: str, answers: Sequence[str]) -> float:
    """Token F1 of a prediction against its best-scoring accepted answer.

    The harmonic mean of precision and recall over normalised tokens,
    taken against whichever accepted answer scores highest.
    """
    prediction_tokens = normalise_answer(prediction).split()
    best = 0.0
    for answer in answers:
        answer_tokens = normalise_answer(answer).split()
        best = max(best, _token_f1(prediction_tokens, answer_tokens))
    return best


def score_answers(items: Sequence[tuple[str, Sequence[str]]]) -> dict:
    """Scores a set of (prediction, accepted answers) pairs.

    Returns the set's mean exact match and mean token F1, each on the
    0-100 scale SQuAD reports, and the number of predictions scored.
    """
    exact_matches = [exact_match(prediction, answers) for prediction, answers in items]
    token_f1s = [token_f1(prediction, answers) for prediction, answers in items]
    count = len(items)
    return {
        "exact_match": sum(exact_matches) / count * 100,
        "token_f1": sum(token_f1s) / count * 100,
        "count": count,
    }
