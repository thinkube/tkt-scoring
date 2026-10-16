#!/usr/bin/env python3
# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

"""Redeploy this component through Thinkube Control and wait for the result.

Usage: python3 scripts/deploy.py <component name>

Thinkube Control renders a platform template from the head of the branch the
cluster follows, so the script first checks that the checkout is clean and
that its head is pushed, then asks Control to redeploy the component and
waits for the deployment to end. It exits 0 only when the deployment
succeeded.

Needs THINKUBE_CONTROL_URL and THINKUBE_API_TOKEN.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLL_SECONDS = 15
DEPLOY_SECONDS = 30 * 60
# A request to Control can fail while its backend restarts; the same request
# is sent again this many times before the deploy stops with the error.
REQUEST_TRIES = 8


def fail(message: str) -> None:
    print(f"deploy: {message}", file=sys.stderr)
    sys.exit(1)


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode != 0:
        fail(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def template_url() -> str:
    origin = git("remote", "get-url", "origin")
    m = re.match(r"^git@([^:]+):(.+?)(\.git)?$", origin)
    if m:
        return f"https://{m.group(1)}/{m.group(2)}"
    return re.sub(r"\.git$", "", origin)


def check_pushed() -> None:
    """Stop unless what Control will render is this checkout's head."""
    # .tandem/ is Tandem's record of what it proved here, written as it works;
    # it is not part of what is deployed.
    if git("status", "--porcelain", "--", ".", ":!.tandem"):
        fail("the checkout has uncommitted changes; commit and push them first")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    git("fetch", "-q", "origin", branch)
    if git("rev-parse", "HEAD") != git("rev-parse", f"origin/{branch}"):
        fail(f"the head of {branch} is not the head of origin/{branch}; push or pull first")


def call(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    last = ""
    for _ in range(REQUEST_TRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}"
            if e.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = str(e)
        time.sleep(POLL_SECONDS)
    fail(f"{method} {url} failed: {last}")


def redeploy(name: str, control: str, token: str) -> None:
    queued = call("POST", f"{control}/api/v1/templates/redeploy-async", token,
                  {"template_url": template_url(), "template_name": name, "variables": {}})
    deployment = queued.get("deployment_id")
    if not deployment:
        fail(f"Control did not queue the redeploy: {json.dumps(queued)[:500]}")
    print(f"deploy: redeploying {name} ({deployment})")
    started = time.time()
    while time.time() - started < DEPLOY_SECONDS:
        time.sleep(POLL_SECONDS)
        status = call("GET", f"{control}/api/v1/templates/deployments/{deployment}", token)
        state = status.get("status")
        if state == "success":
            print(f"deploy: {name} redeployed")
            return
        if state in ("failed", "cancelled"):
            fail(f"the redeploy {state}: {status.get('output') or status.get('reason') or 'no reason given'}")
    fail(f"the redeploy did not end within {DEPLOY_SECONDS // 60} minutes ({deployment})")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: python3 scripts/deploy.py <component name>")
    control = os.environ.get("THINKUBE_CONTROL_URL", "").rstrip("/")
    token = os.environ.get("THINKUBE_API_TOKEN", "")
    if not control:
        fail("THINKUBE_CONTROL_URL is not set: the address of Thinkube Control, such as https://control.<domain>")
    if not token:
        fail("THINKUBE_API_TOKEN is not set: a Thinkube Control API token")
    check_pushed()
    redeploy(sys.argv[1], control, token)


if __name__ == "__main__":
    main()
