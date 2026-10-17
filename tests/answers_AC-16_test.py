# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

from fastapi.testclient import TestClient

from app.main import app


def _post(prediction, answers):
    payload = {"items": [{"prediction": prediction, "answers": answers}]}
    return TestClient(app).post("/api/v1/answers", json=payload)


# WHY (INVARIANT): through the route, the prediction "The  Eiffel-Tower!"
# against accepted answer "eiffeltower" answers exact_match 100.
def test_route_scores_punctuation_deleted_match_as_100():
    res = _post("The  Eiffel-Tower!", ["eiffeltower"])
    assert res.status_code == 200
    assert res.json()["exact_match"] == 100


# WHY (TRANSITION): the normalisation statement returned with the scores says
# punctuation is deleted without leaving a space - done once it ships - and
# still names lowercasing, article removal and whitespace collapsing.
def test_route_statement_says_punctuation_is_deleted():
    res = _post("x", ["x"])
    assert res.status_code == 200
    statement = res.json()["normalisation"].lower()
    assert "punctuation" in statement
    assert "delet" in statement
    assert "space" in statement
    assert "lowercase" in statement
    assert "article" in statement
    assert "whitespace" in statement


# WHY (TRANSITION): the route returns exactly the module's NORMALISATION
# statement, and that statement says punctuation is deleted - done once shipped.
def test_route_returns_the_module_statement_which_says_deleted():
    from app.answers import NORMALISATION

    assert "delet" in NORMALISATION.lower()
    res = _post("x", ["x"])
    assert res.json()["normalisation"] == NORMALISATION


# WHY (TRANSITION): the README's example carries the new statement and says
# punctuation is deleted - done once the README ships.
def test_readme_example_carries_the_new_statement():
    from pathlib import Path

    from app.answers import NORMALISATION

    readme = (Path(__file__).resolve().parent.parent / "README.md").read_text()
    assert NORMALISATION in readme
    assert "delet" in readme.lower()


# WHY (TRANSITION): a page documenting POST /api/v1/answers exists - done once
# the page ships.
def test_docs_page_exists():
    from pathlib import Path

    page = Path(__file__).resolve().parent.parent / "docs" / "post-api-v1-answers.md"
    assert page.is_file()
    assert "/api/v1/answers" in page.read_text()
