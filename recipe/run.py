#!/usr/bin/env python3
"""Serial performance-only W4A16 mixed-cluster EP8 runs through FlashInfer's native benchmark.

No refcheck, pytest, or correctness kernel is launched here. Installation is
separate; the native driver's --model preset provides the workload directly.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.metadata as md
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import statistics
import subprocess
import sys

DEFAULT_TOKENS = "1,2,4,8,16,32,64,128,256,512,4096,8192,16384"
VALID_VARIANTS = {"w4a4", "w4a16", "w4a4_megamoe", "w4a16_megamoe"}
LEGACY_COMPILED_CACHE_POLICY = "cache-root-v1"
SPLIT_COMPILED_CACHE_POLICY = "separate-flashinfer-workspace-v1"
COMPILED_CACHE_POLICIES = {LEGACY_COMPILED_CACHE_POLICY, SPLIT_COMPILED_CACHE_POLICY}
PREFIX = re.compile(r"(DISTRIBUTED_TIMING_SAMPLES_JSON|DISTRIBUTED_ROUTING_JSON|DISTRIBUTED_MODEL_JSON|MEGAMOE_TACTIC_JSON|MEGAMOE_POLICY_JSON),")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(source, *args):
    return subprocess.check_output(["git", "-C", str(source), *args], text=True)


def source_manifest(source):
    names = git(source, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "flashinfer", "benchmarks").split("\0")
    return {name: digest(source / name) for name in names if name and (source / name).is_file()}


def compiled_cache_settings(cache_root, workspace_base=None):
    """Resolve cache paths without importing CUDA or creating directories."""
    cache = Path(cache_root).resolve()
    workspace = Path(workspace_base).resolve() if workspace_base is not None else cache / "flashinfer"
    environment = {
        "FLASHINFER_WORKSPACE_BASE": str(workspace),
        "CUTE_DSL_CACHE_DIR": str(cache / "cute-dsl"),
        "CUDA_CACHE_PATH": str(cache / "cuda-driver"),
        "TRITON_CACHE_DIR": str(cache / "triton"),
    }
    policy = SPLIT_COMPILED_CACHE_POLICY if workspace_base is not None else LEGACY_COMPILED_CACHE_POLICY
    return environment, policy


def parse_rows(log, sweep):
    decoder = json.JSONDecoder()
    rows = []
    # Rank output can concatenate JSON records without line breaks.
    for line in log.read_text(errors="replace").splitlines():
        for match in PREFIX.finditer(line):
            try:
                value, _ = decoder.raw_decode(line[match.end():])
            except json.JSONDecodeError as error:
                raise ValueError(f"Malformed structured record in {log}: {line[:200]}") from error
            rows.append({"kind": match.group(1), "sweep": sweep, "value": value})
    return rows


def summarize(rows, tokens, variants, sweeps, iters, warmup, apply_routing_weights_before_fc2):
    result = []
    for variant in variants:
        for tokens_n in tokens:
            matching = [row for row in rows if row["kind"] == "DISTRIBUTED_TIMING_SAMPLES_JSON"
                        and row["value"]["profile_label"] == f"ep::{variant}"
                        and row["value"]["global_tokens"] == tokens_n]
            if sorted(row["sweep"] for row in matching) != list(range(1, sweeps + 1)):
                raise ValueError(f"Missing/duplicate timing record: {variant} T{tokens_n}")
            samples = []
            for row in matching:
                record = dict(row["value"])
                # The current benchmark renamed this field; accept historical captures for audit.
                if "apply_routing_weights_before_fc2" not in record and "apply_topk_in_fc1" in record:
                    record["apply_routing_weights_before_fc2"] = record["apply_topk_in_fc1"]
                expected = {"timer": "cupti", "world_size": 8, "cuda_graph": True,
                            "cold_l2_cache": True, "precomputed_routing": True,
                            "apply_routing_weights_before_fc2": apply_routing_weights_before_fc2, "sample_aggregation": "per_iteration_rank_max",
                            "repeat_iters": iters, "sample_count": iters, "warmup_iters": warmup}
                if any(record.get(key) != value for key, value in expected.items()):
                    raise ValueError(f"Native timing contract drift: {record}")
                values = record["samples_ms"]
                if len(values) != iters or any(not math.isfinite(v) or v <= 0 for v in values):
                    raise ValueError("Missing or invalid raw timing samples")
                samples.extend(values)
            result.append({"variant": variant, "global_tokens": tokens_n,
                           "sample_count": len(samples), "median_us": 1000 * statistics.median(samples),
                           "sweep_medians_us": [1000 * statistics.median(r["value"]["samples_ms"]) for r in matching],
                           "min_us": 1000 * min(samples), "max_us": 1000 * max(samples),
                           "samples_ms": samples})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New result directory; never overwritten")
    parser.add_argument("--driver", type=Path, help="Use this exact benchmark driver with source selected through PYTHONPATH")
    parser.add_argument("--tactic-policy", choices=("all", "mixed-only"), default="all", help="Project wrapper's AUTO candidate policy; native timing remains unchanged")
    parser.add_argument("--arm", required=True, help="Provenance label, e.g. baseline or situ-exp2")
    parser.add_argument("--model", required=True, help="Native distributed benchmark model preset")
    parser.add_argument("--policy", required=True, help="Recorded AUTO source/catalog policy")
    parser.add_argument("--apply-routing-weights-before-fc2", action="store_true", help="Match the native model routing-weight placement")
    parser.add_argument("--tokens", default=DEFAULT_TOKENS)
    parser.add_argument("--variants", default="w4a16_megamoe")
    parser.add_argument("--knobs", choices=("auto",), default="auto", help="Native AUTO policy; fixed-tactic performance arms are disabled")
    parser.add_argument("--iters", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--sweeps", type=int, default=1)
    parser.add_argument("--port", type=int, default=29500)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--workspace-base", type=Path, help="Separate persistent FlashInfer workspace for this checkout; other caches still use --cache-root")
    parser.add_argument("--image", required=True, help="Exact newly selected image tag or digest; recorded as supplied")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    recipe = Path(__file__).resolve().parent
    policy_wrapper = recipe / "policy_driver.py"
    driver = args.driver.resolve() if args.driver else source / "benchmarks/bench_cute_dsl_moe_distributed.py"
    tokens = [int(value) for value in args.tokens.split(",")]
    variants = args.variants.split(",")
    if (len(tokens) != len(set(tokens)) or any(value <= 0 for value in tokens)
            or len(variants) != len(set(variants)) or not set(variants) <= VALID_VARIANTS
            or min(args.iters, args.sweeps, args.warmup) <= 0):
        parser.error("Use distinct positive tokens, supported variants, and positive counts")
    knobs = args.knobs
    if args.tactic_policy == "mixed-only" and variants != ["w4a16_megamoe"]:
        parser.error("mixed-only policy is scoped to w4a16_megamoe")
    command = ["torchrun", "--master-addr=127.0.0.1", f"--master-port={args.port}", "--nproc-per-node=8",
               str(policy_wrapper), "--native-driver", str(driver), "--tactic-policy", args.tactic_policy,
               "--", "--model", args.model,
               "--mode", "benchmark", "--parallel-modes", "ep",
               "--num-gpus", "8", "--variants", args.variants, "--num-tokens", args.tokens,
               "--timing", "cupti", "--cuda-graph", "--precomputed-routing", "--no-fused-finalize",
               "--warmup", str(args.warmup), "--iters", str(args.iters), "--log-timing-samples"]
    if args.apply_routing_weights_before_fc2:
        command.append("--apply-routing-weights-before-fc2")
    if any(variant.endswith("_megamoe") for variant in variants):
        command += ["--megamoe-knobs", knobs]
    print(shlex.join(command), flush=True)
    if args.dry_run:
        return 0
    if sys.platform != "linux":
        parser.error("Collection requires the prepared Linux GPU container")
    cache = (args.cache_root or source.parent / "compile-cache" / source.name).resolve()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("FLASHINFER_NVFP4_4OVER6")}
    for name in ("FLASHINFER_DISABLE_JIT", "FLASHINFER_DISABLE_VERSION_CHECK", "CUTE_DSL_DISABLE_FILE_CACHING",
                 "CUTE_DSL_DUMP_DIR", "CUTE_DSL_KEEP", "CUTE_DSL_KEEP_PTX", "CUTE_DSL_KEEP_CUBIN",
                 "MEGA_NO_DIST", "MEGA_SINGLE_GPU_GLOO", "MEGA_USE_NCU",
                 "RANK", "WORLD_SIZE", "LOCAL_RANK", "LOCAL_WORLD_SIZE",
                 "GROUP_RANK", "ROLE_RANK", "MASTER_ADDR", "MASTER_PORT"):
        env.pop(name, None)
    env.update({"MIXED_CLUSTER_SOURCE_DIR": str(source), "PYTHONPATH": str(source), "PYTHONUNBUFFERED": "1",
                "CUDA_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7", "BUILD_NVEP": "0", "BUILD_NIXL_EP": "0", "BUILD_NCCL_EP": "0", "MAX_JOBS": "8",
                "FLASHINFER_BUILD_NO_PIP": "1", "FLASHINFER_DIST_AWARE_AUTOTUNE": "0",
                "FLASHINFER_MOE_EP_KNOB_CACHE": "0",
                "FLASHINFER_NVFP4_4OVER6": "1", "FLASHINFER_NVFP4_4OVER6_E4M3_USE_256": "1",
                "FLASHINFER_NVFP4_4OVER6_ERR_MODE": "MSE", "FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH": "1",
                "FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH": "1", "CUTE_DSL_NO_CACHE": "0",
                "FLASHINFER_CUTE_DSL_DISABLE_CACHE": "0", "CUDA_CACHE_DISABLE": "0",
                "CUDA_HOME": "/usr/local/cuda", "CUDA_MODULE_LOADING": "LAZY"})
    cache_environment, cache_policy = compiled_cache_settings(cache, args.workspace_base)
    env.update(cache_environment)
    for path in cache_environment.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    warning = "error:CUPTI is not installed:UserWarning"
    env["PYTHONWARNINGS"] = env.get("PYTHONWARNINGS", "") + ("," if env.get("PYTHONWARNINGS") else "") + warning
    # A source-wide lock prevents simultaneous arms and cache/source mutations
    # by another invocation of this recipe. Keep candidate edits outside runs.
    lock_path = source.parent / ".mixed-cluster-perf.lock"
    inherited_fd = os.environ.get("MIXED_CLUSTER_PERF_LOCK_FD")
    if inherited_fd is None:
        lock = lock_path.open("a+")
    else:
        lock = os.fdopen(os.dup(int(inherited_fd)), "a+")
        actual, expected = os.fstat(lock.fileno()), lock_path.stat()
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino):
            raise RuntimeError("Inherited performance lock is not the project lock")
    env.pop("MIXED_CLUSTER_PERF_LOCK_FD", None)
    with lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        output.mkdir(parents=True, exist_ok=False)
        before = source_manifest(source)
        driver_sha = digest(driver)
        wrapper_sha = digest(policy_wrapper)
        shutil.copy2(driver, output / "benchmark-driver.py")
        shutil.copy2(policy_wrapper, output / "benchmark-policy-wrapper.py")
        (output / "source-before.patch").write_text(git(source, "diff", "HEAD", "--binary"))
        (output / "source-status.txt").write_text(git(source, "status", "--porcelain=v1"))
        (output / "submodules.txt").write_text(git(source, "submodule", "status", "--recursive"))
        write_json(output / "source-manifest.json", before)
        for filename, probe in (
            ("gpu-before.txt", ["nvidia-smi"]),
            ("gpu-topology.txt", ["nvidia-smi", "topo", "-m"]),
        ):
            capture = subprocess.run(probe, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (output / filename).write_text(capture.stdout)
            if capture.returncode:
                raise RuntimeError(f"Hardware inventory failed: {probe}")
        write_json(output / "command.json", command)
        (output / "command.sh").write_text(shlex.join(command) + "\n")
        frozen = output / "recipe"
        frozen.mkdir()
        for path in recipe.iterdir():
            if path.is_file() and path.suffix in (".py", ".md", ".sh"):
                shutil.copy2(path, frozen / path.name)
        versions = {}
        for package in ("torch", "nvidia-cutlass-dsl", "cuda-python", "cuda-bindings", "cupti-python",
                        "nvidia-cuda-cupti", "nvshmem4py-cu13", "nvidia-nvshmem-cu13"):
            versions[package] = md.version(package)
        metadata = {"schema_version": 1, "arm": args.arm, "started_at": stamp(), "complete": False,
                    "source": str(source), "source_commit": git(source, "rev-parse", "HEAD").strip(),
                    "source_patch_sha256": digest(output / "source-before.patch"),
                    "benchmark_driver": str(driver), "benchmark_driver_sha256": driver_sha,
                    "benchmark_policy_wrapper": str(policy_wrapper), "benchmark_policy_wrapper_sha256": wrapper_sha,
                    "tactic_policy": args.tactic_policy, "candidate_counts": None,
                    "image": args.image, "runtime_versions": versions, "model": args.model,
                    "tokens": tokens, "variants": variants,
                    "knobs": knobs,
                    "tuning_policy": args.policy,
                    "compiled_cache_policy": cache_policy,
                    "iters": args.iters, "warmup": args.warmup, "sweeps": args.sweeps,
                    "correctness_requested": False, "pdl": True, "fused_tma_reduce": False,
                    "apply_routing_weights_before_fc2": args.apply_routing_weights_before_fc2,
                    "w4a16_megamoe_fused_deterministic_combine": True,
                    "environment": {key: value for key, value in env.items() if key.startswith(
                        ("FLASHINFER_", "CUTE_DSL_", "CUDA_", "TRITON_", "MIXED_CLUSTER_", "BUILD_NVEP", "MAX_JOBS"))},
                    "recipe_sha256": {path.name: digest(path) for path in frozen.iterdir()}}
        write_json(output / "run.json", metadata)
        all_rows = []
        for sweep in range(1, args.sweeps + 1):
            log = output / f"sweep-{sweep}.log"
            print(f"{stamp()} {args.arm} sweep {sweep}/{args.sweeps} -> {log}", flush=True)
            with log.open("w") as handle:
                completed = subprocess.run(command, cwd=source, env=env, stdout=handle, stderr=subprocess.STDOUT)
            metadata.setdefault("exit_codes", []).append(completed.returncode)
            write_json(output / "run.json", metadata)
            if completed.returncode:
                print(f"Benchmark failed ({completed.returncode}); inspect {log}", file=sys.stderr)
                return completed.returncode
            all_rows.extend(parse_rows(log, sweep))
        write_json(output / "raw-records.json", all_rows)
        if "w4a16_megamoe" in variants:
            policies = [row for row in all_rows if row["kind"] == "MEGAMOE_POLICY_JSON"]
            for sweep in range(1, args.sweeps + 1):
                for rank in range(8):
                    receipts = [row["value"] for row in policies
                                if row["sweep"] == sweep and row["value"]["rank"] == rank]
                    if sorted(row["call_index"] for row in receipts) != list(range(1, len(tokens) + 1)):
                        raise ValueError(f"Missing/duplicate AUTO policy calls: sweep{sweep} rank{rank}")
            signatures = {(r["value"]["tactic_policy"], r["value"]["available_candidates"],
                           r["value"]["candidate_count"], r["value"]["candidate_sha256"],
                           r["value"]["enable_in_kernel_fc2_reduce"]) for r in policies}
            if len(signatures) != 1:
                raise ValueError("AUTO candidate policy differs across ranks, tokens or sweeps")
            policy, available, count, candidate_sha, reduction = next(iter(signatures))
            if policy != args.tactic_policy or reduction or not 0 < count <= available:
                raise ValueError("Unexpected AUTO candidate policy receipt")
            metadata["candidate_counts"] = {"available": available, "selected": count,
                                            "candidate_sha256": candidate_sha}
            write_json(output / "run.json", metadata)
        summary = summarize(all_rows, tokens, variants, args.sweeps, args.iters, args.warmup, args.apply_routing_weights_before_fc2)
        write_json(output / "summary.json", summary)
        if knobs == "auto":
            for sweep in range(1, args.sweeps + 1):
                for token in tokens:
                    for variant in variants:
                        if not variant.endswith("_megamoe"):
                            continue
                        receipts = [r["value"] for r in all_rows if r["kind"] == "MEGAMOE_TACTIC_JSON"
                                    and r["sweep"] == sweep and r["value"]["global_tokens"] == token
                                    and r["value"]["variant"] == variant]
                        if sorted(r["rank"] for r in receipts) != list(range(8)):
                            raise ValueError(f"Missing/duplicate per-rank tactic receipts: sweep{sweep} T{token}")
                        if any(r["knobs"] != receipts[0]["knobs"] for r in receipts):
                            raise ValueError(f"Ranks selected different tactics: sweep{sweep} T{token}")
                        if args.tactic_policy == "mixed-only" and any(
                            tuple(r["knobs"].get("cluster_shape_mnk", ())) != (4, 1, 1)
                            or tuple(r["knobs"].get("fallback_cluster_shape_mnk") or ()) != (2, 1, 1)
                            for r in receipts
                        ):
                            raise ValueError(f"mixed-only AUTO selected an incompatible winner: sweep{sweep} T{token}")
        after = source_manifest(source)
        if digest(driver) != driver_sha:
            raise RuntimeError("Benchmark driver changed during capture")
        if digest(policy_wrapper) != wrapper_sha:
            raise RuntimeError("Benchmark policy wrapper changed during capture")
        if before != after:
            write_json(output / "source-manifest-after.json", after)
            raise RuntimeError("Source changed during benchmark; capture must not be used")
        metadata.update(complete=True, finished_at=stamp(), source_unchanged_during_capture=True)
        write_json(output / "run.json", metadata)
        for point in summary:
            print(f"{args.arm} {point['variant']} T{point['global_tokens']}: {point['median_us']:.4f} us "
                  f"({point['sample_count']} untrimmed samples)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
