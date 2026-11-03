"""Independently replay fresh CUPTI spans and structured publication joins, CPU only."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEAD = "2b4732791a3ce48bc3ae6c030a283fab73854e0e"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def close(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-9), (a, b)


def main():
    inputs = read(HERE / "inputs.json")
    assert inputs["passed"] and inputs["head"] == HEAD
    values, final_records, file_hashes = {}, {}, {}
    candidate_phases_by_key = {}
    samples = measurements = candidate_samples = 0
    for item in inputs["roots"]:
        data = ROOT / item["data"]
        config = read(data / "perf-config.json")
        assert sha(data / "perf-config.json") == item["config_sha256"]
        assert config["phases"] == ["control", "candidate", "candidate", "control"]
        candidate_phases = [f"{i}-{role}" for i, role in enumerate(config["phases"]) if role == "candidate"]
        for name, job in config["jobs"].items():
            topology = "tp" if job["tp"] > 1 else "ep"
            for phase in (f"{i}-{role}" for i, role in enumerate(config["phases"])):
                path = data / "results" / name / phase / "results.json"
                result = read(path)
                assert result["complete"] and result["exit_code"] == 0
                file_hashes[str(path.relative_to(ROOT))] = sha(path)
                flat = [(row, value) for row in result["rows"] for value in row["results"]]
                native = result["native_diagnostic"]["measurements"]
                assert len(flat) == len(native)
                for (row, record), m in zip(flat, native):
                    assert m["timer"] == "CUPTI" and m["event_fallback_forbidden"]
                    assert len(m["milliseconds"]) == len(m["iter_timestamps"]) == 100
                    for reported, (begin, end) in zip(m["milliseconds"], m["iter_timestamps"]):
                        correlation = {x[2] for x in m["launches"] if begin <= x[0] <= end}
                        activity = [x for x in m["activities"] if x[3] in correlation]
                        assert activity
                        span = (max(x[2] for x in activity) - min(x[1] for x in activity)) / 1e6
                        close(span, reported)
                        samples += 1
                        candidate_samples += phase in candidate_phases
                    median = statistics.median(m["milliseconds"])
                    close(median, m["median_ms"])
                    close(median, record["latency_ms"])
                    assert record["tokens"] == row["tokens"]
                    identity = (job["model"], topology, record["backend"], row["tokens"])
                    assert phase not in values.setdefault(identity, {})
                    values[identity][phase] = median * 1000
                    candidate_phases_by_key[identity] = candidate_phases
                    if phase == candidate_phases[-1]:
                        final_records[identity] = record
                    measurements += 1
    assert (len(values), samples, measurements) == (468, 187200, 1872)
    printed = rows(HERE / "report/cells.csv")
    assert len(printed) == 468
    for row in printed:
        identity = row["model"], row["topology"], row["backend"], int(row["tokens"])
        phases = values[identity]
        a, b = (phases[p] for p in candidate_phases_by_key[identity])
        close(a, row["a1_us"])
        close(b, row["a2_us"])
        close(math.exp((math.log(a) + math.log(b)) / 2), row["candidate_us"])
        close(100 * (max(a, b) / min(a, b) - 1), row["candidate_spread_percent"])
        control = [value for phase, value in phases.items() if phase.endswith("-control")]
        assert len(control) == 2
        close(control[0], row["c1_us"])
        close(control[1], row["c2_us"])
        close(math.sqrt(math.prod(control)), row["control_us"])
        close(100 * (max(control) / min(control) - 1), row["control_spread_percent"])
        close(100 * (math.sqrt(math.prod(control) / (a * b)) - 1), row["speedup_percent"])

    modes = {"w4a4": "W4A4", "per_token": "PER-TOKEN", "mxfp4x8": "MXFP4x8",
             "mxfp8": "MXFP8", "w4a16": "W4A16"}
    unchanged = ["model", "tokens", "column", "baseline", "status", "baseline_ms", "reason", "baseline_evidence"]
    external_cells = external_measured = negatives = 0
    plots = {}
    for topology in ("ep", "tp"):
        old = rows(ROOT / f"harness/historical/external/{topology}/summary-cells.csv")
        newpath = HERE / f"external/{topology}/summary-cells.csv"
        new = rows(newpath)
        assert len(old) == len(new) == 468
        expected_plot = {}
        for before, after in zip(old, new):
            assert all(before[k] == after[k] for k in unchanged)
            mode = after["column"].removeprefix("trtllm_").removeprefix("legacy_")
            identity = after["model"], topology, "CuteDSL " + modes[mode], int(after["tokens"])
            if identity in values:
                a, b = (values[identity][p] for p in candidate_phases_by_key[identity])
                current = math.sqrt(a * b) / 1000
                close(current, after["current_ms"])
            else:
                assert after["current_ms"] == "" and after["status"] == "unsupported"
            if after["status"] == "measured":
                delta = 100 * (float(after["baseline_ms"]) / current - 1)
                close(delta, after["speed_percent"])
                if int(after["tokens"]) >= 4:
                    external_measured += 1
                    negatives += delta < 0
            if int(after["tokens"]) >= 4:
                expected_plot[after["model"], int(after["tokens"]), after["column"]] = after
            external_cells += 1
        manifest = read(HERE / f"plots/plot-manifest-{topology}.json")
        assert manifest["source_sha256"] == sha(newpath)
        assert manifest["commit_label"] == HEAD[:8] and manifest["topology"] == topology
        assert len(manifest["cells"]) == len(expected_plot) == 396
        for cell in manifest["cells"]:
            row = expected_plot[cell["model"], int(cell["tokens"]), cell["column"]]
            assert cell["status"] == row["status"]
            if row["status"] == "measured":
                close(cell["percent"], row["speed_percent"])
                close(cell["ratio"], float(row["baseline_ms"]) / float(row["current_ms"]))
        for name, digest in manifest["outputs"].items():
            path = HERE / "plots" / name
            assert sha(path) == digest
            plots[str(path.relative_to(HERE))] = digest

    tables = read(HERE / "completed-tables/manifest.json")
    assert tables["passed"] and tables["head"] == HEAD
    candidate_count = historical_count = 0
    for group in tables["groups"]:
        if group.get("skipped"):
            continue
        assert sha(HERE / "completed-tables" / group["table"]) == group["table_sha256"]
        for row in group["rows"]:
            for record in row["results"]:
                if record["backend"].startswith("CuteDSL"):
                    identity = group["model"], group["topology"], record["backend"], row["tokens"]
                    assert record == final_records[identity]
                    candidate_count += 1
                else:
                    assert record["backend"].startswith("TRTLLM")
                    historical_count += 1
    assert (candidate_count, historical_count) == (468, 390)
    summary = read(HERE / "report/summary.json")
    assert summary["candidate_samples"] == candidate_samples and summary["fresh_candidate_cells"] == len(values)
    receipt = dict(passed=True, head=HEAD, samples=samples, candidate_samples=candidate_samples, phase_medians=measurements,
        fresh_cells=len(values), reused_candidate_cells=0, displayed_candidate_cells=396,
        external_rows=external_cells, displayed_measured_comparisons=external_measured,
        displayed_negative_comparisons=negatives, unchanged_baseline_fields=unchanged,
        native_candidate_records=candidate_count, historical_trt_records=historical_count,
        inputs=file_hashes, cells_sha256=sha(HERE / "report/cells.csv"),
        table_manifest_sha256=sha(HERE / "completed-tables/manifest.json"),
        baseline_index_sha256=sha(HERE / "completed-tables/baseline-index.json"),
        plots=plots, verifier_sha256=sha(__file__),
        boundary="Independent CPU arithmetic/structured-join replay. Visual inspection belongs to a separate receipt; source, routing, resource and clock raw audits remain separately preserved.")
    (HERE / "numeric-validation.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("passed", "samples", "fresh_cells", "displayed_negative_comparisons")}))


if __name__ == "__main__":
    main()
