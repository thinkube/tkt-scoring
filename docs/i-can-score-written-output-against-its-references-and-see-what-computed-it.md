# I can score written output against its references, and see what computed it

## What this does

You have some written output from an AI system — a translation, a summary,
an answer — and one or more reference texts it should match. You want a
number that says how close the output is to the references, and you want
to know exactly what produced that number, so you can trust it and compare
it with numbers from other projects.

Post your output and its references to the scoring service's
`POST /api/v1/text` endpoint, naming the metrics you want. You get back,
for each metric, a corpus score and a statement of what computed it: the
sacreBLEU signature for BLEU, chrF, chrF++ and TER, or the name and version
of the ROUGE implementation for ROUGE-1, ROUGE-2 and ROUGE-L.

## How you use it

Send a request like this:

```json
{
  "hypotheses": ["the cat sat on the mat"],
  "references": [["the cat sat on the mat", "a cat was sitting on the mat"]],
  "metrics": ["bleu", "chrf++", "rouge1"]
}
```

- `hypotheses` is the list of outputs you want scored.
- `references` gives, for each hypothesis in order, the list of references
  it should be checked against. A hypothesis with one reference still gets
  a list of one; a hypothesis with several references gets all of them.
- `metrics` names which of the seven metrics you want scored: `bleu`,
  `chrf`, `chrf++`, `ter`, `rouge1`, `rouge2`, `rougeL`. You can ask for
  any mix of sacreBLEU metrics and ROUGE metrics in the same request.

You get back one entry per metric you asked for, and nothing for a metric
you did not ask for:

```json
{
  "metrics": {
    "bleu": {"score": 100.0, "provenance": "nrefs:2|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0"},
    "chrf++": {"score": 100.0, "provenance": "nrefs:2|case:mixed|eff:yes|nc:6|nw:2|space:no|version:2.6.0"},
    "rouge1": {"score": 100.0, "provenance": "rouge-score 0.1.2"}
  }
}
```

Each metric's `score` is the corpus score over everything you posted —
not a per-sentence breakdown — and its `provenance` says exactly what
computed it, down to the version. If you ask for several references per
hypothesis, each ROUGE metric picks, for each hypothesis, whichever
reference scores best for that metric; BLEU, chrF, chrF++ and TER score
all the references together, the way sacreBLEU does.

If you name a metric that is not one of the seven, or give a different
number of reference groups than hypotheses, or post no hypotheses at all,
the service refuses the request and tells you what to fix — it never
invents a number.

## Who this is for

Anyone building or evaluating an AI system on Thinkube whose output is
free text — a translation, a summary, a generated answer — and who needs
a number that is comparable with everyone else's, because everyone's
number comes from the same implementation.
