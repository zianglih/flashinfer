#!/usr/bin/env bash
# Re-run the exact captured CPU-only helper using the normalized public inputs.
set -euo pipefail
[[ $# == 3 ]] || { echo "usage: $0 EXPERIMENT_DIRECTORY baseline_OR_candidate4s NEW_AUDIT_JSON" >&2; exit 2; }
experiment=$1 arm=$2 output=$3
case "$arm" in
  baseline) modes=atomic_counter:16 ;;
  candidate4s) modes=atomic_counter:18,static:18 ;;
  *) echo "unknown experiment arm" >&2; exit 2 ;;
esac
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
# The native helper expects run.json; preserve the public metadata bytes verbatim.
cp "$experiment/$arm/metadata.json" "$temporary/run.json"
cp "$experiment/$arm/raw-records.json" "$temporary/raw-records.json"
python3 -B "$experiment/recipe/audit_scheduler_modes.py" "$temporary" \
  --rankings "$experiment/$arm/auto-rankings.json" --mode-counts "$modes" --output "$output"
