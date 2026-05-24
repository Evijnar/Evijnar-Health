#!/usr/bin/env bash
set -euo pipefail

# check_structure.sh
# Scans the repository for files that don't conform to the canonical layout
# and prints a suggested plan. Does NOT move files by default.
# Usage: ./scripts/check_structure.sh [--apply]

APPLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=true; shift ;;
    -h|--help) echo "Usage: $0 [--apply]"; exit 0 ;;
    *) echo "Unknown arg $1"; exit 2 ;;
  esac
done

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
cd "$ROOT"

echo "Scanning for potential misplaced files..."

# Backend expected directories under apps/api/app/
EXPECTED_BACKEND=(routers services repositories models db dependencies middleware)

# Frontend expected directories under apps/web/src/
EXPECTED_FRONTEND=(app components lib styles)

# Find backend files not under expected subdirs
mapfile -t backend_misplaced < <(find apps/api/app -maxdepth 2 -type f \( -name "*.py" -o -name "*.pyi" \) -print | grep -vE "apps/api/app/(${EXPECTED_BACKEND[*]// /|})/" || true)

# Find frontend files not under expected src folders
mapfile -t frontend_misplaced < <(find apps/web -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.js" -o -name "*.jsx" -o -name "*.css" \) -print | grep -v "apps/web/src/" || true)

if [ ${#backend_misplaced[@]} -eq 0 ]; then
  echo "No backend misplaced files detected."
else
  echo "Backend files outside canonical subpaths:"; printf '%s\n' "${backend_misplaced[@]}"
fi

if [ ${#frontend_misplaced[@]} -eq 0 ]; then
  echo "No frontend files outside apps/web/src/ detected."
else
  echo "Frontend files outside apps/web/src/:"; printf '%s\n' "${frontend_misplaced[@]}"
fi

if [ "$APPLY" = true ]; then
  echo "--apply requested: attempting safe moves where possible."
  # For backend, move top-level python files into apps/api/app/ (if not there)
  for f in "${backend_misplaced[@]}"; do
    bn=$(basename "$f")
    target="apps/api/app/${bn}"
    echo "Moving $f -> $target"
    mkdir -p "$(dirname "$target")"
    git mv -f "$f" "$target" || mv "$f" "$target"
  done

  # For frontend, move JS/TS files into apps/web/src/components if they look like components
  for f in "${frontend_misplaced[@]}"; do
    bn=$(basename "$f")
    target_dir="apps/web/src/components"
    mkdir -p "$target_dir"
    target="$target_dir/$bn"
    echo "Moving $f -> $target"
    git mv -f "$f" "$target" || mv "$f" "$target"
  done

  echo "Apply complete. Review 'git status' for the changes."
else
  echo "Run with --apply to perform safe suggested moves."
fi
