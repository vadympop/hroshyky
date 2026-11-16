#!/usr/bin/env bash
# Fails when total coverage is lower than at the merge base with the given ref.
# Run after pytest. The base value is computed once per base commit and kept in .coverage-base/.
set -euo pipefail
cd "$(dirname "$0")/.."

base_sha=$(git merge-base HEAD "${1:-origin/main}")
cached=".coverage-base/$base_sha"
if [[ ! -f $cached ]]; then
  mkdir -p .coverage-base
  tree=$(mktemp -d)
  trap 'git worktree remove --force "$tree" 2>/dev/null || true' EXIT
  git worktree add --quiet --detach "$tree" "$base_sha"
  base=0
  if [[ -f $tree/backend/pyproject.toml ]]; then
    base=$(cd "$tree/backend" && uv run --locked pytest -q >&2 && uv run coverage report --format=total)
  fi
  echo "$base" >"$cached"
fi

base=$(cat "$cached")
head=$(uv run coverage report --format=total)
echo "total coverage: base $base%, now $head%"
uv run python -c "import sys; sys.exit($head < $base)"
