# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

# The tests import the service as `app`, from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
