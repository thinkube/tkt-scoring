# Live checks

Checks of what only the deployed component can answer. Each one calls the
service at `TANDEM_LIVE_URL`, sends the outputs and references it scores in
the request, and keeps nothing behind. The classification check sends its
predicted and true labels in the request the same way and keeps none of them. Every call to a scoring route sends the `THINKUBE_API_TOKEN` the checks are
given as a bearer token (`Authorization: Bearer <token>`); one check shows
the service refusing a request without a token, and a made-up one, with 401
while `/health` and `/docs` still answer without any. They never import this repository's
code and never run in the unit suite: Thinkube Tandem runs them after a
deploy (thinkube.yaml `spec.deploy.live`).
