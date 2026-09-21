"""Plan or execute the serial, fail-closed GLM MoE calibration on its own node.

This helper does not provision a node, change packages, update Git, or resume a
measurement directory. A new --run-id is required for every attempt.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


TASK_ROOT = Path("/data/home/ziangli/flashinfer-sglang-megamoe-benchmark-alignment")
SOURCE_COMMIT = "bd8391858db504c8997e704c7952f4d48ccab591"
RUNTIME_BASE = "ad0a5e5e78e57070ec7c582efe733cb55cd8839f"
TIMING_STAGE = "timing-r5"
REFCHECK_POLICY = "per-path"
REFERENCE_SOURCE_SHA = (
    "6282388bf42df1cc2580c79ce1cf58644943f958decd2ebf99ff2228629d25a5"
)
IMAGE = "lmsysorg/sglang:nightly-dev-cu13-20260918-20518d85"
PHASES = ("correctness", "core", "auto", "routing", "prefill")
VARIANTS = ("w4a16", "w4a16_megamoe")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path, record):
    with Path(path).open("x") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")


def jobs_for(phases):
    jobs = []

    def add(phase, ep, communication, capacity, repeat, tokens, **overrides):
        job = dict(
            phase=phase,
            ep=ep,
            communication=communication,
            capacity=capacity,
            repeat=repeat,
            tokens=list(tokens),
            timer="cupti",
            graph=True,
            warmup=3,
            iters=100,
            knobs=None,
            precomputed_routing=False,
            refcheck_policy=REFCHECK_POLICY,
        )
        job.update(overrides)
        token_tag = "-n" + "_".join(map(str, tokens)) if phase == "auto" else ""
        job["id"] = (
            f"{len(jobs) + 1:03d}-{phase}-ep{ep}-{communication}-"
            f"cap{capacity or 'live'}-r{repeat}{token_tag}"
        )
        jobs.append(job)

    for phase in PHASES:
        if phase not in phases:
            continue
        if phase == "correctness":
            for ep, comm, cap in itertools.product(
                (4, 8), ("allgather", "allreduce"), (None, 32768)
            ):
                add(
                    phase,
                    ep,
                    comm,
                    cap,
                    1,
                    (1, 3, 5, 32),
                    timer="cuda_event",
                    warmup=1,
                    iters=3,
                )
        elif phase == "core":
            for repeat, ep, comm, cap in itertools.product(
                (1, 2), (4, 8), ("alltoall", "allgather", "allreduce"), (None, 32768)
            ):
                add(phase, ep, comm, cap, repeat, (16, 32, 64, 128, 256, 512, 1024))
        elif phase == "auto":
            # One token count per process/cache: fixed-capacity cache keys must
            # not turn later N values into reuse of the first N's auto winner.
            for repeat, ep, tokens in itertools.product(
                (1, 2), (4, 8), (16, 128, 1024)
            ):
                add(phase, ep, "allgather", 32768, repeat, (tokens,), knobs="auto")
        elif phase == "routing":
            for repeat, ep, comm in itertools.product(
                (1, 2), (4, 8), ("allgather", "allreduce")
            ):
                add(
                    phase,
                    ep,
                    comm,
                    32768,
                    repeat,
                    (16, 128, 1024),
                    precomputed_routing=True,
                )
        elif phase == "prefill":
            for repeat, ep, comm in itertools.product(
                (1, 2), (4, 8), ("allgather", "allreduce")
            ):
                add(phase, ep, comm, 32768, repeat, (4096, 16384), graph=False)
    return jobs


def benchmark_argv(job, python, wrapper):
    argv = [
        python,
        "-m",
        "torch.distributed.run",
        "--master-addr=127.0.0.1",
        "--master-port=30327",
        "--nnodes=1",
        f"--nproc-per-node={job['ep']}",
        "--max-restarts=0",
        str(wrapper),
        "--num-gpus",
        str(job["ep"]),
        "--parallel-modes",
        "ep",
        "--variants",
        ",".join(VARIANTS),
        "--model-shape",
        "glm-5.2",
        "--ep-communication",
        job["communication"],
        "--num-tokens",
        ",".join(map(str, job["tokens"])),
        "--warmup",
        str(job["warmup"]),
        "--iters",
        str(job["iters"]),
        "--timing",
        job["timer"],
        "--refcheck",
        "--refcheck-policy",
        REFCHECK_POLICY,
        "--no-fused-finalize",
        "--log-timing-samples",
    ]
    if job["graph"]:
        argv += ["--cuda-graph", "--validate-graph-output"]
    if job["capacity"] is not None:
        argv += ["--megamoe-max-tokens-per-rank", str(job["capacity"])]
    if job["knobs"] is not None:
        argv += ["--megamoe-knobs", job["knobs"]]
    if job["precomputed_routing"]:
        argv.append("--precomputed-routing")
    return argv


def parse_records(log):
    prefixes = (
        "DISTRIBUTED_CASE_JSON",
        "DISTRIBUTED_RESULT_JSON",
        "DISTRIBUTED_TIMING_SAMPLES_JSON",
        "GRAPH_REFCHECK_JSON",
        "ORACLE_REFCHECK_JSON",
        "CALIBRATION_WRAPPER_FINISH_JSON",
        "MEGAMOE_TACTIC_JSON",
    )
    records = {prefix: [] for prefix in prefixes}
    records["refcheck"] = []
    marker = re.compile("(" + "|".join(prefixes) + "),")
    decoder = json.JSONDecoder()
    with Path(log).open(errors="replace") as handle:
        for line in handle:
            # Native rank prints may write their newline separately, so two
            # otherwise atomic JSON records can share a physical log line.
            for match in marker.finditer(line):
                value, _ = decoder.raw_decode(line[match.end() :])
                records[match.group(1)].append(value)
            refcheck = re.search(
                r"REFCHECK_CSV,[^,\s]+,\d+,[^,\s]+,[^,\s]+,(?:PASS|FAIL)", line
            )
            if refcheck:
                fields = refcheck.group().split(",")
                if len(fields) != 6:
                    raise ValueError(f"Malformed refcheck line: {line}")
                records["refcheck"].append(
                    dict(
                        variant=fields[1],
                        tokens=int(fields[2]),
                        max_abs=float(fields[3]),
                        relative_l2=float(fields[4]),
                        status=fields[5],
                    )
                )
    return records


def routing_identity(source_record):
    return {
        "provider": "benchmark.pinned_sglang_glm52_triton",
        "sglang_commit": "50eeb742961908afa68f4f523a1a19c5de6eb0b3",
        "source_sha256": "5663a23cf30e6b2e1e2f8ba6d25b9c3eac39e319658c05f0f400b78b3862c47b",
        "kernel_ast_sha256": "075eb2d017d66233cb3ac41155ab1ef8105fa1f0c0f81fccea253bd0e94ffe0a",
        "adapter_sha256": source_record["benchmark_sha256"][
            "benchmarks/sglang_glm_routing.py"
        ],
    }


def reference_identity(source_record):
    paths = source_record["benchmark_sha256"]
    if paths["tests/moe_ep/w4a16_reference.py"] != REFERENCE_SOURCE_SHA:
        raise ValueError("Original independent reference source differs")
    module_sha = paths["benchmarks/w4a16_contract_reference.py"]
    if not re.fullmatch(r"[0-9a-f]{64}", module_sha):
        raise ValueError("Independent contract reference module hash is invalid")
    return dict(
        reference_provider="benchmark.w4a16_independent_contract",
        reference_source_sha256=REFERENCE_SOURCE_SHA,
        reference_module_sha256=module_sha,
    )


def validate_log(log, job, expected_routing_identity, expected_reference_identity):
    if job.get("refcheck_policy") != REFCHECK_POLICY:
        raise ValueError("The r4 driver requires explicit per-path validation")
    if (
        set(expected_reference_identity)
        != {"reference_provider", "reference_source_sha256", "reference_module_sha256"}
        or expected_reference_identity["reference_provider"]
        != "benchmark.w4a16_independent_contract"
        or expected_reference_identity["reference_source_sha256"]
        != REFERENCE_SOURCE_SHA
        or not re.fullmatch(
            r"[0-9a-f]{64}", expected_reference_identity["reference_module_sha256"]
        )
    ):
        raise ValueError("Expected independent reference identity is incomplete")
    records = parse_records(log)
    expected = {(variant, tokens) for variant in VARIANTS for tokens in job["tokens"]}

    def indexed(prefix, label_field="variant"):
        rows = records[prefix]
        keys = [
            (row[label_field].removeprefix("ep::"), row["global_tokens"])
            for row in rows
        ]
        if len(keys) != len(expected) or set(keys) != expected:
            raise ValueError(f"{prefix}: expected each variant/token exactly once")
        return dict(zip(keys, rows, strict=True))

    case_rows = indexed("DISTRIBUTED_CASE_JSON")
    result_rows = indexed("DISTRIBUTED_RESULT_JSON")
    samples = indexed("DISTRIBUTED_TIMING_SAMPLES_JSON", "profile_label")
    for key, row in case_rows.items():
        variant, tokens = key
        if {
            name: value
            for name, value in result_rows[key].items()
            if name != "median_ms"
        } != row:
            raise ValueError(f"{key}: result/case metadata differ")
        required = dict(
            routing_identity=expected_routing_identity,
            model_shape="glm-5.2",
            world_size=job["ep"],
            parallel_mode="ep",
            split_ep_communication=job["communication"],
            megamoe_capacity_override=job["capacity"],
            timer=job["timer"],
            cuda_graph=job["graph"],
            precomputed_routing=job["precomputed_routing"],
            use_fused_finalize=False,
            apply_topk_in_fc1=False,
            enable_pdl=True,
            megamoe_knobs=job["knobs"],
            refcheck=True,
            refcheck_policy=REFCHECK_POLICY,
        )
        for name, value in required.items():
            if row.get(name) != value or result_rows[key].get(name) != value:
                raise ValueError(f"{key}: wrong {name}")
        if row["shape"] != dict(
            hidden_size=6144,
            intermediate_size=2048,
            num_experts=256,
            top_k=8,
            n_group=1,
            topk_group=1,
            routed_scaling_factor=2.5,
        ):
            raise ValueError(f"{key}: wrong model shape")
        capacity = job["capacity"] or math.ceil(tokens / job["ep"])
        quotient, remainder = divmod(tokens, job["ep"])
        if row["live_tokens_per_rank"] != [
            quotient + int(rank < remainder) for rank in range(job["ep"])
        ]:
            raise ValueError(f"{key}: wrong live token partition")
        expected_comm = (
            "fused_megamoe"
            if variant == "w4a16_megamoe"
            else "alltoall_dispatch_combine"
            if job["communication"] == "alltoall"
            else job["communication"] + "+sum_reduce_scatter"
        )
        if row["actual_communication"] != expected_comm:
            raise ValueError(f"{key}: wrong actual communication")
        if (
            variant == "w4a16_megamoe"
            and row["megamoe_max_tokens_per_rank"] != capacity
        ):
            raise ValueError(f"{key}: wrong Mega capacity")
        sample = samples[key]
        values = sample["samples_ms"]
        if (
            sample["sample_count"] != job["iters"]
            or len(values) != job["iters"]
            or sample["repeat_iters"] != job["iters"]
            or sample["warmup_iters"] != job["warmup"]
            or sample["sample_aggregation"] != "per_iteration_rank_max"
            or sample["timer"] != job["timer"]
            or sample["cuda_graph"] != job["graph"]
            or sample["world_size"] != job["ep"]
            or sample["cold_l2_cache"] is not True
            or sample["precomputed_routing"] != job["precomputed_routing"]
            or sample["model_shape"] != "glm-5.2"
            or sample["ep_communication"] != job["communication"]
            or sample["megamoe_capacity_override"] != job["capacity"]
            or not all(
                isinstance(value, (float, int)) and math.isfinite(value) and value > 0
                for value in values
            )
        ):
            raise ValueError(f"{key}: invalid timing samples")
        import statistics

        if not math.isclose(
            result_rows[key]["median_ms"],
            statistics.median(values),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            raise ValueError(f"{key}: median does not match raw samples")
    refchecks = records["refcheck"]
    if (
        len(refchecks) != len(job["tokens"])
        or {r["tokens"] for r in refchecks} != set(job["tokens"])
        or any(
            r["variant"] != "w4a16_megamoe"
            or r["status"] not in ("PASS", "FAIL")
            or not math.isfinite(r["max_abs"])
            or not math.isfinite(r["relative_l2"])
            or r["max_abs"] < 0
            or r["relative_l2"] < 0
            for r in refchecks
        )
    ):
        raise ValueError("Missing or malformed diagnostic cross-pair refchecks")
    oracle_rows = indexed("ORACLE_REFCHECK_JSON")

    def validate_oracle_metrics(row):
        if any(
            row.get(name) != value
            for name, value in dict(status="PASS", atol=1e-2, rtol=1e-2).items()
        ):
            raise ValueError(
                "Independent per-path reference failed or changed tolerance"
            )
        for name in ("max_abs", "relative_l2"):
            value = row.get(name)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("Invalid independent reference error metric")
        if (
            type(row.get("bitwise_mismatches")) is not int
            or row["bitwise_mismatches"] < 0
        ):
            raise ValueError("Invalid independent reference mismatch count")
        if type(row.get("nonfinite_count")) is not int or row["nonfinite_count"] != 0:
            raise ValueError("Independent reference contains nonfinite values")

    for (variant, _), row in oracle_rows.items():
        validate_oracle_metrics(row)
        if (
            row.get("input_contract_passed") is not True
            or row.get("communication") != job["communication"]
        ):
            raise ValueError(
                "Independent reference input/communication contract differs"
            )
        if any(
            row.get(name) != value
            for name, value in expected_reference_identity.items()
        ):
            raise ValueError("Independent reference source identity differs")
        contract = (
            "unweighted_bf16_routes_ordered_fp32_fma_bf16"
            if variant == "w4a16_megamoe"
            else "owner_fp32_fma_bf16_then_topk_slot_fp32_tree_bf16"
            if job["communication"] == "alltoall"
            else "owner_fp32_fma_bf16_then_nccl_bf16_sum"
        )
        if row.get("contract") != contract:
            raise ValueError("Independent reference rounding contract differs")
        partial = row.get("partial_validation")
        if variant == "w4a16":
            if not isinstance(partial, dict):
                raise ValueError(
                    "Split reference lacks independent owner-partial validation"
                )
            validate_oracle_metrics(partial)
        elif partial is not None:
            raise ValueError("Unexpected Mega owner-partial validation")
    if job["graph"]:
        for row in indexed("GRAPH_REFCHECK_JSON", "profile_label").values():
            for name, value in dict(
                status="PASS",
                world_size=job["ep"],
                atol=1e-2,
                rtol=1e-2,
                extra_untimed_eager_forwards=3,
                extra_untimed_captures=1,
                checked_untimed_replays=2,
                outputs_poisoned_before_each_replay=True,
                all_ranks_checked=True,
                timed_replays_checked=False,
            ).items():
                if row.get(name) != value:
                    raise ValueError(f"Invalid graph check {name}")
            if not math.isfinite(row["max_abs"]):
                raise ValueError("Nonfinite graph check")
    elif records["GRAPH_REFCHECK_JSON"]:
        raise ValueError("Unexpected graph checks in eager case")
    finishes = records["CALIBRATION_WRAPPER_FINISH_JSON"]
    if len(finishes) != job["ep"] or {r["rank"] for r in finishes} != set(
        range(job["ep"])
    ):
        raise ValueError("Missing or duplicate per-rank wrapper completion")
    for row in finishes:
        use_cupti = job["timer"] == "cupti"
        if (
            row["cupti_used"] != use_cupti
            or row["final_detaches"] != int(use_cupti)
            or row["graph_output_validation_requested"] != job["graph"]
            or (
                use_cupti
                and (
                    row["registrations"] < len(expected)
                    or row["deferred_finalizes"] < len(expected)
                )
            )
        ):
            raise ValueError("Invalid CUPTI callback/detach lifecycle")
    if job["knobs"] == "auto":
        tactics = records["MEGAMOE_TACTIC_JSON"]
        expected_tactics = {
            (rank, tokens) for rank in range(job["ep"]) for tokens in job["tokens"]
        }
        if (
            len(tactics) != len(expected_tactics)
            or {(r["rank"], r["global_tokens"]) for r in tactics} != expected_tactics
        ):
            raise ValueError("Missing per-rank auto tactic evidence")
    return dict(
        validated_at=now(),
        result_count=len(expected),
        sample_count=len(expected) * job["iters"],
        eager_refcheck_count=len(refchecks),
        refcheck_policy=REFCHECK_POLICY,
        cross_pair_status_counts={
            status: sum(r["status"] == status for r in refchecks)
            for status in ("PASS", "FAIL")
        },
        cross_pair_all_passed=all(r["status"] == "PASS" for r in refchecks),
        oracle_refcheck_count=len(oracle_rows),
        reference_identity=expected_reference_identity,
        accepted_latency=True,
        graph_refcheck_count=len(records["GRAPH_REFCHECK_JSON"]),
        timed_replays_numerically_checked=False,
        records=records,
    )


def checked_output(argv, **kwargs):
    return subprocess.check_output(argv, text=True, **kwargs).strip()


def source_proof(source):
    if not isinstance(SOURCE_COMMIT, str) or not re.fullmatch(
        r"[0-9a-f]{40}", SOURCE_COMMIT
    ):
        raise ValueError("r4 source commit is not pinned; execution is disabled")
    actual = checked_output(["git", "-C", str(source), "rev-parse", "HEAD"])
    if actual != SOURCE_COMMIT:
        raise ValueError(f"Expected benchmark source {SOURCE_COMMIT}; got {actual}")
    if checked_output(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=normal"]
    ):
        raise ValueError("Source checkout must be clean")
    changed = checked_output(
        ["git", "-C", str(source), "diff", "--name-only", RUNTIME_BASE, "HEAD"]
    )
    if any(
        not (
            name.startswith("benchmarks/")
            or name
            in (
                "tests/test_moe_distributed_layout.py",
                "tests/test_sglang_glm_routing.py",
                "tests/test_w4a16_contract_reference.py",
            )
        )
        for name in changed.splitlines()
    ):
        raise ValueError("Runtime source differs from the ad0 baseline")
    paths = (
        "benchmarks/bench_cute_dsl_moe_distributed.py",
        "benchmarks/moe_distributed_layout.py",
        "benchmarks/sglang_glm_routing.py",
        "benchmarks/w4a16_contract_reference.py",
        "tests/moe_ep/w4a16_reference.py",
    )
    record = dict(
        benchmark_commit=actual,
        runtime_base=RUNTIME_BASE,
        benchmark_sha256={name: digest(source / name) for name in paths},
    )
    reference_identity(record)
    return record


def validate_environment(environment_root, runtime, source_record):
    names = (
        "initial/setup-completed.json",
        "initial/runtime-after.json",
        "initial/image-before.json",
        f"{TIMING_STAGE}/setup-completed.json",
        f"{TIMING_STAGE}/runtime-after.json",
    )
    records = {
        name: json.loads((environment_root / name).read_text()) for name in names
    }
    initial = records["initial/setup-completed.json"]
    timing = records[f"{TIMING_STAGE}/setup-completed.json"]
    if (
        initial["flashinfer_commit"] != RUNTIME_BASE
        or initial["preserved_image_torch_cuda_nccl"] is not True
    ):
        raise ValueError(
            "Initial environment seal does not match the ad0 runtime baseline"
        )
    if (
        timing["source_head"] != source_record["benchmark_commit"]
        or timing["flashinfer_kernel_base"] != RUNTIME_BASE
        or timing["benchmark_sha256"] != source_record["benchmark_sha256"]
        or timing["image_torch_cuda_nccl_preserved"] is not True
        or timing["cupti_timestamp_ok"] is not True
        or timing["cupti_python"] != "13.2.0"
        or timing["cupti_library_dist"] != "13.2.86"
        or not timing["loaded_cupti_libraries"]
    ):
        raise ValueError("Timing environment seal/source/CUPTI evidence differs")
    # Exact comparison also binds all package providers, loaded NCCL (which can
    # differ from its installed distribution version), NVCC, driver and GPU UUIDs.
    if runtime != records[f"{TIMING_STAGE}/runtime-after.json"]:
        raise ValueError("Fresh runtime differs from sealed timing runtime")
    before = records["initial/image-before.json"]
    prepared = records["initial/runtime-after.json"]
    for field in ("torch_import", "torch_cuda", "nccl", "nvcc", "gpu"):
        if not (before[field] == prepared[field] == runtime[field]):
            raise ValueError(f"Image/runtime provider changed: {field}")
    allowed_timing_changes = {"cupti-python", "nvidia-cuda-cupti"}
    for name in set(prepared["versions"]) | set(runtime["versions"]):
        if name not in allowed_timing_changes and prepared["versions"].get(
            name
        ) != runtime["versions"].get(name):
            raise ValueError(f"Non-CUPTI provider changed during timing setup: {name}")
    for name in (
        "torch",
        "triton",
        "transformers",
        "sglang-kernel",
        "nvidia-nccl-cu13",
    ):
        if before["versions"][name] != runtime["versions"][name]:
            raise ValueError(f"Image package changed: {name}")
    for name in (
        "nvidia-cutlass-dsl",
        "nvidia-cutlass-dsl-libs-base",
        "nvidia-cutlass-dsl-libs-core",
        "nvidia-cutlass-dsl-libs-cu12",
        "nvidia-cutlass-dsl-libs-cu13",
    ):
        if runtime["versions"].get(name) != "4.7.1":
            raise ValueError(f"Unexpected CuTe provider: {name}")
    return {name: digest(environment_root / name) for name in names}


def validate_gate(gate_root, provenance):
    receipt = json.loads((gate_root / "gate-receipt.json").read_text())
    if (
        receipt["source"] != provenance["source"]
        or receipt["runtime_versions"] != provenance["runtime"]["versions"]
    ):
        raise ValueError("Imported gate source/runtime versions differ")
    if (
        receipt["wrapper_sha256"] != provenance["wrapper_sha256"]
        or receipt["image_declared"] != provenance["image_declared"]
        or receipt["environment_sha256"] != provenance["environment_sha256"]
    ):
        raise ValueError("Imported gate wrapper/image differs")
    if receipt["job_count"] != 8:
        raise ValueError("Imported gate is incomplete")
    gate_jobs = jobs_for(["correctness"])
    expected_files = {
        f"{job['id']}/{name}"
        for job in gate_jobs
        for name in ("invocation.json", "benchmark.log", "validation.json", "exit.json")
    }
    if set(receipt["files"]) != expected_files:
        raise ValueError("Imported gate evidence matrix is incomplete")
    for relative, sha256 in receipt["files"].items():
        path = (gate_root / relative).resolve()
        if not path.is_relative_to(gate_root.resolve()) or digest(path) != sha256:
            raise ValueError(f"Gate evidence changed: {relative}")
    for job in gate_jobs:
        case = gate_root / job["id"]
        if json.loads((case / "invocation.json").read_text())["job"] != job:
            raise ValueError("Imported gate job differs from the required matrix")
        if json.loads((case / "exit.json").read_text())["passed"] is not True:
            raise ValueError("Imported gate contains a failed job")
        validate_log(
            case / "benchmark.log",
            job,
            routing_identity(provenance["source"]),
            reference_identity(provenance["source"]),
        )
    return {
        "root": str(gate_root),
        "receipt_sha256": digest(gate_root / "gate-receipt.json"),
    }


def execute(args, jobs):
    root = args.task_root
    source = root / "sources/flashinfer-ad0"
    wrapper = Path(__file__).with_name("run_deferred_cupti.py").resolve()
    run = root / "runs" / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    exit_record = {"started_at": now(), "run_id": args.run_id, "status": "failed"}
    current = None
    try:
        source_record = source_proof(source)
        probe = Path(__file__).with_name("probe_runtime.py")
        runtime = json.loads(checked_output([args.python, str(probe)]))
        environment_sha256 = validate_environment(
            root / "environment", runtime, source_record
        )
        for relative, sha256 in environment_sha256.items():
            target = run / "environment" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as handle:
                handle.write((root / "environment" / relative).read_bytes())
            if digest(target) != sha256:
                raise ValueError("Environment evidence changed while copying")
        for name, value in {
            "nvidia-cutlass-dsl": "4.7.1",
            "cupti-python": "13.2.0",
            "nvidia-cuda-cupti": "13.2.86",
        }.items():
            if runtime["versions"].get(name) != value:
                raise ValueError(f"Unexpected {name}: {runtime['versions'].get(name)}")
        if any(
            runtime["versions"].get(name) is not None
            for name in ("flashinfer-cubin", "flashinfer-jit-cache")
        ):
            raise ValueError(
                "Installed FlashInfer prebuilt wheels would confound source JIT"
            )
        gpu_names = checked_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]
        ).splitlines()
        if len(gpu_names) < 8 or any("B300" not in name for name in gpu_names[:8]):
            raise ValueError("Calibration requires eight B300 GPUs")
        active = checked_output(
            ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"]
        )
        if active:
            raise ValueError(
                "GPU compute processes already exist; refusing concurrent calibration"
            )
        provenance = dict(
            source=source_record,
            runtime=runtime,
            environment_sha256=environment_sha256,
            timing_stage=TIMING_STAGE,
            refcheck_policy=REFCHECK_POLICY,
            image_declared=IMAGE,
            driver_sha256=digest(__file__),
            wrapper_sha256=digest(wrapper),
            python=args.python,
            created_at=now(),
        )
        write_json(run / "provenance.json", provenance)
        if "correctness" not in args.phases:
            if args.gate_run is None:
                raise ValueError(
                    "A performance-only run requires --gate-run with a complete sealed gate"
                )
            write_json(
                run / "imported-gate.json", validate_gate(args.gate_run, provenance)
            )
        write_json(
            run / "plan.json",
            dict(
                run_id=args.run_id,
                phases=args.phases,
                jobs=jobs,
                required_phases=list(PHASES),
                omitted_required_phases=[p for p in PHASES if p not in args.phases],
            ),
        )
        cache = run / "compiled-cache"
        cache.mkdir()
        gate_files = {}
        for index, job in enumerate(jobs):
            current = job["id"]
            if source_proof(source) != source_record:
                raise ValueError("Source changed during calibration")
            case = run / current
            case.mkdir()
            env = os.environ.copy()
            # Remove inherited experiment overrides, preserving package/library
            # search paths prepared by the operator. Explicit settings follow.
            for key in tuple(env):
                if key.startswith(("FLASHINFER_", "CUTE_DSL_", "CUTLASS_DSL_")):
                    del env[key]
            env.update(
                {
                    "PYTHONPATH": str(source),
                    "PYTHONUNBUFFERED": "1",
                    "OMP_NUM_THREADS": "1",
                    "CUDA_VISIBLE_DEVICES": ",".join(map(str, range(job["ep"]))),
                    "FLASHINFER_CUDA_ARCH_LIST": "10.3a",
                    "MAX_JOBS": "16",
                    "FLASHINFER_NVCC_THREADS": "2",
                    "FLASHINFER_WORKSPACE_BASE": str(cache),
                    "FLASHINFER_MOE_EP_KNOB_CACHE": str(case / "knobs.json"),
                    "CUDA_CACHE_PATH": str(cache / "cuda"),
                    "XDG_CACHE_HOME": str(cache / "xdg"),
                    "TRITON_CACHE_DIR": str(cache / "triton"),
                }
            )
            argv = benchmark_argv(job, args.python, wrapper)
            captured_env = {
                k: v
                for k, v in sorted(env.items())
                if k.startswith(
                    (
                        "FLASHINFER_",
                        "CUDA_",
                        "NVSHMEM_",
                        "NCCL_",
                        "CUTE_",
                        "CUTLASS_",
                        "TRITON_",
                        "PYTORCH_",
                    )
                )
                or k
                in (
                    "PATH",
                    "PYTHONPATH",
                    "PYTHONUNBUFFERED",
                    "LD_LIBRARY_PATH",
                    "OMP_NUM_THREADS",
                    "MAX_JOBS",
                    "XDG_CACHE_HOME",
                )
            }
            write_json(
                case / "invocation.json",
                dict(
                    job=job,
                    argv=argv,
                    cwd=str(source),
                    env=captured_env,
                    pins=source_record,
                    wrapper_sha256=provenance["wrapper_sha256"],
                    runtime_versions=runtime["versions"],
                    started_at=now(),
                    knob_cache_initially_absent=not (case / "knobs.json").exists(),
                ),
            )
            print(f"{now()} START {current} ({index + 1}/{len(jobs)})", flush=True)
            timed_out = False
            interrupted = None
            with (case / "benchmark.log").open("x") as log:
                process = subprocess.Popen(
                    argv,
                    cwd=source,
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                try:
                    rc = process.wait(timeout=args.case_timeout)
                except BaseException as error:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    timed_out = isinstance(error, subprocess.TimeoutExpired)
                    interrupted = f"{type(error).__name__}: {error}"
                    rc = process.returncode
            validation = None
            issue = None
            if rc == 0 and not timed_out:
                try:
                    validation = validate_log(
                        case / "benchmark.log",
                        job,
                        routing_identity(source_record),
                        reference_identity(source_record),
                    )
                    write_json(case / "validation.json", validation)
                except (ValueError, KeyError, TypeError) as error:
                    issue = str(error)
            passed = rc == 0 and not timed_out and validation is not None
            write_json(
                case / "exit.json",
                dict(
                    exit_code=rc,
                    timed_out=timed_out,
                    interrupted=interrupted,
                    passed=passed,
                    validation_issue=issue,
                    finished_at=now(),
                    log_sha256=digest(case / "benchmark.log"),
                ),
            )
            if not passed:
                raise RuntimeError(
                    f"Case {current} failed (exit={rc}, timeout={timed_out}, validation={issue})"
                )
            print(f"{now()} PASS {current}", flush=True)
            if job["phase"] == "correctness":
                for name in (
                    "invocation.json",
                    "benchmark.log",
                    "validation.json",
                    "exit.json",
                ):
                    gate_files[f"{current}/{name}"] = digest(case / name)
                if index + 1 == len(jobs) or jobs[index + 1]["phase"] != "correctness":
                    write_json(
                        run / "gate-receipt.json",
                        dict(
                            source=source_record,
                            runtime_versions=runtime["versions"],
                            wrapper_sha256=provenance["wrapper_sha256"],
                            image_declared=IMAGE,
                            environment_sha256=environment_sha256,
                            job_count=8,
                            files=gate_files,
                            sealed_at=now(),
                        ),
                    )
        exit_record.update(
            status="completed",
            completed_jobs=len(jobs),
            omitted_required_phases=[p for p in PHASES if p not in args.phases],
        )
        return 0
    except BaseException as error:
        exit_record.update(error=f"{type(error).__name__}: {error}", failed_job=current)
        print(exit_record["error"], file=sys.stderr, flush=True)
        return 1
    finally:
        exit_record["finished_at"] = now()
        write_json(run / "exit.json", exit_record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--task-root", type=Path, default=TASK_ROOT)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--phases", default="correctness,core")
    parser.add_argument("--gate-run", type=Path)
    parser.add_argument("--case-timeout", type=int, default=7200)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute on the dedicated node; omission prints plan only",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,119}", args.run_id):
        parser.error("Use a simple, new run ID without path separators")
    args.phases = args.phases.split(",")
    if len(set(args.phases)) != len(args.phases) or not set(args.phases) <= set(PHASES):
        parser.error("--phases must be a unique subset of " + ",".join(PHASES))
    if args.case_timeout <= 0:
        parser.error("--case-timeout must be positive")
    if args.execute and (
        not isinstance(SOURCE_COMMIT, str)
        or not re.fullmatch(r"[0-9a-f]{40}", SOURCE_COMMIT)
    ):
        parser.error("r4 SOURCE_COMMIT must be pinned before execution")
    jobs = jobs_for(args.phases)
    if not args.execute:
        print(
            json.dumps(
                dict(
                    run_id=args.run_id,
                    source_commit=SOURCE_COMMIT,
                    runtime_base=RUNTIME_BASE,
                    refcheck_policy=REFCHECK_POLICY,
                    phases=args.phases,
                    invocation_count=len(jobs),
                    jobs=jobs,
                    required_phases=list(PHASES),
                    omitted_required_phases=[p for p in PHASES if p not in args.phases],
                ),
                indent=2,
            )
        )
        return 0
    return execute(args, jobs)


if __name__ == "__main__":
    raise SystemExit(main())
