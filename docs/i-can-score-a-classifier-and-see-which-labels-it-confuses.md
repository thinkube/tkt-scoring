# I can score a classifier and see which labels it confuses

## What this does

You have a classifier — it puts each item under one label — and you know
the label each item should have had. You want one number for how often it
was right, a precision, recall and F1 for each label, and a table showing
which labels it mixes up with which.

Post the labels it predicted and the true labels to the scoring service's
`POST /api/v1/classification` endpoint. You get back all of those numbers,
computed the same way for every project.

## How you use it

Send your Thinkube token with the request, as `Authorization: Bearer <token>`
(a Keycloak token of the platform's realm or a Thinkube API token). Without
one the service answers 401.

Send a request like this:

```json
{
  "predicted": ["bird", "bird", "cat", "cat", "dog", "dog"],
  "true_labels": ["bird", "cat", "cat", "dog", "dog", "bird"]
}
```

- `predicted` is the list of labels the classifier gave, one per item.
- `true_labels` is the list of labels each item should have had, in the
  same order. Position `i` in one list is the same item as position `i` in
  the other, so the two lists must be the same length and not empty.

You get back:

```json
{
  "accuracy": 0.5,
  "per_label": {
    "bird": {"precision": 0.5, "recall": 0.5, "f1": 0.5},
    "cat": {"precision": 0.5, "recall": 0.5, "f1": 0.5},
    "dog": {"precision": 0.5, "recall": 0.5, "f1": 0.5}
  },
  "macro": {"precision": 0.5, "recall": 0.5, "f1": 0.5},
  "micro": {"precision": 0.5, "recall": 0.5, "f1": 0.5},
  "labels": ["bird", "cat", "dog"],
  "confusion_matrix": [[1, 0, 1], [1, 1, 0], [0, 1, 1]],
  "statement": "Accuracy is the share of positions where the predicted label equals the true label. Per-label precision is TP / (TP + FP), recall is TP / (TP + FN), and F1 is their harmonic mean, treating that label as the positive class and every other label as the negative class; a value whose denominator is zero is 0.0. Macro average is the unweighted mean of the per-label values. Micro average is computed from the pooled true/false positive and false negative counts across all labels. The confusion matrix has one row per true label and one column per predicted label, in the order given by labels."
}
```

What each field means:

- `accuracy` is the number of positions where the predicted label equals
  the true label, divided by the number of positions. It is between 0 and 1.
- `per_label` has one entry for every label that appears, whether it
  appears among the predictions, among the true labels, or both. Each
  entry holds that label's `precision` (of the items predicted as this
  label, the share that truly were), `recall` (of the items that truly
  were this label, the share predicted as it) and `f1` (the harmonic mean
  of the two). A value whose denominator is zero is 0.0.
- `macro` is the unweighted mean of the per-label `precision`, `recall`
  and `f1`, so a label with few examples counts as much as one with many.
- `micro` is the same three numbers computed from the counts pooled over
  all labels. When every item has exactly one predicted and one true
  label, micro precision, micro recall, micro F1 and `accuracy` are the
  same number.
- `labels` is the order the confusion matrix is written in. It holds every
  label that appears, once.
- `confusion_matrix` has as many rows and columns as `labels` has entries.
  The rows are the true label and the columns are the predicted label:
  the cell in row `i`, column `j` counts the items whose true label is
  `labels[i]` and whose predicted label is `labels[j]`. In the example, the
  first row says that of the two items truly `bird`, one was predicted
  `bird` and one was predicted `dog`.
- `statement` says in words how the numbers were computed.

The service answers exactly these fields and nothing else.

The service keeps nothing of what you post: no label from your request is
logged or stored.

If you post lists of different lengths, the service refuses with a 422
that names both counts. If you post an empty list, or leave out
`predicted` or `true_labels`, it refuses and says that both are required
and each must be a non-empty list of the same length. In every refusal no
numbers come back — it never invents a number.

## Who this is for

Anyone building or evaluating a classifier on Thinkube who needs numbers
that are comparable with everyone else's, because everyone's numbers come
from the same implementation.
