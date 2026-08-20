"""
Lesson 19: exporting and versioning flows. `flow.json` is a real,
diffable file the moment it's in git, but "diffable" and "reviewable"
aren't the same thing, and `lfx` ships two CLI checks worth running
before you commit one: `validate` and `upgrade`.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langflow/03_advanced/19_exporting_and_versioning_flows/lesson.py

No running Langflow server is required for this one.
"""

import json
import subprocess
import sys
import uuid
from pathlib import Path

SOURCE_FLOW = Path(__file__).parent.parent.parent / "01_beginner" / "02_first_flow" / "flow.json"
FLOW_PATH = Path(__file__).parent / "flow.json"


def run_lfx(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "lfx", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> None:
    # A flow.json produced by graph.dump() (every flow.json shipped
    # earlier in this course) has no top-level "id" field, the server
    # assigns one on upload, `lfx validate` catches this before you'd
    # ever find out the hard way.
    missing_id = run_lfx("validate", str(SOURCE_FLOW))
    print("validate, as shipped (no top-level id):")
    print((missing_id.stdout + missing_id.stderr).strip())

    # Adding one, the fix, makes it pass.
    flow_data = json.loads(SOURCE_FLOW.read_text())
    flow_data["id"] = str(uuid.uuid4())
    FLOW_PATH.write_text(json.dumps(flow_data, indent=2))

    fixed = run_lfx("validate", str(FLOW_PATH))
    print("\nvalidate, with an id added:")
    print(fixed.stdout.strip() or f"(exit code {fixed.returncode}, no issues)")

    # `upgrade` checks something different: whether each component in
    # the flow still matches what the installed Langflow version
    # expects, useful after upgrading the langflow/lfx package itself.
    upgrade_check = run_lfx("upgrade", str(FLOW_PATH))
    print("\nupgrade check:")
    print(upgrade_check.stdout.strip())


if __name__ == "__main__":
    main()
