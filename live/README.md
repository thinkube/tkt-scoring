# Live checks

Checks of what only the deployed component can answer. Each one calls the
service at `TANDEM_LIVE_URL`, sends the outputs and references it scores in
the request, and keeps nothing behind. The classification check sends its
predicted and true labels in the request the same way and keeps none of them. They never import this repository's
code and never run in the unit suite: Thinkube Tandem runs them after a
deploy (thinkube.yaml `spec.deploy.live`).
