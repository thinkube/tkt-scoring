#!/bin/sh
# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: Apache-2.0

# run_tests.sh - Run the tests.
#
#   ./run_tests.sh              the whole suite (the platform's pipeline)
#   ./run_tests.sh <file>       one test file (Thinkube Tandem)

set -e
cd "$(dirname "$0")"

# The requirements are installed once per tree and again only when
# requirements.txt changes; .provisioned holds the hash they were installed for.
# pytest and httpx (which FastAPI's TestClient uses) are needed by the tests only.
STAMP=.provisioned
WANT=$(sha256sum requirements.txt | cut -d' ' -f1)
if [ "$(cat "$STAMP" 2>/dev/null)" != "$WANT" ]; then
    pip install --break-system-packages -q -r requirements.txt pytest==8.4.2 httpx==0.28.1
    echo "$WANT" > "$STAMP"
fi

python3 -m pytest -q -p no:cacheprovider "${1:-tests}"
