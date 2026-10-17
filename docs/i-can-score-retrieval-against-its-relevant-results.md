# I can score retrieval against its relevant results

Send `POST /api/v1/retrieval` the ranked ids your system returned for each
query, the ids that were relevant, and the cut-offs you want. It answers
recall@k, precision@k, nDCG@k and MRR, averaged over your queries.

## Request

Send your Thinkube token with it, as `Authorization: Bearer <token>` (a
Keycloak token of the platform's realm or a Thinkube API token). Without
one the service answers 401.

```json
{
  "queries": [
    {
      "retrieved": ["a", "x", "b"],
      "relevant": [{"id": "a", "grade": 3}, {"id": "b"}]
    }
  ],
  "k": [1, 3]
}
```

- `queries`: one entry per query.
  - `retrieved`: the ids your system returned, best first.
  - `relevant`: the relevant ids. Each is `{"id": "..."}` with an optional
    `grade`. A grade is a number from 0 upward; an id without a grade counts
    as grade 1.
- `k`: the cut-offs wanted, each a positive whole number.

## Response

```json
{
  "recall_at_k": {"1": 0.5, "3": 1.0},
  "precision_at_k": {"1": 1.0, "3": 0.6666666666666666},
  "ndcg_at_k": {"1": 1.0, "3": 0.96394},
  "mrr": 1.0,
  "count": 1,
  "definitions": "..."
}
```

- `recall_at_k`, `precision_at_k`, `ndcg_at_k`: one number for each cut-off
  you asked for, keyed by that cut-off (as a string in JSON), and no other.
- `mrr`: the mean reciprocal rank over the queries.
- `count`: the number of queries scored.
- `definitions`: the definitions used, in words.

All four numbers are on a 0 to 1 scale; 1 is best.

- **Relevant** means present in the query's `relevant` list; the grade never
  changes that.
- **recall@k**: the share of the query's relevant ids found in the first k
  ranked ids.
- **precision@k**: relevant ids in the first k, divided by k itself, so
  returning fewer than k ids does not raise the score.
- **MRR**: 1 divided by the 1-based rank of the first relevant id; 0 when
  none is in the list.
- **nDCG@k**: the grade is the gain, discounted at rank r by 1/log2(r+1),
  divided by the best possible ordering of the query's relevant ids, so a
  list in grade order scores 1.

## What it refuses

A refusal is a 422 whose message names what to fix, and no number comes back:
no `queries`; no `k`; a query with no relevant ids (named by its position,
counting from 0); a cut-off that is not a positive whole number (named); a
ranked list that repeats an id (named); a negative grade. It never invents a
number, and keeps nothing of your request.
