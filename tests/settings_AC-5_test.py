# Copyright Alejandro Martínez Corriá and the Thinkube contributors
# SPDX-License-Identifier: MIT

import re
from pathlib import Path

DESCRIPTOR = Path(__file__).resolve().parent.parent / "thinkube.yaml"


def _entry():
    lines = DESCRIPTOR.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if "THINKUBE_CONTROL_URL" in line)
    # The entry runs from its own list item to the next one (or a dedent).
    first = start
    while first > 0 and not lines[first].lstrip().startswith("- "):
        first -= 1
    indent = len(lines[first]) - len(lines[first].lstrip())
    block = [lines[first]]
    for line in lines[first + 1:]:
        if line.strip() and (len(line) - len(line.lstrip())) <= indent:
            break
        block.append(line)
    return "\n".join(block)


# WHY (TRANSITION): proves the deployment descriptor now declares
# THINKUBE_CONTROL_URL with a description and a default built from the
# domain placeholder; its job is done once the setting is declared.
def test_descriptor_declares_the_setting_with_description_and_default():
    assert "THINKUBE_CONTROL_URL" in DESCRIPTOR.read_text()
    entry = _entry()
    assert re.search(r"description\s*:\s*\S", entry)
    default = re.search(r"default\s*:\s*(.+)", entry)
    assert default, entry
    value = default.group(1)
    assert "control" in value.lower()
    assert re.search(r"\{\{.*domain.*\}\}|\$\{?.*domain.*\}?", value, re.I), value


# WHY (TRANSITION): proves the README now tells operators the service needs
# THINKUBE_CONTROL_URL and will not start without it; done once documented.
def test_readme_says_the_setting_is_required():
    text = (DESCRIPTOR.parent / "README.md").read_text()
    assert "THINKUBE_CONTROL_URL" in text
    assert "address of thinkube control" in text.lower()
