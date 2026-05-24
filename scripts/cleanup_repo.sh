#!/usr/bin/env bash
set -euo pipefail

# cleanup_repo.sh
# Safely removes common development artifacts and build outputs.
# Usage:
#   ./scripts/cleanup_repo.sh         # interactive
#   ./scripts/cleanup_repo.sh --yes   # run non-interactively
#   ./scripts/cleanup_repo.sh --dry   # show what would be removed
#   ./scripts/cleanup_repo.sh --deep  # include node_modules removals

SELF=$(basename "$0")
DRY=false
ASSUME_YES=false
DEEP=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry) DRY=true; shift ;;
    --yes) ASSUME_YES=true; shift ;;
    --deep) DEEP=true; shift ;;
    -h|--help)
      cat <<EOF
Usage: $SELF [--dry] [--yes] [--deep]

--dry    : Show files that would be removed (no deletion).
--yes    : Run non-interactively.
--deep   : Also remove large dependency folders (node_modules, .venv).
EOF
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
cd "$ROOT_DIR"

PATTERNS=(
  "__pycache__"
  "*.pyc"
  "*.pyo"
  "*.pyd"
  ".pytest_cache"
  ".mypy_cache"
  ".DS_Store"
  "htmlcov"
  ".coverage"
  "coverage.xml"
  "apps/web/.next"
  "dist"
  "build"
  "*.egg-info"
  ".cache"
  "*.log"
  "npm-debug.log*"
  "yarn-debug.log*"
  "yarn-error.log*"
  "Thumbs.db"
  "Desktop.ini"
)

if [ "$DEEP" = true ]; then
  PATTERNS+=("node_modules" "apps/web/node_modules" "apps/web/.turbo" ".venv" "venv" "env")
fi

# Find targets
mapfile -t TO_REMOVE < <(for p in "${PATTERNS[@]}"; do
  # use find to gather matching items safely
  find . -type d -name "${p##*/}" -path "./${p#*/}" 2>/dev/null || true
  find . -name "$p" -print 2>/dev/null || true
done | sort -u)

if [ ${#TO_REMOVE[@]} -eq 0 ]; then
  echo "No matching artifacts found. Nothing to clean."
  exit 0
fi

echo "Found the following artifact paths to remove:"
printf "%s\n" "${TO_REMOVE[@]}"

if [ "$DRY" = true ]; then
  echo "Dry run — no deletions performed."
  exit 0
fi

if [ "$ASSUME_YES" != true ]; then
  read -rp "Proceed to delete the above items? (y/N): " yn
  case "$yn" in
    [Yy]* ) ;;
    *) echo "Aborted."; exit 1 ;;
  esac
fi

# Delete
for path in "${TO_REMOVE[@]}"; do
  if [ -e "$path" ]; then
    echo "Removing: $path"
    rm -rf "$path"
  fi
done

# Remove stray compiled JS server build artifacts under .next (if any were not matched)
if [ -d "apps/web/.next" ]; then
  echo "Removing apps/web/.next"
  rm -rf apps/web/.next
fi

echo "Cleanup complete. Run 'git status' to review remaining changes."