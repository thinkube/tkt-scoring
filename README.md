# tkt-scoring

A Thinkube optional component: a CPU service that scores the outputs of AI
systems against references. Every measurement on Thinkube goes through it, so
every measurement uses one implementation, and two numbers from two projects
can be compared.

The service answers `GET /health`, scores written output through
`POST /api/v1/text`, scores predicted answers against accepted answers
through `POST /api/v1/answers`, scores a classifier through
`POST /api/v1/classification`, scores retrieval through
`POST /api/v1/retrieval`, and compares two systems through
`POST /api/v1/compare`. Each route below has a worked example: the request
as you would send it and the answer the service gives to it. The examples
use `https://scoring.<domain>` and `<token>` for your own address and token.

Every route except `/health` and the API documentation (`/docs`, `/redoc`,
`/openapi.json`) requires an `Authorization: Bearer <token>` header carrying
a token Thinkube accepts: a Keycloak token of the platform's realm or a
Thinkube API token. The service checks each token with Thinkube Control on
every request and keeps nothing. It answers 401 without a valid token, and
503 when Control cannot be asked.

### Example: GET /health

Open, no token needed. Answers 200:

```bash
curl https://scoring.<domain>/health
```

```json
{"status": "ok"}
```

`POST /api/v1/text` takes `hypotheses` (the outputs to score), `references`
(one list of accepted references per hypothesis, of length one when there
is a single reference) and `metrics` (the metric keys wanted). It answers,
for each metric asked, that metric's corpus score and what produced it —
the sacreBLEU signature for a sacreBLEU metric, the ROUGE implementation
and version for a ROUGE metric. The metric keys a caller may ask for are
exactly: `bleu`, `chrf`, `chrf++`, `ter`, `rouge1`, `rouge2`, `rougeL`.

### Example: POST /api/v1/text

Request:

```bash
curl -X POST https://scoring.<domain>/api/v1/text \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"hypotheses": ["the cat sat on the mat", "a dog barked loudly"], "references": [["the cat sat on the mat"], ["the dog barked loudly"]], "metrics": ["bleu", "chrf", "ter", "rouge1"]}'
```

Answer (200):

```json
{
  "metrics": {
    "bleu": {
      "score": 83.75922397086269,
      "provenance": "nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0"
    },
    "chrf": {
      "score": 91.09746144895593,
      "provenance": "nrefs:1|case:mixed|eff:yes|nc:6|nw:0|space:no|version:2.6.0"
    },
    "ter": {
      "score": 10.0,
      "provenance": "nrefs:1|case:lc|tok:tercom|norm:no|punct:yes|asian:no|version:2.6.0"
    },
    "rouge1": {
      "score": 87.5,
      "provenance": "rouge-score 0.1.2"
    }
  }
}
```

`POST /api/v1/answers` takes `items`, a list of predictions each paired
with its accepted answers (`{"prediction": "...", "answers": ["...", ...]}`).
It answers the set's exact match and token F1 — on the 0-100 scale SQuAD
reports — the number of predictions scored, and the normalisation that was
applied before comparing: lowercasing, removing punctuation, removing the
articles a, an and the, and collapsing whitespace, exactly as SQuAD
computes it. Every refusal on these routes is a 422 with a message naming the
problem: for text, an empty `metrics` list, an empty reference group or an
unknown metric; for answers, no items or an item with no accepted answers.

### Example: POST /api/v1/answers

Request:

```bash
curl -X POST https://scoring.<domain>/api/v1/answers \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"items": [{"prediction": "The Eiffel Tower", "answers": ["Eiffel Tower", "the Eiffel tower in Paris"]}, {"prediction": "in 1889", "answers": ["1889"]}]}'
```

Answer (200):

```json
{
  "exact_match": 50.0,
  "token_f1": 83.33333333333333,
  "count": 2,
  "normalisation": "lowercases the text, removes punctuation, removes the articles a, an and the, and collapses whitespace into single spaces"
}
```

`POST /api/v1/classification` takes `predicted` (the labels a classifier
gave) and `true_labels` (the labels it should have given, in the same
order); both must be non-empty lists of the same length. It answers
`accuracy`, the `per_label` precision, recall and F1, the `macro` and
`micro` averages of those three, the `confusion_matrix` (rows are the true
label, columns the predicted label) with the `labels` order it is written
in, and a `statement` of the definitions used. It refuses lists of
different lengths, naming both counts, and never invents a number.

### Example: POST /api/v1/classification

Request:

```bash
curl -X POST https://scoring.<domain>/api/v1/classification \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"predicted": ["spam", "ham", "spam", "ham"], "true_labels": ["spam", "ham", "ham", "ham"]}'
```

Answer (200):

```json
{
  "accuracy": 0.75,
  "per_label": {
    "ham": {
      "precision": 1.0,
      "recall": 0.6666666666666666,
      "f1": 0.8
    },
    "spam": {
      "precision": 0.5,
      "recall": 1.0,
      "f1": 0.6666666666666666
    }
  },
  "macro": {
    "precision": 0.75,
    "recall": 0.8333333333333333,
    "f1": 0.7333333333333334
  },
  "micro": {
    "precision": 0.75,
    "recall": 0.75,
    "f1": 0.75
  },
  "labels": [
    "ham",
    "spam"
  ],
  "confusion_matrix": [
    [
      2,
      1
    ],
    [
      0,
      1
    ]
  ],
  "statement": "Accuracy is the share of positions where the predicted label equals the true label. Per-label precision is TP / (TP + FP), recall is TP / (TP + FN), and F1 is their harmonic mean, treating that label as the positive class and every other label as the negative class; a value whose denominator is zero is 0.0. Macro average is the unweighted mean of the per-label values. Micro average is computed from the pooled true/false positive and false negative counts across all labels. The confusion matrix has one row per true label and one column per predicted label, in the order given by labels."
}
```

`POST /api/v1/retrieval` takes `queries`, each with `retrieved` (the ranked
ids a system returned) and `relevant` (a list of `{"id": "...", "grade": 2}`,
`grade` optional and 1 when left out), and `k`, the cut-offs wanted. It
answers `recall_at_k`, `precision_at_k` and `ndcg_at_k` (each keyed by the
cut-off) and `mrr`, all on a 0 to 1 scale and averaged over the queries,
with the `count` of queries scored and the `definitions` used. It refuses no
queries, no cut-offs, a query with no relevant ids, a cut-off that is not a
positive whole number, and a ranked list that repeats an id, naming the
offender, and never invents a number. See
[the how-to](docs/i-can-score-retrieval-against-its-relevant-results.md).

### Example: POST /api/v1/retrieval

Request:

```bash
curl -X POST https://scoring.<domain>/api/v1/retrieval \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"queries": [{"retrieved": ["d3", "d1", "d7"], "relevant": [{"id": "d1", "grade": 2}, {"id": "d9"}]}, {"retrieved": ["d2", "d4"], "relevant": [{"id": "d2"}]}], "k": [1, 3]}'
```

Answer (200):

```json
{
  "recall_at_k": {
    "1": 0.5,
    "3": 0.75
  },
  "precision_at_k": {
    "1": 0.5,
    "3": 0.3333333333333333
  },
  "ndcg_at_k": {
    "1": 0.5,
    "3": 0.7398124665681315
  },
  "mrr": 0.75,
  "count": 2,
  "definitions": "A ranked id is relevant when it is present in the query's relevant ids; presence alone decides relevance, and a grade never changes it. Grades are numbers on a scale from 0 upward; a relevant id posted without a grade (ungraded) defaults to grade 1. recall@k is the mean over queries of the share of the query's relevant ids that appear among its first k ranked ids. precision@k is the mean over queries of the relevant ids among the first k ranked ids divided by k itself, so a query that returned fewer than k ids is not rewarded for it. MRR is the mean over queries of 1 divided by the 1-based rank of the first relevant id; a query with no relevant id in its ranked list contributes 0. nDCG@k uses the grade as the gain, discounted at 1-based rank r by 1/log2(r+1); DCG@k sums gain x discount over the first k ranked ids (an id that is not relevant has gain 0) and is divided by the ideal DCG@k, the same sum over the query's relevant grades in descending order, so a query ranked in grade order scores 1; nDCG@k is the mean over queries (a query whose ideal DCG is 0 contributes 0). All four numbers are on a 0 to 1 scale."
}
```

`POST /api/v1/compare` takes `hypotheses_a` and `hypotheses_b` (the two
systems' outputs on the same items), `references` (one list per item), one
`metric` key, `samples` (the number of bootstrap samples) and a required
`seed` (a whole number; a request without one is refused). It
answers `system_a` and `system_b`, each a `score` with its 95% interval
(`lower`, `upper`), the `difference` (first minus second) with its interval,
`share_a_beats_b` (the share of samples in which the first system beats the
second; for `ter` beating means a lower score), `significant` (true only
when the difference interval excludes zero), the `provenance` of the metric
and the `method`. The metric keys accepted are exactly: `bleu`, `chrf`,
`chrf++`, `ter`, `rouge1`, `rouge2`, `rougeL`, `exact_match`, `token_f1`. It
refuses bad requests with 422 and a message saying what to send. A
difference whose interval includes zero is not a gain. See
[the how-to](docs/i-can-compare-two-systems-and-see-whether-the-difference-is-real.md).

### Example: POST /api/v1/compare

Request:

```bash
curl -X POST https://scoring.<domain>/api/v1/compare \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"hypotheses_a": ["the cat sat on the mat", "a dog barked loudly", "it rains today", "we like tea"], "hypotheses_b": ["cat the on sat mat", "a dog barked", "rain today", "we like coffee"], "references": [["the cat sat on the mat"], ["a dog barked loudly"], ["it rains today"], ["we like tea"]], "metric": "chrf", "samples": 1000, "seed": 42}'
```

Answer (200):

```json
{
  "metric": "chrf",
  "samples": 1000,
  "seed": 42,
  "system_a": {
    "score": 100.0,
    "lower": 100.0,
    "upper": 100.0
  },
  "system_b": {
    "score": 43.710610183449155,
    "lower": 31.14788575610724,
    "upper": 56.83748254659833
  },
  "difference": {
    "score": 56.289389816550845,
    "lower": 43.16251745340167,
    "upper": 68.85211424389276
  },
  "share_a_beats_b": 1.0,
  "significant": true,
  "provenance": "nrefs:1|case:mixed|eff:yes|nc:6|nw:0|space:no|version:2.6.0",
  "method": "Paired bootstrap. Both systems are scored on the same resampled items in every sample (paired resampling): each sample draws the items with replacement, from the seed, and the same drawn items, with their references, score both systems. Each system's score is its score on the full set, on the metric's own scale; the difference is the first system's score minus the second's. The intervals are 95% percentile intervals, with bounds at the 2.5th and 97.5th percentiles of the samples. The first system 'beats' the second in a sample only when its score is strictly higher, or strictly lower for ter, where lower is better; ties are not counted as beats. The share is the samples in which it beats the second divided by the number of samples. The result is significant only when the difference interval excludes zero."
}
```

## Version 1

- **Translation and generation text:** BLEU, chrF, chrF++ and TER through
  sacreBLEU 2.6.0, each returned with its sacreBLEU signature; ROUGE-1,
  ROUGE-2 and ROUGE-L, each returned with the ROUGE implementation and
  version that produced it.
- **Answers and extraction:** exact match and token F1, through
  `POST /api/v1/answers`.
- **Classification:** accuracy; precision, recall and F1, macro and micro;
  the confusion matrix, through `POST /api/v1/classification`.
- **Retrieval:** recall@k, precision@k, MRR and nDCG@k, through
  `POST /api/v1/retrieval`.
- **Comparing two systems:** paired bootstrap for any text or answers
  metric, through `POST /api/v1/compare`, with 95% intervals and
  significance. A difference whose interval includes zero is not a gain.

### Which metric for which kind of AI output

- **Translation:** `bleu`, `chrf`, `chrf++` and `ter` through
  `POST /api/v1/text`. Use `chrf` or `chrf++` for morphologically rich
  languages, where one word has many forms and character overlap is fairer
  than whole-word overlap. `ter` is edit distance: the edits needed to turn
  the output into the reference, so lower is better.
- **Generated or summarised text:** `rouge1`, `rouge2` and `rougeL` through
  `POST /api/v1/text`. ROUGE is the usual metric for summaries: it measures
  how much of the reference's words, word pairs and longest common
  sequence the output covers.
- **Short extracted answers:** `exact_match` and `token_f1` through
  `POST /api/v1/answers`. For extractive QA, exact match says whether the
  answer is right as written and token F1 gives credit for partial overlap.
- **Classifier labels:** accuracy, precision, recall, F1 and the confusion
  matrix through `POST /api/v1/classification`, because labels are
  compared for equality, not for similarity.
- **Ranked retrieval results:** `recall_at_k`, `precision_at_k`, `mrr` and
  `ndcg_at_k` through `POST /api/v1/retrieval`, because they judge the
  order of ids, not their text.
- **Choosing between two systems:** any text or answers metric through
  `POST /api/v1/compare`, always with a `seed`. The difference is the first
  system's score minus the second's. A lower score beats for `ter`, and a
  higher score beats for every other metric; ties do not count as beating.

Version 1 does not judge open-ended output well, such as free-form chat or
reasoning answers, where many different outputs are right. That is for the
[later milestones](#later-milestones) named below: model-based metrics
(COMET, MetricX, BERTScore) and LLM-as-judge.

## Later milestones

- Model-based metrics on GPU: COMET or MetricX, and BERTScore.
- LLM-as-judge, through the LLM Gateway.
- Named test sets, stored and reused.

## Running the tests

```bash
./run_tests.sh                     # the whole suite
./run_tests.sh tests/test_health.py  # one file
```

`run_tests.sh` installs `requirements.txt` (with pytest and httpx) when the
file has changed since the last install, then runs pytest. The platform's
pipeline runs the same script in its test step, before it builds the image.

The checks in `live/` call the deployed service and are not part of the
suite; see `live/README.md`.

## Installing and deploying

The component is listed as `scoring` in
[thinkube-metadata](https://github.com/thinkube/thinkube-metadata)
`optional_components.json`. It is installed from Thinkube Control's Optional
Components page (or the `install_optional_component` MCP tool), which deploys
this template into the namespace `scoring`. The service is then at
`https://scoring.<domain>`.

The running service needs the setting `THINKUBE_CONTROL_URL`, the address of Thinkube Control
(for example `https://control.<domain>`), and will not start without it. It is
declared in `thinkube.yaml`, so a deployment through Control fills it in.

A change is deployed by pushing it and redeploying the installed component
from this template: the `redeploy_template` MCP tool with the name `scoring`,
or `python3 scripts/deploy.py scoring`, which needs `THINKUBE_CONTROL_URL` and
`THINKUBE_API_TOKEN` and waits until the deployment ends.

## License

MIT - See [LICENSE](LICENSE)

## Copyright

Copyright Alejandro Martínez Corriá and the Thinkube contributors
