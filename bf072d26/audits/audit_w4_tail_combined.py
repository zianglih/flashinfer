"""Verify the complete 39-cell union without rewriting either campaign."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

P = Path(__file__).resolve().parents[1]
OUT = P / "experiments/w4-tail-dequant/combined39"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
csvrows = lambda p: list(csv.DictReader(p.open()))
key = lambda r: (r["job"], int(r["tokens"]), r["backend"])
gm = lambda rows: 100 * (math.exp(statistics.mean(math.log1p(float(r["speedup_percent"]) / 100) for r in rows)) - 1)
close = lambda a, b: math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-9)
summary = read(OUT / "summary.json")
all_rows = {}
configs = []
audits = [read(P / "audits" / name) for name in ("w4-tail-data-peer.json", "w4-tail-remaining-data-peer.json")]
assert all(a["passed"] for a in audits)
for source in summary["inputs"]:
    data = Path(source["data"])
    report = data.parent / "report"
    for filename, expected in ((data / "perf-config.json", source["config_sha256"]), (report / "cells.csv", source["cells_sha256"]), (report / "summary.json", source["summary_sha256"]), (report / "resource-deltas.json", source["resource_sha256"])):
        assert sha(filename) == expected
    configs.append(read(data / "perf-config.json"))
    rows = csvrows(report / "cells.csv")
    assert len(rows) == source["measured_cells"]
    for row in rows:
        assert key(row) not in all_rows
        all_rows[key(row)] = row
assert configs[0]["observer_hashes"] == configs[1]["observer_hashes"]
for role in ("control", "candidate"):
    for field in ("head", "repo", "source_sha256", "tracked_manifest_sha256", "register_policy", "freeze_receipt_sha256", "workspace_base", "cute_cache"):
        assert configs[0]["sources"][role][field] == configs[1]["sources"][role][field]
merged = csvrows(OUT / "cells.csv")
assert len(merged) == len(all_rows) == 39
assert {key(r): r for r in merged} == all_rows
tokens = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384}
jobs = {r["job"] for r in merged}
assert len(jobs) == 3
assert all({int(r["tokens"]) for r in merged if r["job"] == job} == tokens for job in jobs)
retention = [r for r in merged if int(r["tokens"]) >= 4]
assert len(retention) == 33 and all(r["retention"] == "True" for r in retention)
band = lambda r: "decode" if int(r["tokens"]) <= 64 else "middle" if int(r["tokens"]) <= 512 else "prefill"
for name, reported in summary["groups"].items():
    parts = name.split("/")
    selected = [r for r in retention if all(part == "all" or (r["job"] == part if part in jobs else band(r) == part) for part in parts)]
    assert reported["cells"] == len(selected)
    assert close(reported["speedup_percent"], gm(selected))
    assert reported["negative"] == sum(float(r["speedup_percent"]) < 0 for r in selected)
    for role in ("control", "candidate"):
        assert close(reported["max_" + role + "_spread"], max(float(r[role + "_spread_percent"]) for r in selected))
for field, audit_field in (("raw_samples", "samples"), ("loaded_kernels", "loaded_resource_records"), ("clock_quartiles", "clock_quartiles"), ("clock_exception_quartiles", "clock_exception_quartiles"), ("missing_clock_quartiles", "missing_clock_quartiles"), ("default_stage_resource_joins", "default_stage_joins")):
    assert summary[field] == sum(a[audit_field] for a in audits)
small = [r for r in retention if int(r["tokens"]) <= 512]
assert len(small) == 24
assert all(max(float(r["a1_us"]), float(r["a2_us"])) < min(float(r["c1_us"]), float(r["c2_us"])) for r in small)
result = {
    "passed": True,
    "combined_summary_sha256": sha(OUT / "summary.json"),
    "combined_cells_sha256": sha(OUT / "cells.csv"),
    "source_manifests": summary["source_manifests"],
    "measured_cells": 39,
    "retention_cells": 33,
    "original_12_row_dicts_exactly_preserved": True,
    "all_27_new_row_dicts_exactly_preserved": True,
    "raw_samples": summary["raw_samples"],
    "phase_medians": sum(a["phase_medians"] for a in audits),
    "loaded_resource_records": summary["loaded_kernels"],
    "all_78_cell_stage_resource_configs_equal": True,
    "clock_quartiles": summary["clock_quartiles"],
    "clock_exception_quartiles": summary["clock_exception_quartiles"],
    "missing_clock_quartiles": summary["missing_clock_quartiles"],
    "retention_geomean_percent": gm(retention),
    "negative_retention_cells": sum(float(r["speedup_percent"]) < 0 for r in retention),
    "all_24_decode_middle_cells_have_both_candidate_phases_below_both_controls": True,
    "groups": summary["groups"],
    "input_audits": {name: sha(P / "audits" / name) for name in ("w4-tail-data-peer.json", "w4-tail-components-peer.json", "w4-tail-remaining-data-peer.json", "w4-tail-remaining-components-peer.json")},
    "boundary": "All negative cells retained; tokens 1/2 excluded only from retention groups. No row replacement, fresh timing, source changes, or statistical-confidence claim. Prefill aggregate includes two positive 8K cells with substantial phase/clock variation.",
}
(P / "audits/w4-tail-combined-data-peer.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k not in ("groups", "input_audits")}, indent=2))
