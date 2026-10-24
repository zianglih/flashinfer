#!/usr/bin/env python3
"""Apply a project-only AUTO candidate policy, then run the unchanged native driver."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import runpy
import sys


def select_candidates(candidates, policy):
    """Preserve native order and knob objects; only remove disallowed tactics."""
    if policy == "all":
        return candidates
    if policy != "mixed-only":
        raise ValueError(f"Unsupported tactic policy: {policy}")
    selected = [
        knobs for knobs in candidates
        if tuple(knobs.get("cluster_shape_mnk", ())) == (4, 1, 1)
        and tuple(knobs.get("fallback_cluster_shape_mnk") or ()) == (2, 1, 1)
    ]
    if not selected:
        raise RuntimeError("mixed-only AUTO policy found no preferred4/fallback2 candidates")
    return selected


def install_policy(policy, module=None):
    if module is None:
        module = importlib.import_module("flashinfer.moe_ep.cute_dsl.megamoe.bf16_nvfp4.autotune")
    original = module.bf16_nvfp4_candidates
    call_index = 0

    def candidates(*, enable_in_kernel_fc2_reduce=False):
        nonlocal call_index
        available = original(enable_in_kernel_fc2_reduce=enable_in_kernel_fc2_reduce)
        selected = select_candidates(available, policy)
        call_index += 1
        encoded = json.dumps(selected, sort_keys=True, separators=(",", ":"))
        receipt = {
            "rank": int(os.environ.get("RANK", "0")),
            "call_index": call_index,
            "tactic_policy": policy,
            "available_candidates": len(available),
            "candidate_count": len(selected),
            "candidate_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "enable_in_kernel_fc2_reduce": enable_in_kernel_fc2_reduce,
        }
        print("MEGAMOE_POLICY_JSON," + json.dumps(receipt, sort_keys=True, separators=(",", ":")), flush=True)
        return selected

    # The native AUTO function reads this module global when candidates=None.
    # Its compile, warmup, graph-event timing, ranking and winner logic remain intact.
    module.bf16_nvfp4_candidates = candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-driver", type=Path, required=True)
    parser.add_argument("--tactic-policy", choices=("all", "mixed-only"), required=True)
    parser.add_argument("benchmark_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    driver = args.native_driver.resolve()
    if not driver.is_file():
        parser.error(f"Native driver does not exist: {driver}")
    benchmark_args = args.benchmark_args
    if benchmark_args[:1] == ["--"]:
        benchmark_args = benchmark_args[1:]
    # Match direct Python execution's sibling benchmark imports; PYTHONPATH still
    # chooses the baseline or candidate FlashInfer library checkout.
    sys.path.insert(0, str(driver.parent))
    sys.argv = [str(driver), *benchmark_args]
    install_policy(args.tactic_policy)
    runpy.run_path(str(driver), run_name="__main__")


if __name__ == "__main__":
    main()
