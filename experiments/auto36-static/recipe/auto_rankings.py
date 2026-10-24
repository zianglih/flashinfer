#!/usr/bin/env python3
"""Extract rounded internal AUTO rankings, never substitute them for CUPTI results."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("capture", type=Path)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
if args.output.exists():
    raise FileExistsError(args.output)
header = re.compile(r"\[cutedsl-autotune\].* winner (\{.*\}) \(([0-9.]+) us median, max across ranks\) out of ([0-9]+) candidates:")
score = re.compile(r"^\s*([0-9.]+) us\s+(\{.*\})\s*$")
decoder = json.JSONDecoder()
groups = []
for path in sorted(args.capture.glob("sweep-*.log")):
    current = None
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        match = header.search(line)
        if match:
            current = {"log": path.name, "line": line_number,
                       "candidate_count": int(match[3]), "winner_knobs": ast.literal_eval(match[1]),
                       "winner_score_us": float(match[2]), "rankings": []}
            groups.append(current)
            continue
        match = score.match(line)
        if match and current is not None:
            current["rankings"].append({"rank": len(current["rankings"]) + 1,
                                        "score_us": float(match[1]), "knobs": ast.literal_eval(match[2])})
        marker = "MEGAMOE_TACTIC_JSON,"
        if current is not None and marker in line and "global_tokens" not in current:
            receipt, _ = decoder.raw_decode(line.split(marker, 1)[1])
            current["global_tokens"] = receipt["global_tokens"]
    if current is None:
        raise ValueError(f"No AUTO rankings in {path}")
for group in groups:
    if len(group["rankings"]) != group["candidate_count"] or "global_tokens" not in group:
        raise ValueError(f"Incomplete ranking group: {group}")
    mixed = [r for r in group["rankings"] if r["knobs"].get("fallback_cluster_shape_mnk") is not None]
    if mixed:
        best = min(mixed, key=lambda r: r["score_us"])
        group["best_mixed"] = best
        group["mixed_ties_at_printed_precision"] = [r for r in mixed if r["score_us"] == best["score_us"]]
        group["best_mixed_over_winner_ratio"] = best["score_us"] / group["winner_score_us"]
    print(json.dumps({k: v for k, v in group.items() if k not in ("rankings", "mixed_ties_at_printed_precision")}, sort_keys=True))
report = {"capture": str(args.capture.resolve()), "groups": groups,
          "scope": "Rounded AUTO graph-event selection scores; not standalone fixed-tactic benchmarks or cold-L2 CUPTI reported medians.",
          "log_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in args.capture.glob("sweep-*.log")}}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
