"""
Lesson 17: lfx, the standalone executor. Everything so far has run
inside this repo's own `uv` environment, with the full `langflow`
package installed. `lfx` is the lighter package underneath it, on its
own, it's enough to run a flow from a plain CLI command, no Python
script, no server, exactly what you'd reach for in a CI pipeline.

Read README.md in this folder first, then read this file top to bottom,
then run it with:

    uv run python lessons/langflow/03_advanced/17_lfx_headless_execution/lesson.py

No running Langflow server is required for this one.
"""

import subprocess
import sys
from pathlib import Path

FLOW_PATH = Path(__file__).parent.parent.parent / "01_beginner" / "02_first_flow" / "flow.json"


def run_via_lfx_cli(input_value: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "lfx", "run", str(FLOW_PATH), input_value, "-f", "text"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main() -> None:
    answer = run_via_lfx_cli("Say hello in exactly three words.")
    print(f"lfx CLI said: {answer}")


if __name__ == "__main__":
    main()
