"""Join the complete fresh merged-head AA matrix to immutable historical baselines.

Adapted from publication/assemble.py; no benchmark execution or table parsing.
"""
import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HEAD = "a620ce7790b32f7f0ae524a811417d2c6cee1152"
HISTORICAL = "326c4a793085e79b64b9c7fd79e77320c220ccba"
MODELS = [("v3", "V3", 8), ("v41-flash", "V41F", 4),
          ("kimi-k3", "K3", 8), ("nemo3-ultra", "N3U", 8)]
MODES = ["CuteDSL W4A4", "CuteDSL PER-TOKEN", "CuteDSL W4A16",
         "CuteDSL MXFP4x8", "CuteDSL MXFP8"]
TOKENS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]
COLUMNS = [("trtllm_w4a4", "TRTLLM W4A4", MODES[0]),
           ("trtllm_per_token", "TRTLLM PER-TOKEN", MODES[1]),
           ("trtllm_mxfp4x8", "TRTLLM MXFP4x8", MODES[3]),
           ("trtllm_mxfp8", "TRTLLM MXFP8", MODES[4]),
           ("legacy_w4a4", "Non-swap W4A4", MODES[0]),
           ("legacy_per_token", "Non-swap PER-TOKEN", MODES[1]),
           ("legacy_mxfp4x8", "Non-swap MXFP4x8†", MODES[3]),
           ("legacy_mxfp8", "Non-swap MXFP8†", MODES[4]),
           ("w4a16", "W4A16 before PR", MODES[2])]
BASELINE_FIELDS = ["model", "tokens", "column", "baseline", "status",
                   "baseline_ms", "reason", "baseline_evidence"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def writecsv(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


def key(row):
    return row["model"], row["topology"], row["backend"], int(row["tokens"])


def gm(values):
    return 100 * math.expm1(statistics.mean(math.log1p(x / 100) for x in values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, nargs="+", required=True)
    args = parser.parse_args()
    roots = [p.resolve() for p in args.data]
    assert len(roots) == len(set(roots))
    fresh, logs, clocks, resources, inputs, summaries, jobs = {}, [], [], [], [], [], set()
    source_records = []
    for data in roots:
        assert data.is_relative_to(ROOT)
        report = data.parent / "report"
        summary = read(report / "summary.json")
        assert summary["passed"] and summary["complete_campaign"]
        config = read(data / "perf-config.json")
        assert config["phases"] == ["candidate", "candidate"]
        source = config["sources"]["candidate"]
        assert source["head"] == HEAD
        manifest = data / Path(source["tracked_manifest"]).name
        assert sha(manifest) == source["tracked_manifest_sha256"]
        assert len(read(manifest)) == 13245
        for path, digest in source["source_sha256"].items():
            raw = subprocess.check_output(["git", "-C", str(ROOT / "flashinfer"),
                                           "show", f"{HEAD}:{path}"])
            assert hashlib.sha256(raw).hexdigest() == digest, path
        source_records.append(source)
        incoming = rows(report / "cells.csv")
        assert len(incoming) == summary["cells"]
        for row in incoming:
            identity = key(row)
            assert identity not in fresh
            value = dict(row)
            value["tokens"] = int(row["tokens"])
            for field in ("a1_us", "a2_us", "candidate_us", "candidate_spread_percent"):
                value[field] = float(row[field])
            assert math.isclose(value["candidate_us"], math.sqrt(value["a1_us"] * value["a2_us"]), abs_tol=1e-9)
            value["candidate_evidence"] = json.dumps([
                str((data / "results" / row["job"] / phase / "results.json").relative_to(ROOT))
                for phase in ("0-candidate", "1-candidate")])
            fresh[identity] = value
        for job in config["jobs"]:
            assert job not in jobs
            jobs.add(job)
            for phase in ("0-candidate", "1-candidate"):
                original = data / "results" / job / (phase + ".log")
                destination = HERE / "stdout" / f"{job}-{phase}.log"
                destination.parent.mkdir(exist_ok=True)
                shutil.copyfile(original, destination)
                assert sha(destination) == sha(original)
                logs.append(dict(job=job, phase=phase, source=str(original.relative_to(ROOT)),
                                 path=str(destination.relative_to(HERE)), sha256=sha(original)))
        clocks += read(report / "clock-quartiles.json")
        resources += read(report / "runtime-resources.json")
        summaries.append(summary)
        inputs.append(dict(data=str(data.relative_to(ROOT)), config_sha256=sha(data / "perf-config.json"),
                           report_sha256=sha(report / "cells.csv"), summary_sha256=sha(report / "summary.json")))
    assert len(fresh) == 468 and len(jobs) == 31 and len(logs) == 62
    assert len(clocks) == 3744 and sum(s["samples"] for s in summaries) == 93600
    assert len({s["tracked_manifest_sha256"] for s in source_records}) == 1
    ordered = sorted(fresh.values(), key=lambda r: (r["topology"], next(i for i,m in enumerate(MODELS) if m[0] == r["model"]), MODES.index(r["backend"]), r["tokens"]))
    historical = {key(r) for r in rows(ROOT / "harness/historical/report/cells.csv")}
    assert set(fresh) == historical
    writecsv(HERE / "report/cells.csv", ordered)
    write(HERE / "inputs.json", dict(passed=True, head=HEAD, roots=inputs, jobs=sorted(jobs), fresh_cells=468))
    write(HERE / "source-equivalence.json", dict(passed=True, head=HEAD, measured_sources=source_records,
        tracked_manifest_sha256=source_records[0]["tracked_manifest_sha256"],
        boundary="All468 candidate cells are fresh; source record hashes match merged Git object. Full inventory/source/cache pre/postflight are retained in raw campaign evidence."))

    external_proof, external_groups = {}, {}
    comparison_rows = []
    for topology in ("ep", "tp"):
        oldpath = ROOT / f"harness/historical/external/{topology}/summary-cells.csv"
        old = rows(oldpath)
        revised = []
        for row in old:
            mode = next(c[2] for c in COLUMNS if c[0] == row["column"])
            value = fresh.get((row["model"], topology, mode, int(row["tokens"])))
            current = dict(row)
            current["candidate_spread_percent"] = value["candidate_spread_percent"] if value else ""
            current["current_ms"] = value["candidate_us"] / 1000 if value else ""
            current["current_evidence"] = value["candidate_evidence"] if value else "[]"
            current["speed_percent"] = 100 * (float(row["baseline_ms"]) / current["current_ms"] - 1) if row["status"] == "measured" else ""
            assert all(row[k] == current[k] for k in BASELINE_FIELDS)
            revised.append(current)
            comparison_rows.append(dict(topology=topology, **current))
        folder = HERE / "external" / topology
        writecsv(folder / "summary-cells.csv", revised)
        lines = ["| Model | Tokens | " + " | ".join(c[1] for c in COLUMNS) + " |",
                 "|---|---:|" + "---:|" * len(COLUMNS)]
        lookup = {(r["model"], int(r["tokens"]), r["column"]): r for r in revised}
        for model, label, parallel in MODELS:
            for token in TOKENS[2:]:
                values = [lookup[model, token, c[0]] for c in COLUMNS]
                lines.append(f"| {label} {topology.upper()}{parallel} | {token} | " + " | ".join(
                    f"{r['speed_percent']:+.2f}%" if r["status"] == "measured" else "N/A" for r in values) + " |")
        (folder / "summary-table.md").write_text("\n".join(lines) + "\n")
        write(folder / "provenance.json", dict(complete=True, head=HEAD, baseline_fields_unchanged=True,
              original_csv=str(oldpath.relative_to(ROOT)), original_sha256=sha(oldpath),
              outputs={"summary-cells.csv": sha(folder / "summary-cells.csv")}))
        external_proof[topology] = dict(original_sha256=sha(oldpath), new_sha256=sha(folder / "summary-cells.csv"), rows=len(revised))
        for column, label, _ in COLUMNS:
            values = [r for r in revised if r["column"] == column and int(r["tokens"]) >= 4 and r["status"] == "measured"]
            external_groups[f"{topology}/{column}"] = dict(label=label, cells=len(values),
                speedup_percent=gm([r["speed_percent"] for r in values]), negative=sum(r["speed_percent"] < 0 for r in values))
    writecsv(HERE / "benchmark-comparisons.csv", comparison_rows)
    (HERE / "numerical-tables.md").write_text("# End-to-end historical-baseline comparisons\n\nTokens1/2 are raw only. Positive means faster; all negatives retained.\n\n" + "\n\n".join(
        f"## {t.upper()}\n\n" + (HERE / f"external/{t}/summary-table.md").read_text() for t in ("ep", "tp")))
    available = [q for q in clocks if q["clock"]["available"]]
    summary = dict(passed=True, head=HEAD, fresh_candidate_cells=468, reused_candidate_cells=0,
        displayed_candidate_cells=396, candidate_samples=93600, jobs=31, stdout_logs=62,
        candidate_loaded_functions=len(resources), recorded_default_joins=sum(s["default_stage_resource_joins"] for s in summaries),
        clock_quartiles=3744, missing_clock_quartiles=3744-len(available),
        clock_exception_quartiles=sum(q["clock"]["sm_mhz"]["median"] != 2032 or set(q["clock"]["reasons"]) != {"0"} for q in available),
        max_candidate_spread_percent=max(r["candidate_spread_percent"] for r in ordered), external=external_proof,
        external_groups=external_groups, inputs=inputs, all_negative_rows_retained=True,
        boundary="Fresh merged-head candidate AA only; original historical TRTLLM/non-swap/pre-PR W4 denominators unchanged. Cross-instance comparison, not fresh causal controls. Tables use final pass; plots use geometric two-pass medians.")
    write(HERE / "report/summary.json", summary)
    write(HERE / "report/clock-quartiles.json", clocks)
    write(HERE / "report/runtime-resources.json", resources)
    write(HERE / "stdout/manifest.json", logs)
    write(HERE / "manifest.json", dict(passed=True, head=HEAD, assemble_sha256=sha(__file__),
        report_sha256=sha(HERE / "report/cells.csv"), summary_sha256=sha(HERE / "report/summary.json"),
        stdout_manifest_sha256=sha(HERE / "stdout/manifest.json"), inputs=inputs))
    print(json.dumps({k: summary[k] for k in ("head", "fresh_candidate_cells", "candidate_samples", "clock_exception_quartiles", "missing_clock_quartiles")}, indent=2))


if __name__ == "__main__":
    main()
