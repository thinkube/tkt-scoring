# POST /api/v1/answers

`POST /api/v1/answers` tells you how well a set of predicted answers
matches the answers you accept, the way SQuAD scores question answering.

## How to use it

Send a JSON body with `items`. Each item has a `prediction` (the text your
system produced) and `answers` (a list of accepted answers). Include your
bearer token in the `Authorization` header.

```bash
curl -X POST https://scoring.<domain>/api/v1/answers \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"items": [{"prediction": "The  Eiffel-Tower!", "answers": ["eiffeltower"]}]}'
```

## What you get back

- `exact_match`: the percentage of predictions that equal an accepted answer.
- `token_f1`: the average word-overlap score, as a percentage.
- `count`: how many predictions were scored.
- `normalisation`: a statement of how the texts were tidied before comparing.

Before comparing, both sides are lowercased, punctuation is deleted without
leaving a space ("Eiffel-Tower" becomes "eiffeltower"), the articles a, an
and the are removed, and runs of whitespace become single spaces.

## When it refuses

You get a 422 with a message saying what to fix if you send no items, or an
item with no accepted answers.
