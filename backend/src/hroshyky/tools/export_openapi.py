"""Write the OpenAPI schema of the application to a file.

Usage: `uv run python -m hroshyky.tools.export_openapi openapi.json`
"""

import json
import sys
from pathlib import Path

from hroshyky.api.app import create_app


def render() -> str:
    """Return the schema as stable JSON: sorted keys, so a diff shows only real changes."""
    return json.dumps(create_app().openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    """Write the schema to the path given as the only argument."""
    if len(argv) != 1:
        print(__doc__)
        return 2
    Path(argv[0]).write_text(render(), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
