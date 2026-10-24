#!/usr/bin/env python3
"""Audit and pool native benchmark captures without averaging run medians."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from run import COMPILED_CACHE_POLICIES, LEGACY_COMPILED_CACHE_POLICY, summarize


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def routing_before_fc2(metadata):
    return metadata.get("apply_routing_weights_before_fc2", metadata.get("apply_topk_in_fc1"))


def capture(path):
    metadata = read(path / "run.json")
    require(metadata.get("complete") is True, f"Incomplete capture: {path}")
    require(metadata.get("knobs") == "auto", f"AUTO-only comparison rejects fixed knobs: {path}")
    require(metadata.get("tactic_policy", "all") in ("all", "mixed-only"), f"Unknown AUTO policy: {path}")
    require(metadata.get("compiled_cache_policy", LEGACY_COMPILED_CACHE_POLICY) in COMPILED_CACHE_POLICIES,
            f"Unknown compiled-cache policy: {path}")
    require(metadata.get("source_unchanged_during_capture") is True, f"Source drift: {path}")
    require(metadata["exit_codes"] == [0] * metadata["sweeps"], f"Failed sweep: {path}")
    require(metadata["pdl"] is True and metadata["fused_tma_reduce"] is False
            and metadata["w4a16_megamoe_fused_deterministic_combine"] is True
            and routing_before_fc2(metadata) is False, f"Execution control drift: {path}")
    rows = read(path / "raw-records.json")
    if metadata.get("benchmark_policy_wrapper_sha256") is not None:
        require(sha(path / "benchmark-policy-wrapper.py") == metadata["benchmark_policy_wrapper_sha256"],
                f"Policy wrapper hash mismatch: {path}")
    if metadata.get("tactic_policy") == "mixed-only":
        winners = [r["value"]["knobs"] for r in rows if r["kind"] == "MEGAMOE_TACTIC_JSON"]
        require(winners and all(tuple(k.get("cluster_shape_mnk", ())) == (4, 1, 1)
                                and tuple(k.get("fallback_cluster_shape_mnk") or ()) == (2, 1, 1)
                                for k in winners), f"mixed-only AUTO winner mismatch: {path}")
    summaries = summarize(rows, metadata["tokens"], metadata["variants"], metadata["sweeps"],
                          metadata["iters"], metadata["warmup"], False)
    saved = read(path / "summary.json")
    require(summaries == saved, f"Raw samples differ from saved summary: {path}")
    require(sha(path / "source-before.patch") == metadata["source_patch_sha256"],
            f"Source patch hash mismatch: {path}")
    fixtures = [r["value"] for r in rows if r["kind"] == "DISTRIBUTED_MODEL_JSON"]
    require(fixtures and all(f == fixtures[0] for f in fixtures), f"Inconsistent fixture: {path}")
    return {"path": str(path), "metadata": metadata, "source": read(path / "source-manifest.json"),
            "fixture": fixtures[0], "summaries": summaries, "rows": rows,
            "sha256": {name: sha(path / name) for name in
                       ("run.json", "raw-records.json", "summary.json", "source-manifest.json")}}


def common_metadata(capture):
    m = capture["metadata"]
    keys = ("model", "tokens", "variants", "image", "runtime_versions", "iters", "warmup", "pdl",
            "fused_tma_reduce", "w4a16_megamoe_fused_deterministic_combine")
    result = {key: m[key] for key in keys}
    result["benchmark_driver_sha256"] = m.get("benchmark_driver_sha256", capture["source"].get("benchmarks/bench_cute_dsl_moe_distributed.py"))
    result["benchmark_policy_wrapper_sha256"] = m.get("benchmark_policy_wrapper_sha256")
    result["compiled_cache_policy"] = m.get("compiled_cache_policy", LEGACY_COMPILED_CACHE_POLICY)
    ignored_environment = {"PYTHONPATH", "FLASHINFER_WORKSPACE_BASE", "CUTE_DSL_CACHE_DIR", "CUDA_CACHE_PATH",
                           "TRITON_CACHE_DIR", "CUTE_DSL_DUMP_DIR", "K3_SOURCE_DIR", "MIXED_CLUSTER_SOURCE_DIR"}
    result["controlled_environment"] = {key: value for key, value in m["environment"].items()
                                        if key not in ignored_environment}
    return result


def pool(captures, variant, token):
    samples = []
    processes = []
    for c in captures:
        point = next(p for p in c["summaries"] if p["variant"] == variant and p["global_tokens"] == token)
        samples.extend(point["samples_ms"])
        tactics = [r for r in c["rows"] if r["kind"] == "MEGAMOE_TACTIC_JSON"
                   and r["value"]["global_tokens"] == token and r["value"]["variant"] == variant]
        processes.append({"path": c["path"], "arm": c["metadata"]["arm"],
                          "sweep_medians_us": point["sweep_medians_us"], "tactic_receipts": tactics,
                          "requested_knobs": c["metadata"]["knobs"],
                          "tactic_policy": c["metadata"].get("tactic_policy", "all"),
                          "candidate_counts": c["metadata"].get("candidate_counts")})
    q1, _, q3 = statistics.quantiles(samples, n=4, method="inclusive")
    return {"sample_count": len(samples), "median_us": statistics.median(samples) * 1000,
            "p25_us": q1 * 1000, "p75_us": q3 * 1000, "min_us": min(samples) * 1000,
            "max_us": max(samples) * 1000, "samples_ms": samples, "processes": processes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, nargs="+", required=True)
    parser.add_argument("--candidate", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True, help="New JSON report, never overwritten")
    args = parser.parse_args()
    require(not args.output.exists(), "Use a fresh output path")
    baseline = [capture(p.resolve()) for p in args.baseline]
    candidate = [capture(p.resolve()) for p in args.candidate]
    all_captures = baseline + candidate
    expected = common_metadata(baseline[0])
    for c in all_captures:
        require(common_metadata(c)["compiled_cache_policy"] == expected["compiled_cache_policy"],
                f"Compiled-cache policy mismatch: {c['path']}")
        require(common_metadata(c) == expected, f"Runtime/workload/protocol mismatch: {c['path']}")
        require(c["fixture"] == baseline[0]["fixture"], f"Fixture/seed mismatch: {c['path']}")
    for arm in (baseline, candidate):
        for c in arm[1:]:
            require(c["source"] == arm[0]["source"], f"Same-arm source changed: {c['path']}")
            require(c["metadata"]["knobs"] == arm[0]["metadata"]["knobs"], f"Same-arm knob policy changed: {c['path']}")
            require(c["metadata"].get("tactic_policy", "all") == arm[0]["metadata"].get("tactic_policy", "all"), f"Same-arm AUTO policy changed: {c['path']}")
    source_a, source_b = baseline[0]["source"], candidate[0]["source"]
    differences = sorted(p for p in source_a.keys() | source_b.keys() if source_a.get(p) != source_b.get(p))
    # The effective driver can be shared via --driver while each library checkout stays pristine.
    # Its hash is matched above; all other benchmark/timer sources must still match.
    native_driver = "benchmarks/bench_cute_dsl_moe_distributed.py"
    require(not any((p.startswith("benchmarks/") and p != native_driver) or p.startswith("flashinfer/testing/") for p in differences),
            "Benchmark/timer sources differ across arms; establish equivalence before comparison")
    points = []
    for variant in expected["variants"]:
        for token in expected["tokens"]:
            a, b = pool(baseline, variant, token), pool(candidate, variant, token)
            points.append({"variant": variant, "global_tokens": token, "baseline": a, "candidate": b,
                           "speedup": a["median_us"] / b["median_us"]})
    aggregates = {}
    for variant in expected["variants"]:
        aggregates[variant] = {}
        for name, predicate in (("retention_T4plus", lambda t: t >= 4),
                                ("decode_T4to512", lambda t: 4 <= t <= 512),
                                ("prefill_T4096plus", lambda t: t >= 4096)):
            eligible = [p for p in points if p["variant"] == variant and predicate(p["global_tokens"])]
            if eligible:
                aggregates[variant][name] = {"tokens": [p["global_tokens"] for p in eligible],
                    "geomean_speedup": math.exp(statistics.mean(math.log(p["speedup"]) for p in eligible))}
    report = {"protocol": expected, "fixture": baseline[0]["fixture"], "points": points,
              "aggregates": aggregates, "changed_source_files": differences,
              "inputs": [{"path": c["path"], "sha256": c["sha256"],
                          "commit": c["metadata"]["source_commit"]} for c in all_captures],
              "statistical_boundary": "Descriptive raw-sample pooling; not an independence or significance claim."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("tokens\tbaseline_us\tcandidate_us\tspeedup")
    for p in points:
        print(f"{p['global_tokens']}\t{p['baseline']['median_us']:.4f}\t{p['candidate']['median_us']:.4f}\t{p['speedup']:.5f}")
    print(json.dumps(aggregates, indent=2))


if __name__ == "__main__":
    main()
