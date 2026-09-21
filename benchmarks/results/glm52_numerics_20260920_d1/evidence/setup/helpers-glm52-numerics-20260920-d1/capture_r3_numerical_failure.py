#!/usr/bin/env python3
"""Capture frozen r3 N1/N3 eager numerics; preserve its strict refcheck and sources."""

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import gc
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

SOURCE_COMMIT = "6f88c235b658104053761aad15158e954f439a41"
RUNTIME_BASE = "ad0a5e5e78e57070ec7c582efe733cb55cd8839f"
SOURCE_SHA = {
    "benchmarks/bench_cute_dsl_moe_distributed.py": "66fdc2b041531cdfb203161aa514a007db970deb1d190faec1ce7b5af57617e0",
    "benchmarks/moe_distributed_layout.py": "a66953bc8db2c38cb6fa23f5fa84c89721a0a09a9aad5b83eeba0c44d1a83d76",
    "benchmarks/sglang_glm_routing.py": "29016eaa2713851fb09d5c141300ea42d0d7e6d444ec77de9dba2bdd6ffbeac0",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, default=str)
        stream.write("\n")


def prepare_contract(source, output, baseline_path):
    """Validate immutable source/baseline identity before GPU initialization."""
    source, output, baseline_path = map(
        lambda p: Path(p).resolve(), (source, output, baseline_path)
    )
    baseline = json.loads(baseline_path.read_text())
    if baseline["pins"] != {
        "benchmark_commit": SOURCE_COMMIT,
        "benchmark_sha256": SOURCE_SHA,
        "runtime_base": RUNTIME_BASE,
    }:
        raise ValueError("Baseline source pins differ")
    expected_job = {
        "capacity": None,
        "communication": "allgather",
        "ep": 4,
        "graph": True,
        "id": "001-correctness-ep4-allgather-caplive-r1",
        "iters": 3,
        "knobs": None,
        "phase": "correctness",
        "precomputed_routing": False,
        "repeat": 1,
        "timer": "cuda_event",
        "tokens": [1, 3, 5, 32],
        "warmup": 1,
    }
    if baseline["job"] != expected_job:
        raise ValueError("Unexpected baseline case settings")
    argv = baseline["argv"]
    for flag, expected in (
        ("--model-shape", "glm-5.2"),
        ("--variants", "w4a16,w4a16_megamoe"),
    ):
        if argv.count(flag) != 1 or argv[argv.index(flag) + 1] != expected:
            raise ValueError("Baseline argv differs: " + flag)
    if "--no-fused-finalize" not in argv or any(
        flag in argv
        for flag in (
            "--no-pdl",
            "--use-per-token-activation",
            "--apply-topk-in-fc1",
            "--precomputed-routing",
        )
    ):
        raise ValueError("Baseline precision/routing/PDL flags differ")
    if output == source or source in output.parents or output.exists():
        raise ValueError(
            "Diagnostic output must be new and outside the source checkout"
        )
    baseline_run = baseline_path.parents[1]
    if output == baseline_run or baseline_run in output.parents:
        raise ValueError("Diagnostic output cannot modify the original run")

    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(source), *args], text=True
        ).strip()

    if git("rev-parse", "HEAD") != SOURCE_COMMIT or git("status", "--porcelain"):
        raise ValueError("Frozen source checkout is not clean at 6f88")
    if git("diff", "--name-only", RUNTIME_BASE, "--", "flashinfer", "csrc", "include"):
        raise ValueError("Runtime kernels differ from pinned ad0")
    for name, digest in SOURCE_SHA.items():
        if sha(source / name) != digest:
            raise ValueError("Frozen source hash differs: " + name)
    env = baseline["env"]
    cache_keys = (
        "FLASHINFER_WORKSPACE_BASE",
        "TRITON_CACHE_DIR",
        "XDG_CACHE_HOME",
        "CUDA_CACHE_PATH",
    )
    cache_env = {name: env[name] for name in cache_keys}
    cache_root = Path(cache_env["FLASHINFER_WORKSPACE_BASE"]).resolve()
    if cache_root != baseline_run / "compiled-cache" or not cache_root.is_dir():
        raise ValueError("Original compiled cache root missing or unexpected")
    for name, path in cache_env.items():
        resolved = Path(path).resolve()
        if resolved != cache_root and cache_root not in resolved.parents:
            raise ValueError(
                "Cache environment escapes the original compiled-cache root"
            )
    knob = output / "knobs.json"
    if knob.exists() or knob.is_symlink():
        raise ValueError("Diagnostic knob file must initially be absent")
    return source, output, baseline_path, baseline, cache_env, str(knob)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--baseline-invocation", required=True, type=Path)
    cli = parser.parse_args()
    source, output, baseline_path, baseline, cache_env, knob = prepare_contract(
        cli.source_root, cli.output_root, cli.baseline_invocation
    )
    if (
        int(os.environ.get("WORLD_SIZE", "0")) != 4
        or os.environ.get("CUDA_VISIBLE_DEVICES") != "0,1,2,3"
    ):
        raise ValueError("This bounded diagnostic requires EP4 on visible GPUs 0,1,2,3")
    # Reuse existing compiled code; the new knob/output paths cannot replace r3 data.
    os.environ.update(cache_env)
    os.environ["FLASHINFER_MOE_EP_KNOB_CACHE"] = knob
    for name in (
        "FLASHINFER_CUDA_ARCH_LIST",
        "FLASHINFER_NVCC_THREADS",
        "MAX_JOBS",
        "NCCL_NVLS_ENABLE",
    ):
        if name in baseline["env"]:
            os.environ[name] = baseline["env"][name]
    sys.path[:0] = [str(source / "benchmarks"), str(source)]
    import torch
    import torch.distributed as dist
    import flashinfer
    from flashinfer.autotuner import AutoTuner

    split_module = importlib.import_module(
        "flashinfer.fused_moe.cute_dsl.blackwell.moe_w4a16"
    )
    from flashinfer.moe_ep.backends.mega.kernel.sm100.bf16_nvfp4_bf16_cutedsl.backend import (
        Bf16Nvfp4CutedslMegaKernelBackend as MegaBackend,
    )

    bench = importlib.import_module("bench_cute_dsl_moe_distributed")
    if (
        Path(bench.__file__).resolve()
        != source / "benchmarks/bench_cute_dsl_moe_distributed.py"
    ):
        raise ValueError("Unexpected benchmark import")
    if source not in Path(flashinfer.__file__).resolve().parents:
        raise ValueError("FlashInfer import escaped frozen source")
    rank, local_rank = int(os.environ["RANK"]), int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)
    device = torch.device("cuda", local_rank)
    dist.init_process_group("nccl", timeout=timedelta(seconds=300))
    setup_error = None
    if rank == 0:
        try:
            output.mkdir(parents=True, exist_ok=False)
        except Exception as error:
            setup_error = repr(error)
    gate = [setup_error]
    dist.broadcast_object_list(gate, src=0)
    if gate[0] is not None:
        raise RuntimeError(gate[0])
    bench.CFG = replace(bench.CFG, **bench.model_shape("glm-5.2"))
    bench.BASE_INTERMEDIATE_SIZE = bench.CFG.intermediate_size
    args = SimpleNamespace(
        ep_communication="allgather",
        precomputed_routing=False,
        enable_pdl=True,
        use_per_token_activation=False,
        use_fused_finalize=False,
        megamoe_knobs=None,
        megamoe_max_tokens_per_rank=None,
        apply_topk_in_fc1=False,
    )
    variant = next(v for v in bench.BENCH_VARIANTS if v.name == "w4a16")
    state = {"arm": None, "num_tokens": None, "capture": {}}
    originals = {}

    def patch(obj, name, replacement):
        originals[(obj, name)] = getattr(obj, name)
        setattr(obj, name, replacement)

    def cpu(tensor):
        return tensor.detach().cpu().clone()

    def capture_allowed():
        return (
            not AutoTuner.get().is_tuning_mode
            and not torch.cuda.is_current_stream_capturing()
        )

    original_inputs = bench._create_distributed_inputs

    def inputs(*a, **kw):
        value = original_inputs(*a, **kw)
        state["capture"][state["arm"] + "_inputs"] = {
            k: cpu(v)
            for k, v in zip(
                ("hidden_states", "local_logits", "global_logits", "routing_bias"),
                value,
            )
        }
        return value

    patch(bench, "_create_distributed_inputs", inputs)
    original_pack = bench._make_distributed_activation_pack

    def pack(*a, **kw):
        value = original_pack(*a, **kw)
        if state["arm"] == "split" and capture_allowed():
            state["capture"]["split_activation"] = {
                name: cpu(getattr(value, name))
                for name in ("hidden_states_q", "topk_ids", "topk_weights")
            }
        return value

    patch(bench, "_make_distributed_activation_pack", pack)
    original_unpermute = split_module.moe_unpermute

    def unpermute(*a, **kw):
        result = original_unpermute(*a, **kw)
        if state["arm"] == "split" and capture_allowed():
            if a:
                raise ValueError(
                    "Frozen unpermute call unexpectedly uses positional arguments"
                )
            if kw["num_tokens"] != 4:
                raise ValueError("Expected four padded global rows")
            torch.cuda.synchronize()
            mapping = kw["expanded_idx_to_permuted_idx"].reshape(4, 8)
            valid = mapping >= 0
            safe = mapping.clamp_min(0).long().flatten()
            terms = kw["permuted_input"].index_select(0, safe).reshape(4, 8, 6144)
            terms.masked_fill_(~valid[:, :, None], 0)
            state["capture"]["split_route_fc2"] = {
                "terms": cpu(terms),
                "valid": cpu(valid),
                "mapping": cpu(mapping),
                "routing_weights": cpu(kw["topk_scales"]),
                "rank_partial": cpu(kw["output"]),
            }
        return result

    patch(split_module, "moe_unpermute", unpermute)
    original_rs = dist.reduce_scatter_tensor

    def reduce_scatter(out, inp, *a, **kw):
        result = original_rs(out, inp, *a, **kw)
        if state["arm"] == "split" and capture_allowed():
            if kw.get("async_op", False):
                raise ValueError("Unexpected asynchronous reduction")
            state["capture"]["split_collective"] = {
                "rank_partial": cpu(inp),
                "result_with_padding": cpu(out),
            }
        return result

    patch(dist, "reduce_scatter_tensor", reduce_scatter)
    original_gemm = split_module._run_grouped_gemm

    def grouped_gemm(*a, **kw):
        result = original_gemm(*a, **kw)
        if state["arm"] == "split" and capture_allowed():
            phase = "fc1" if kw["activation_type"] is not None else "fc2"
            state["capture"].setdefault("split_tactics", {})[phase] = repr(
                kw.get("tactic")
            )
        return result

    patch(split_module, "_run_grouped_gemm", grouped_gemm)
    original_compute = MegaBackend.compute

    def mega_compute(self, workspace, transformed_weights, *, output):
        result = original_compute(self, workspace, transformed_weights, output=output)
        if state["arm"] == "mega" and capture_allowed():
            n = output.shape[0]
            if workspace._frontend.config.in_kernel_fc2_reduce:
                raise ValueError("Expected external K8 reduction for this diagnostic")
            if workspace.combine_output.shape != (1, 8, 6144):
                raise ValueError("Unexpected Mega per-route buffer shape")
            torch.cuda.synchronize()
            state["capture"]["mega_workspace"] = {
                "hidden_states": cpu(workspace.x[:n]),
                "topk_ids": cpu(workspace.topk_idx[:n]),
                "topk_weights": cpu(workspace.topk_weights[:n]),
                "route_fc2": cpu(workspace.combine_output[:n]),
                "output": cpu(result),
                "resolved_config": asdict(workspace._frontend.config),
            }
        return result

    patch(MegaBackend, "compute", mega_compute)
    original_check = bench._check_megamoe_output

    def check(actual, expected, group, dev, rnk, n):
        a, b = cpu(actual).float(), cpu(expected).float()
        error = (a - b).abs()
        threshold = 0.01 + 0.01 * b.abs()
        mask = (~torch.isfinite(a)) | (~torch.isfinite(b)) | (error > threshold)
        state["capture"]["refcheck"] = {
            "actual": cpu(actual),
            "reference": cpu(expected),
            "error": error,
            "threshold": threshold,
            "mismatch_mask": mask,
            "mismatch_count": int(mask.sum()),
            "first_mismatch_coordinates": mask.nonzero()[:64],
            "max_abs": float(error.max()) if error.numel() else 0.0,
            "max_error_over_threshold": float((error / threshold).max())
            if error.numel()
            else 0.0,
            "all_finite": bool(torch.isfinite(a).all() and torch.isfinite(b).all()),
        }
        try:
            original_check(actual, expected, group, dev, rnk, n)
        except Exception as exc:
            state["capture"]["strict_refcheck_status"] = "FAIL"
            state["capture"]["strict_refcheck_error"] = str(exc)
            raise
        state["capture"]["strict_refcheck_status"] = "PASS"

    patch(bench, "_check_megamoe_output", check)
    # Keep native setup/tuning/initial-reference code; exclude timing, graphs and extra forwards.
    patch(bench, "_run_distributed_iterations", lambda *a, **kw: None)
    provenance = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": SOURCE_COMMIT,
        "runtime_base": RUNTIME_BASE,
        "source_sha256": SOURCE_SHA,
        "helper_sha256": sha(__file__),
        "baseline_invocation": str(baseline_path),
        "baseline_invocation_sha256": sha(baseline_path),
        "imports": {"flashinfer": flashinfer.__file__, "benchmark": bench.__file__},
        "compiled_cache_reused": cache_env,
        "new_knob_cache": knob,
        "knob_initially_absent": not Path(knob).exists(),
        "tokens": [1, 3],
        "split_tune_max_tokens": 16384,
        "enable_pdl": True,
        "world_size": 4,
        "rank": rank,
        "gpu": torch.cuda.get_device_name(local_rank),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "nccl": torch.cuda.nccl.version(),
        "atol": 0.01,
        "rtol": 0.01,
        "eager_only": True,
        "timing_enabled": False,
        "observer_limitations": "CPU snapshots/synchronization outside autotune perturb scheduling. Native source and strict reference check unchanged. Skipping r3 graph/timing calls does not replay its allocator/autotuner/graph state exactly; diagnostic output is not performance evidence.",
    }
    write_json(output / f"provenance-rank{rank}.json", provenance)
    failed = False
    try:
        for n in (1, 3):
            state.update(num_tokens=n, arm="split", capture={})
            shared = bench._create_shared_ep_weights(rank, 4, device)
            references = {}
            failure = None
            try:
                bench._benchmark_distributed_gather_ep(
                    args,
                    variant,
                    n,
                    4096,
                    rank,
                    4,
                    device,
                    prepared_weights=shared[0],
                    reference_outputs=references,
                )
                state["capture"]["split_saved_reference"] = cpu(references["w4a16"])
                dist.barrier()
                gc.collect()
                torch.cuda.empty_cache()
                state["arm"] = "mega"
                bench._benchmark_distributed_megamoe(
                    args, n, rank, 4, device, shared[1], references
                )
            except Exception as exc:
                failure = repr(exc)
                failed = True
            folder = output / f"n{n}"
            folder.mkdir(exist_ok=True)
            payload = folder / f"rank{rank}.pt"
            with payload.open("xb") as stream:
                torch.save(state["capture"], stream)
            r = state["capture"].get("refcheck", {})
            write_json(
                folder / f"rank{rank}.json",
                {
                    "global_tokens": n,
                    "rank": rank,
                    "local_tokens": bench._token_partition(n, rank, 4)[0],
                    "strict_refcheck_status": state["capture"].get(
                        "strict_refcheck_status", "NOT_REACHED"
                    ),
                    "error": failure,
                    "payload_sha256": sha(payload),
                    "payload_bytes": payload.stat().st_size,
                    "captured_fields": list(state["capture"]),
                    "mismatch_count": r.get("mismatch_count"),
                    "max_abs": r.get("max_abs"),
                    "max_error_over_threshold": r.get("max_error_over_threshold"),
                    "all_finite": r.get("all_finite"),
                },
            )
            del shared, references
            if failed:
                break
            dist.barrier()
            gc.collect()
            torch.cuda.empty_cache()
    finally:
        for (obj, name), fn in originals.items():
            setattr(obj, name, fn)
        write_json(
            output / f"exit-rank{rank}.json",
            {
                "failed": failed,
                "exit_code": 1 if failed else 0,
                "strict_gate_preserved": True,
                "finished_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        dist.destroy_process_group()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
