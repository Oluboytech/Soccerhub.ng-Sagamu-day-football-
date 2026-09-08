#!/usr/bin/env bash
# Full data pipeline for the Sagamu Day 2026 competition data repo.
#
# Order matters:
#   1. Validate the raw, hand-edited source files (teams/groups/matches/players)
#      BEFORE deriving anything from them — never compute standings on top of
#      broken data.
#   2. Compute standings.json from matches.json results.
#   3. Compute derived convenience files (upcoming/results/top-scorers) and
#      the manifest, which hashes the freshly-written files above.
#   4. Validate again — the full, final output — as the last gate before commit.
#
# Usage: scripts/build.sh [path-to-repo-root]   (defaults to repo root)

set -euo pipefail

REPO_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DATA_DIR="$REPO_ROOT/data/v1/sagamu-day-2026"

echo "== Sagamu Day 2026 data build =="
echo "Repo root: $REPO_ROOT"
echo

echo "-- Step 1/4: validating source data --"
python3 "$REPO_ROOT/scripts/validate.py" "$REPO_ROOT"
echo

echo "-- Step 2/4: computing standings --"
python3 "$REPO_ROOT/scripts/compute_standings.py" "$DATA_DIR"
echo

echo "-- Step 3/4: computing derived endpoints + manifest --"
python3 "$REPO_ROOT/scripts/compute_derived.py" "$DATA_DIR"
echo

echo "-- Step 4/4: final validation --"
python3 "$REPO_ROOT/scripts/validate.py" "$REPO_ROOT"
echo

echo "Build complete."
