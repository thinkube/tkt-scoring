# tkt-scoring

A Thinkube optional component: a CPU service that scores the outputs of AI
systems against references. Every measurement on Thinkube goes through it, so
every measurement uses one implementation, and two numbers from two projects
can be compared.

Today the service is a skeleton: it answers `GET /health` with
`{"status": "ok"}`. The metrics below are built on it next.

## Version 1

- **Translation and generation text:** BLEU, chrF, chrF++ and TER through
  sacreBLEU 2.6.0, each returned with its sacreBLEU signature; ROUGE-1,
  ROUGE-2 and ROUGE-L.
- **Answers and extraction:** exact match and token F1.
- **Classification:** accuracy; precision, recall and F1, macro and micro;
  the confusion matrix.
- **Retrieval:** recall@k, precision@k, MRR and nDCG@k.
- **Comparing two systems:** paired bootstrap for any of the metrics above,
  with 95% intervals and significance. A difference inside the interval is
  not a gain.

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

A change is deployed by pushing it and redeploying the installed component
from this template: the `redeploy_template` MCP tool with the name `scoring`,
or `python3 scripts/deploy.py scoring`, which needs `THINKUBE_CONTROL_URL` and
`THINKUBE_API_TOKEN` and waits until the deployment ends.

## License

Apache License 2.0 - See [LICENSE](LICENSE)

## Copyright

Copyright Alejandro Martínez Corriá and the Thinkube contributors
