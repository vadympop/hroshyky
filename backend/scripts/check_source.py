"""Source rules that the linters do not cover.

Usage: `python scripts/check_source.py suppressions|length PATH...`

`suppressions`: every `noqa`, `type: ignore`, `pragma: no cover`, `nosec` and `fmt: off/skip`
names its rule code (where the tool has codes) and carries a written reason in a second comment:
`# noqa: S105  # the reason, at least ten characters`.

`length`: no Python file is longer than MAX_LINES lines.
"""

import re
import sys
import tokenize
from collections.abc import Iterator
from pathlib import Path

MAX_LINES = 400
SUPPRESSION = re.compile(r"#\s*(noqa|type:\s*ignore|pragma:\s*no\s*cover|nosec|fmt:\s*(off|skip))")
EXPLAINED = re.compile(
    r"#\s*(noqa: [A-Z]+\d+(, ?[A-Z]+\d+)*|type: ignore\[[\w, -]+\]|pragma: no cover"
    r"|fmt: (off|skip))\s+#\s*\S.{9,}"
)


def python_files(paths: list[str]) -> Iterator[Path]:
    """Yield the given files and every `.py` file under the given directories."""
    for path in map(Path, paths):
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*.py") if ".venv" not in p.parts)
        elif path.suffix == ".py":
            yield path


def unexplained_suppressions(path: Path) -> list[str]:
    """Return one message per suppression comment without a code or a reason."""
    with tokenize.open(path) as source:
        comments = [
            t for t in tokenize.generate_tokens(source.readline) if t.type == tokenize.COMMENT
        ]
    return [
        f"{path}:{token.start[0]}: suppression needs a rule code and a reason: {token.string}"
        for token in comments
        if SUPPRESSION.search(token.string) and not EXPLAINED.search(token.string)
    ]


def too_long(path: Path) -> list[str]:
    """Return a message when the file has more than MAX_LINES lines."""
    lines = len(path.read_text(encoding="utf-8").splitlines())
    return [f"{path}: {lines} lines, the limit is {MAX_LINES}"] if lines > MAX_LINES else []


CHECKS = {"suppressions": unexplained_suppressions, "length": too_long}


def main(argv: list[str]) -> int:
    """Run one check over the given paths. Exit code 1 when anything is found."""
    check = CHECKS.get(argv[0]) if argv[1:] else None
    if check is None:
        print(__doc__)
        return 2
    problems = [message for path in python_files(argv[1:]) for message in check(path)]
    print("\n".join(problems) if problems else f"{argv[0]}: ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
