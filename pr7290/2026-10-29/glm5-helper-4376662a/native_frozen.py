#!/usr/bin/env python3
"""Run the native EP benchmark with one frozen tactic per global token count.

This local-only harness does no timed work. Route fingerprints are collected
after native routing and before native warmup/capture/timing.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

source = Path(os.environ["MEGA_SOURCE"])
# Preserve native compiler outputs outside measured launches for codegen proof.
dump_dir = Path(__file__).resolve().parent / "codegen" / source.name
dump_dir.mkdir(parents=True, exist_ok=True)
os.environ["CUTE_DSL_KEEP"] = "ptx,cubin"
os.environ["CUTE_DSL_DUMP_DIR"] = str(dump_dir)
sys.path.insert(0, str(source / "benchmarks"))
spec = importlib.util.spec_from_file_location(
    "native_distributed", source / "benchmarks/bench_cute_dsl_moe_distributed.py"
)
native = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = native
spec.loader.exec_module(native)
frozen_path = os.environ.get("MEGA_FROZEN_TACTICS")
frozen = json.loads(Path(frozen_path).read_text()) if frozen_path else None
original_benchmark = native._benchmark_distributed_megamoe
original_route = native._route_tokens
current_tokens = None


def benchmark(args, variant, num_tokens, rank, *rest):
    global current_tokens
    current_tokens = num_tokens
    if frozen is not None:
        args.megamoe_knobs = native._parse_megamoe_knobs(
            json.dumps(frozen[str(num_tokens)])
        )
        native._print_json("FROZEN_TACTIC_JSON", {
            "global_tokens": num_tokens, "rank": rank,
            "knobs": args.megamoe_knobs,
        })
    return original_benchmark(args, variant, num_tokens, rank, *rest)


def route(logits, bias, weights, ids):
    result = original_route(logits, bias, weights, ids)
    native._print_json("ROUTE_FINGERPRINT_JSON", {
        "global_tokens": current_tokens,
        "rank": int(os.environ["RANK"]),
        "ids_sha256": hashlib.sha256(ids.cpu().numpy().tobytes()).hexdigest(),
        "weights_sha256": hashlib.sha256(weights.cpu().numpy().tobytes()).hexdigest(),
    })
    return result


native._benchmark_distributed_megamoe = benchmark
native._route_tokens = route
raise SystemExit(native.main())
