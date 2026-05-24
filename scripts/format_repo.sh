#!/usr/bin/env bash
set -euo pipefail

# format_repo.sh
# Runs formatters and linters if available. Non-fatal: will skip tools that aren't installed.
# Usage: ./scripts/format_repo.sh

echo "Formatting Python (black/isort/ruff) if available..."
if command -v ruff >/dev/null 2>&1; then
  echo "Running ruff check/fix..."
  ruff check . || true
  ruff format . || true
else
  echo "ruff not found — skipping. Install via 'pip install ruff'."
fi

if command -v black >/dev/null 2>&1; then
  echo "Running black..."
  black --line-length 88 . || true
else
  echo "black not found — skipping. Install via 'pip install black'."
fi

if command -v isort >/dev/null 2>&1; then
  echo "Running isort..."
  isort . || true
else
  echo "isort not found — skipping. Install via 'pip install isort'."
fi

echo "Formatting frontend (prettier/tsc) if available..."
if [ -f "apps/web/package.json" ]; then
  if command -v npm >/dev/null 2>&1; then
    (cd apps/web && npm run type-check) || echo "Type-check failed or 'type-check' script not available."
    (cd apps/web && npm run lint) || echo "Lint step failed or not configured."
  else
    echo "npm not found — skipping frontend commands."
  fi
fi

echo "Formatting complete. Review diffs and run tests/build as needed."