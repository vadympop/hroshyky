from pathlib import Path

import pytest

import check_source

# Built from parts so that this file does not itself contain suppression comments.
HASH = "#"
BAD_LINES = [
    f"x = 1  {HASH} noqa",
    f"x = 1  {HASH} noqa: E501",
    f"x = 1  {HASH} type: ignore",
    f"x = 1  {HASH} type: ignore[arg-type]",
    f"x = 1  {HASH} pragma: no cover",
    f"x = 1  {HASH} nosec",
    f"x = 1  {HASH} noqa: E501  {HASH} short",
]
GOOD_LINES = [
    f"x = 1  {HASH} noqa: E501, S105  {HASH} the URL cannot be wrapped",
    f"x = 1  {HASH} type: ignore[arg-type]  {HASH} the stub is wrong upstream",
    f"x = 1  {HASH} pragma: no cover  {HASH} only runs on Windows",
    f"x = '{HASH} noqa'  {HASH} an ordinary comment",
]


@pytest.mark.parametrize("line", BAD_LINES)
def test_suppression_without_code_or_reason_is_reported(tmp_path: Path, line: str) -> None:
    source = tmp_path / "bad.py"
    source.write_text(f"y = 0\n{line}\n", encoding="utf-8")

    assert check_source.unexplained_suppressions(source) == [
        f"{source}:2: suppression needs a rule code and a reason: {line.split('  ', 1)[1]}"
    ]
    assert check_source.main(["suppressions", str(source)]) == 1


def test_explained_suppressions_pass(tmp_path: Path) -> None:
    source = tmp_path / "good.py"
    source.write_text("\n".join(GOOD_LINES) + "\n", encoding="utf-8")

    assert check_source.main(["suppressions", str(tmp_path)]) == 0


def test_length_limit_is_enforced_on_directories(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "ok.py").write_text("x = 1\n" * check_source.MAX_LINES, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("x\n" * 1000, encoding="utf-8")
    assert check_source.main(["length", str(tmp_path), str(tmp_path / "notes.txt")]) == 0

    long_file = tmp_path / "pkg" / "long.py"
    long_file.write_text("x = 1\n" * (check_source.MAX_LINES + 1), encoding="utf-8")
    assert check_source.too_long(long_file) == [f"{long_file}: 401 lines, the limit is 400"]
    assert check_source.main(["length", str(tmp_path)]) == 1


def test_virtualenv_is_skipped(tmp_path: Path) -> None:
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.py").write_text("x = 1\n" * 500, encoding="utf-8")

    assert check_source.main(["length", str(tmp_path)]) == 0


@pytest.mark.parametrize("argv", [[], ["length"], ["unknown", "x.py"]])
def test_bad_usage_exits_with_2(argv: list[str]) -> None:
    assert check_source.main(argv) == 2
