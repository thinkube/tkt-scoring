# I can compare two systems and see whether the difference is real

`POST /api/v1/compare` scores two systems on the same items with one metric
and tells you whether the gap between them is more than resampling noise.

## What to send

- `hypotheses_a`, `hypotheses_b`: the two systems' outputs, same items, same order.
- `references`: one list of references per item (a list of one for a single reference).
- `metric`: one of `bleu`, `chrf`, `chrf++`, `ter`, `rouge1`, `rouge2`, `rougeL`, `exact_match`, `token_f1`.
- `samples`: the number of bootstrap samples, a positive whole number.
- `seed`: a whole number; the same inputs and seed give the same answer.

## A worked request

```json
{
  "hypotheses_a": ["the cat sat on the mat", "birds sing", "it rains"],
  "hypotheses_b": ["a dog ran", "birds sing", "sun shines"],
  "references": [["the cat sat on the mat"], ["birds sing"], ["it rains"]],
  "metric": "rouge1",
  "samples": 1000,
  "seed": 7
}
```

## A worked answer (numbers illustrative)

```json
{
  "metric": "rouge1",
  "samples": 1000,
  "seed": 7,
  "system_a": {"score": 100.0, "lower": 100.0, "upper": 100.0},
  "system_b": {"score": 33.3, "lower": 0.0, "upper": 66.7},
  "difference": {"score": 66.7, "lower": 33.3, "upper": 100.0},
  "share_a_beats_b": 0.93,
  "significant": true,
  "provenance": "rouge-score 0.1.2",
  "method": "Paired bootstrap. ..."
}
```

Scores are on the metric's own scale. The `difference` is the first system's
score minus the second's. `share_a_beats_b` is the share of samples in which
the first system is strictly better (strictly lower for `ter`); ties do not count.

## Reading it

The intervals are 95% percentile intervals. The result is `significant` only
when the difference interval excludes zero. **A difference whose interval
includes zero is not significant, and is not a gain**, however large the
difference score looks.

## Refusals

A bad request gets 400 with a message saying what to send: empty outputs, an
unknown metric (the accepted keys are listed), systems or references of
different lengths (both counts are named), an empty reference group, or a
sample count that is not a positive whole number. Nothing of the request is kept.
