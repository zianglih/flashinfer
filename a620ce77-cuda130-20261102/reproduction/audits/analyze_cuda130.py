"""Independently replay fresh CAAC CUPTI evidence; write only audit artifacts.

Usage: python3 analyze_cuda130.py DATA_ROOT --output AUDIT_OUTPUT
DATA_ROOT contains results/JOB/receipt.json (or is the results directory).
Historical timings never enter this report. Times use the geometric mean of
the two phase medians per arm; positive speedup means the retained PR is faster.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
TOKENS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384]
MODEL_NAMES = {"v3": "V3", "v41-flash": "V41F", "kimi-k3": "K3", "nemo3-ultra": "N3U"}
HEADS = {"before": "002529e17b22567a071091053c6c4dc2a55e050e",
         "after": "a620ce7790b32f7f0ae524a811417d2c6cee1152"}
MED = statistics.median


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def geo(values):
    return math.exp(statistics.mean(math.log(v) for v in values))


def choices(measurement):
    return sorted({json.dumps({k: h[k] for k in ("key", "runner", "tactic")}, sort_keys=True)
                   for h in measurement["cache_hits"]})


def routing(row):
    return {k: v for k, v in row["routing_identity"].items() if k != "capture"}


def kernel_components(kernels):
    names, counts = [], collections.Counter()
    for kernel in kernels:
        name = kernel[0]
        if "Sm100W4A16GroupedGemmKernel" in name:
            counts["gemm"] += 1
            component = f"fc{counts['gemm']}"
        elif "routingInitExpertCounts" in name:
            component = "route_init"
        elif "topk_kernel" in name:
            component = "route_topk"
        elif "routingIndices" in name:
            component = "route_sort"
        elif "MoeFinalizeKernel" in name:
            component = "combine"
        else:
            counts["other"] += 1
            component = f"other_{counts['other']}"
        assert "Quantize" not in name, name
        names.append((component, kernel))
    assert counts["gemm"] == 2, [k[0] for k in kernels]
    return names


def replay_measurement(measurement, telemetry):
    assert measurement["timer"] == "CUPTI" and measurement["event_fallback_forbidden"]
    times = measurement["milliseconds"]
    assert len(times) == len(measurement["iter_timestamps"]) == 100
    assert all(math.isfinite(v) and v > 0 for v in times)
    assert MED(times) == measurement["median_ms"]
    assert measurement.get("profile_calls_before", 0) == measurement.get("profile_calls_after", 0) == 0
    samples, kernel_names = [], set()
    for ms, (begin, end) in zip(times, measurement["iter_timestamps"]):
        correlations = {launch[2] for launch in measurement["launches"] if begin <= launch[0] <= end}
        kernels = sorted((kernel for kernel in measurement["activities"] if kernel[3] in correlations), key=lambda k: k[1])
        assert 4 <= len(kernels) <= 10, len(kernels)
        first, last = min(k[1] for k in kernels), max(k[2] for k in kernels)
        assert math.isclose((last - first) / 1e6, ms, abs_tol=1e-12)
        sample = dict(e2e_us=ms * 1000, begin_ns=first, end_ns=last)
        frontier = first
        for name, kernel in kernel_components(kernels):
            kernel_names.add(kernel[0])
            sample[name + "_us"] = (kernel[2] - kernel[1]) / 1000
            sample[name + "_extension_us"] = max(0, kernel[2] - max(frontier, kernel[1])) / 1000
            sample[name + "_gap_us"] = max(0, kernel[1] - frontier) / 1000
            frontier = max(frontier, kernel[2])
        assert math.isclose(sum(v for k, v in sample.items() if k.endswith(("_extension_us", "_gap_us"))), sample["e2e_us"], abs_tol=1e-8)
        samples.append(sample)
    begin, end = min(s["begin_ns"] for s in samples), max(s["end_ns"] for s in samples)
    clocks = [t for t in telemetry if begin <= t["start"]["cupti_ns"] <= end]
    clock_summary = dict(samples=len(clocks), available=bool(clocks))
    if clocks:
        clock_summary.update({k: dict(min=min(t[k] for t in clocks), median=MED(t[k] for t in clocks), max=max(t[k] for t in clocks))
                              for k in ("sm_mhz", "memory_mhz", "power_mw", "temperature_c")})
        clock_summary["event_reasons"] = dict(collections.Counter(str(t["clocks_event_reasons"]) for t in clocks))
    common = set.intersection(*(set(s) for s in samples))
    return dict(raw_samples=len(samples), medians={k: MED(s[k] for s in samples) for k in sorted(common) if k.endswith("_us")},
                kernel_names=sorted(kernel_names), clocks=clock_summary)


def audit_current_registers(root, label, source, measurements):
    receipts = list((root / "register-guard" / label).glob("*/receipt.json"))
    assert len(receipts) == 1
    guard = load(receipts[0])
    assert guard["all_guarded"] and guard["exitstatus"] == 0 and not guard["compiler_options_changed"]
    assert guard["kernel_sha256"] == source["source_sha256"]["flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py"]
    assert guard["policy"] == {"control": 80, "gather": 64, "epilogue": 144}
    compiled = {c["library_handle"]: c for c in guard["compilations"]}
    assert len(compiled) == len(guard["compilations"])
    for item in compiled.values():
        assert item["passed"] and all(item["checks"].values())
        assert item["analysis"]["local_bytes"] == 0 and item["analysis"]["binary_version"] == 103
        assert item["launch_threads"] == item["analysis"]["max_threads"]
        if item["gather_input"]:
            assert item["launch_threads"] == 640 and item["initial_regs"] == 96
            assert item["required_pool"] <= item["available_initial_pool"] == 61440
        else:
            assert item["launch_threads"] == 512
    libraries = set()
    for measure in measurements:
        for config in measure["w4_resolved_configs"]:
            item = compiled[config["compiled_library"]]
            libraries.add(config["compiled_library"])
            assert item["gather_input"] == (config["stage"] == "fc1")
            for key in ("mma_tiler_mnk", "cluster_shape_mn", "raster_along_m", "use_clc_scheduler", "enable_pdl"):
                assert item[key] == config[key]
    return dict(receipt_sha256=sha(receipts[0]), guarded_compilations=len(compiled),
                selected_libraries=len(libraries), local_bytes=0,
                boundary="Fresh current-arm CUDA driver attributes joined to exact resolved callable library handles; no SASS inspection or before-arm register claim.")


def analyze_job(root):
    receipt = load(root / "receipt.json")
    assert receipt["complete"] and len(receipt["phases"]) == 4
    assert [p["role"] for p in receipt["phases"]] == ["before", "after", "after", "before"]
    assert set(receipt["tokens"]) <= set(TOKENS)
    for role, head in HEADS.items():
        assert receipt["sources"][role]["head"] == head
    expected = {role: load(HERE.parent / "harness/frozen" / root.name / (role + "-expected.json")) for role in HEADS}
    expected_choices = {role: {r["tokens"]: choices(m) for r, m in zip(d["rows"], d["native_diagnostic"]["measurements"])} for role, d in expected.items()}
    phase_rows, routes, register_guards = [], {}, {}
    uuids = set()
    for phase in receipt["phases"]:
        assert phase["verified"] and phase["returncode"] == 0
        role, label = phase["role"], f"{phase['index']}-{phase['role']}"
        path = root / label / "results.json"
        assert sha(path) == phase["results_sha256"]
        assert sha(root / (label + ".log")) == phase["stdout_sha256"]
        for key in ("gpu_before", "gpu_after"):
            uuids.add(phase[key].split(",")[0].strip())
        data = load(path)
        assert data["complete"] and data["exit_code"] == 0
        assert data["swap_ab"] == (role == "after") and not data["use_fused_finalize"]
        assert data["profile_calls"] == 0 and not data["native_diagnostic"]["admitted_tactics"]
        assert data["benchmark_sha256"] == receipt["sources"][role]["source_sha256"]["benchmarks/bench_moe_deepseek.py"]
        assert [r["tokens"] for r in data["rows"]] == receipt["tokens"]
        telemetry_root = root / "telemetry" / label
        telemetry_receipt = load(telemetry_root / "receipt.json")
        assert telemetry_receipt["complete"] and telemetry_receipt["returncode"] == 0
        telemetry = [json.loads(line) for line in (telemetry_root / "samples.jsonl").read_text().splitlines()]
        measurements = data["native_diagnostic"]["measurements"]
        assert len(measurements) == len(data["rows"])
        if role == "after":
            register_guards[label] = audit_current_registers(root, label, receipt["sources"][role], measurements)
        for row, measure in zip(data["rows"], measurements):
            token = row["tokens"]
            assert row["backend_labels"] == ["CuteDSL W4A16"] and len(row["results"]) == 1
            assert not row["arm_contracts"]["CuteDSL W4A16"]["initial_activation_quantization_timed"]
            assert row["results"][0]["latency_ms"] == measure["median_ms"]
            assert all(h["hit"] for h in measure["cache_hits"])
            assert choices(measure) == expected_choices[role][token]
            if role == "after":
                resolved = measure["w4_resolved_configs"]
                assert len(resolved) == 2 and {r["stage"] for r in resolved} == {"fc1", "fc2"}
                default = [[[256, 128, 256], [2, 1], True], [[256, 128, 256], [2, 1], True]]
                assert measure["w4_default_tactic"] == default
                observed_choices = {json.dumps(h["tactic"]) for h in measure["cache_hits"]}
                assert len(observed_choices) == 1
                chosen = json.loads(next(iter(observed_choices)))
                for config in resolved:
                    assert config["tokens"] == token
                    assert config["supplied_moe_tactic"] == (None if chosen == -1 else chosen)
                    assert config["resolved_moe_tactic"] == (default if chosen == -1 else chosen)
                    tile, cluster, raster = config["resolved_moe_tactic"][0 if config["stage"] == "fc1" else 1]
                    assert (config["mma_tiler_mnk"], config["cluster_shape_mn"], config["raster_along_m"]) == (tile, cluster, raster)
                    assert config["enable_pdl"] is True
                    assert isinstance(config["use_clc_scheduler"], bool)
                    if config["stage"] == "fc2":
                        assert config["use_clc_scheduler"] is False
                for filename, digest in measure["w4_resolution_source_sha256"].items():
                    suffix = ("blackwell/" if filename == "moe_w4a16.py" else "") + filename
                    assert digest == receipt["sources"][role]["source_sha256"]["flashinfer/fused_moe/cute_dsl/" + suffix]
            routes.setdefault(token, routing(row))
            assert routes[token] == routing(row), (root.name, token, "fresh routing mismatch")
            replay = replay_measurement(measure, telemetry)
            phase_rows.append(dict(phase=label, role=role, token=token, result_sha256=sha(path),
                                   winner=choices(measure), resolved_w4_configs=measure.get("w4_resolved_configs"), **replay))
    assert len(uuids) == 1, uuids
    cells = []
    for token in receipt["tokens"]:
        selected = [p for p in phase_rows if p["token"] == token]
        arms = {role: [p for p in selected if p["role"] == role] for role in HEADS}
        assert all(len(p) == 2 for p in arms.values())
        times = {role: [p["medians"]["e2e_us"] for p in phases] for role, phases in arms.items()}
        means = {role: geo(t) for role, t in times.items()}
        cells.append(dict(job=root.name, model=receipt["job"]["model"], ep=receipt["job"]["ep"], tp=receipt["job"]["tp"], token=token,
            retention=token > 2, before_us=means["before"], after_us=means["after"], speedup_percent=(means["before"] / means["after"] - 1) * 100,
            repeat_spread_percent={role: (max(t) / min(t) - 1) * 100 for role, t in times.items()},
            conservative_speedup_percent=(min(times["before"]) / max(times["after"]) - 1) * 100,
            phase_us=times, gpu_uuid=next(iter(uuids)),
            historical_route_matches={p["role"] + str(p["index"]): p["historical_routing_matches"][str(token)] for p in receipt["phases"]}))
    return dict(job=root.name, receipt_sha256=sha(root / "receipt.json"), cells=cells, phases=phase_rows, register_guards=register_guards)


def write_report(jobs, output):
    output.mkdir(parents=True, exist_ok=True)
    cells = [c for j in jobs for c in j["cells"]]
    retained = [c for c in cells if c["retention"]]
    stats = {}
    for topology in ("all", "ep", "tp"):
        for group in ("all", "decode", "prefill"):
            selected = [c for c in retained if (topology == "all" or c[topology] > 1)
                        and (group == "all" or (c["token"] <= 512 if group == "decode" else c["token"] >= 4096))]
            if selected:
                stats[topology + "_" + group] = dict(cells=len(selected), speedup_percent=(geo(c["before_us"] / c["after_us"] for c in selected) - 1) * 100,
                    worst=min(c["speedup_percent"] for c in selected), best=max(c["speedup_percent"] for c in selected),
                    regressions=sum(c["speedup_percent"] < 0 for c in selected))
    summary = dict(complete=True, jobs=len(jobs), cells=len(cells), retention_cells=len(retained),
        raw_samples=sum(p["raw_samples"] for j in jobs for p in j["phases"]), stats=stats,
        boundary="Fresh same-environment CUDA13.0 CAAC fixed per-arm historical tactics, strict CUPTI span replay. Positive speedup=(before/after-1)*100. Decode4..512, prefill4096/8192/16384. Tokens1/2 retained raw but excluded from aggregates/table. Clock and repeat evidence is preserved; no automatic clock-based data exclusion.")
    (output / "audit.json").write_text(json.dumps(dict(summary=summary, jobs=jobs), indent=2) + "\n")
    fields = ["job", "token", "retention", "before_us", "after_us", "speedup_percent", "conservative_speedup_percent", "before_repeat_percent", "after_repeat_percent", "gpu_uuid"]
    with (output / "cells.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for c in cells:
            writer.writerow({key: (c["repeat_spread_percent"][key.split("_")[0]] if key.endswith("_repeat_percent") else c[key]) for key in fields})
    lines = ["| Model | Tokens | Before (µs) | After (µs) | Speedup |", "|---|---:|---:|---:|---:|"]
    for c in retained:
        topology = f"EP{c['ep']}" if c["ep"] > 1 else f"TP{c['tp']}"
        lines.append(f"| {MODEL_NAMES[c['model']]} {topology} | {c['token']} | {c['before_us']:.3f} | {c['after_us']:.3f} | {c['speedup_percent']:+.2f}% |")
    (output / "table.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    data = args.data / "results" if (args.data / "results").is_dir() else args.data
    roots = sorted(path.parent for path in data.glob("*/receipt.json") if load(path).get("complete"))
    assert roots, "No complete CAAC jobs"
    jobs = [analyze_job(root) for root in roots]
    if not args.allow_partial:
        assert len(jobs) == 8 and sum(len(j["cells"]) for j in jobs) == 104
    write_report(jobs, args.output)
