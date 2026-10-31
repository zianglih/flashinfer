"""Preserve native benchmark results after each token's timed work has returned."""

import argparse
import contextlib
import functools
from dataclasses import asdict
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
import time

from arm_contracts import DEFAULT_LABELS, INITIAL_ACTIVATION_QUANTIZATION, arm_contract, selected_labels, unavailable_labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--w4a16-only", action="store_true")
    parser.add_argument("--w4a4-only", action="store_true")
    parser.add_argument("benchmark_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cli = args.benchmark_args
    if cli and cli[0] == "--":
        cli = cli[1:]
    if cli.count("--model") != 1:
        raise ValueError("An explicit model is required")
    model = cli[cli.index("--model") + 1]
    family = cli[cli.index("--quant-family") + 1]
    selectors = cli[cli.index("--backends") + 1] if "--backends" in cli else None
    include_activation_quant = "--include-activation-quant" in cli
    if include_activation_quant != INITIAL_ACTIVATION_QUANTIZATION[family]:
        raise ValueError("Benchmark quantization flag differs from this campaign")
    requested_labels = selected_labels(family, selectors)
    assert not (args.w4a16_only and args.w4a4_only)
    if args.w4a16_only or args.w4a4_only:
        assert family == "nvfp4" and selectors == "cutedsl"
        requested_labels = ("CuteDSL W4A16" if args.w4a16_only else "CuteDSL W4A4",)
    expected_unavailable = unavailable_labels(model, family, requested_labels)
    requested_tokens = [int(t) for t in cli[cli.index("--num-tokens") + 1].split(",")]
    repo, output = args.repo.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = repo / "benchmarks/bench_moe_deepseek.py"
    sys.path.insert(0, str(repo))
    sys.path.insert(0, str(source.parent))
    spec = importlib.util.spec_from_file_location("gather_pipeline_native_benchmark", source)
    benchmark = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = benchmark
    spec.loader.exec_module(benchmark)
    from flashinfer.autotuner import AutoTuner
    from flashinfer.autotuner.autotuner import _tactic_to_json

    swap_ab = "--swap-ab" in cli
    use_fused_finalize = "--no-fused-finalize" not in cli
    has_swap_ab_skip = "swap_ab" in inspect.signature(benchmark._backend_skip_reason).parameters

    def skip_reason(label):
        if has_swap_ab_skip:
            return benchmark._backend_skip_reason(label, swap_ab, use_fused_finalize)
        return benchmark._backend_skip_reason(label)


    # Observe only public measurements; leave native AUTO profiling untouched.
    import warnings
    import numpy as np
    import flashinfer.testing.utils as testing_utils
    warnings.filterwarnings("error", message=".*Falling back to CUDA events.*")
    native_search = "--no-autotune" not in cli
    input_cache = Path(cli[cli.index("--cache") + 1])
    if native_search:
        assert not input_cache.exists(), "Native search requires a fresh managed cache directory"
    else:
        assert input_cache.is_dir(), "Replay requires the freshly tuned managed cache"

    def cache_manifest():
        return {
            str(path.relative_to(input_cache)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(input_cache.rglob("*")) if path.is_file()
        }

    cache_before = cache_manifest() if input_cache.exists() else {}
    profile_calls = 0
    observations = {
        "native_search": native_search,
        "measurements": [],
        "searches": [],
        "autotune_contexts": [],
        "admitted_tactics": [],
    }
    from flashinfer.fused_moe.cute_dsl import tuner as moe_tuner
    from nested_timing import install
    telemetry = install(AutoTuner) if native_search else None
    if telemetry is not None:
        observations["nested_wall_timing"] = telemetry.report

    observations["raw_tactic_counts"] = {
        "w4a16": len(moe_tuner.W4A16_MOE_TACTICS),
        "blackwell": len(moe_tuner.ALL_BLACKWELL_MOE_TACTICS),
        "w4a8": len(moe_tuner.ALL_W4A8_MOE_TACTICS),
    }
    original_valid = moe_tuner.CuteDslFusedMoERunner.get_valid_tactics

    def observed_valid(self, inputs, profile):
        started = time.monotonic()
        tactics = original_valid(self, inputs, profile)
        admission_wall = time.monotonic() - started
        # Record after the existing admission checks; do not time or reorder
        # candidates, and do not inspect tensor contents or synchronize here.
        encoded = json.dumps(tactics, separators=(",", ":")).encode()
        input_shapes = []
        for value in inputs:
            if value is None:
                input_shapes.append(None)
            elif isinstance(value, benchmark.torch.Tensor):
                input_shapes.append(list(value.shape))
            else:
                raise TypeError(f"Unexpected MoE autotune input: {type(value).__name__}")
        observations["admitted_tactics"].append({
            "runner": type(self).__name__,
            "quant_mode": self.quant_mode,
            "per_token_activation": self.use_per_token_activation,
            "input_shapes": input_shapes,
            "count": len(tactics),
            "tactics_sha256": hashlib.sha256(encoded).hexdigest(),
            "admission_wall_seconds": admission_wall,
        })
        return tactics

    moe_tuner.CuteDslFusedMoERunner.get_valid_tactics = observed_valid
    original_w4_valid = moe_tuner.CuteDslFusedMoEW4A16Runner.get_valid_tactics
    def observed_w4_valid(self, inputs, profile):
        started = time.monotonic()
        tactics = original_w4_valid(self, inputs, profile)
        observations["admitted_tactics"].append({
            "runner": type(self).__name__, "quant_mode": "w4a16",
            "input_shapes": [list(x.shape) if x is not None else None for x in inputs],
            "count": len(tactics), "tactics": json.loads(json.dumps(tactics)),
            "admission_wall_seconds": time.monotonic() - started,
        })
        return tactics
    moe_tuner.CuteDslFusedMoEW4A16Runner.get_valid_tactics = observed_w4_valid
    original_context = benchmark._autotune_context

    @contextlib.contextmanager
    def observed_context(do_autotune, cache, measurement_policy=None):
        started = time.monotonic()
        before = len(observations["admitted_tactics"])
        timing = telemetry.span("context") if telemetry is not None else contextlib.nullcontext()
        with timing, original_context(do_autotune, cache, measurement_policy):
            yield
        observations["autotune_contexts"].append({
            "enabled": bool(do_autotune),
            "measurement_policy": measurement_policy.manifest_fields() if measurement_policy else None,
            "wall_seconds": time.monotonic() - started,
            "admission_calls": len(observations["admitted_tactics"]) - before,
            "boundary": "Public pre-warm context, including JIT, cache IO, native profiling, and pre-warm launches; not isolated profiling time.",
        })

    benchmark._autotune_context = observed_context
    active_measurement = None
    from w4_resolution_observer import install as install_w4_resolution
    install_w4_resolution(moe_tuner, lambda: active_measurement, _tactic_to_json)
    expected_operation = None
    original_profile = AutoTuner._profile_single_kernel

    def guarded_profile(self, *args, **kwargs):
        nonlocal profile_calls
        assert active_measurement is None, "Autotuning attempted during public measurement"
        assert native_search, "Replay attempted fresh tactic profiling"
        assert self.is_tuning_mode, "Profiling outside a tuning context"
        profile_calls += 1
        return original_profile(self, *args, **kwargs)

    AutoTuner._profile_single_kernel = guarded_profile

    def observe_backend(original, backend):
        signature = inspect.signature(original)

        @functools.wraps(original)
        def call(*args, **kwargs):
            nonlocal expected_operation
            assert expected_operation is None
            if backend == "cute-dsl":
                operation = "CuteDslFusedMoE::" if "--functional-api" in cli else "CuteDslMoEWrapper::"
            elif backend == "trtllm":
                bound = signature.bind(*args, **kwargs)
                bound.apply_defaults()
                precision = bound.arguments["precision"]
                if precision == "mxfp8":
                    operation = "flashinfer::trtllm_fp8_block_scale_moe"
                elif precision in ("nvfp4", "mxfp4"):
                    operation = "flashinfer::trtllm_fp4_block_scale_moe"
                else:
                    raise ValueError(f"Unexpected benchmark precision: {precision}")
            else:
                raise ValueError(backend)
            expected_operation = operation
            try:
                return original(*args, **kwargs)
            finally:
                expected_operation = None
        return call

    benchmark.bench_cute_dsl = observe_backend(benchmark.bench_cute_dsl, "cute-dsl")
    benchmark.bench_trtllm = observe_backend(benchmark.bench_trtllm, "trtllm")
    # Native AUTO retains its own timer. Public reported measurements must
    # never fall back to event timing, including fallback without a warning.
    def guarded_fallback(original):
        def call(*args, **kwargs):
            if active_measurement is not None:
                raise RuntimeError("CUPTI public measurement fell back to CUDA events")
            return original(*args, **kwargs)
        return call

    testing_utils.bench_gpu_time_with_cudagraph = guarded_fallback(
        testing_utils.bench_gpu_time_with_cudagraph
    )
    testing_utils.bench_gpu_time_with_cuda_event = guarded_fallback(
        testing_utils.bench_gpu_time_with_cuda_event
    )
    timer_source = inspect.getsource(testing_utils.bench_gpu_time_with_cupti)
    timer_return = "    measured_times = aggregate_gpu_time_across_ranks(measured_times, aggregate_op)\n    return measured_times"
    assert timer_source.count(timer_return) == 1
    diagnostic_source = timer_source.replace(timer_return, timer_return.replace("    return measured_times", "    _handoff_activities.append((list(kernels), list(launches), list(iter_timestamps)))\n    return measured_times"))
    testing_utils._handoff_activities = []
    exec(diagnostic_source, testing_utils.__dict__)
    observations['timer_source_sha256'] = hashlib.sha256(timer_source.encode()).hexdigest()
    observations['diagnostic_timer_source_sha256'] = hashlib.sha256(diagnostic_source.encode()).hexdigest()
    observations['activity_boundary'] = 'Host-only copy of collected CUPTI activities after normal timing aggregation; measured function, arguments, execution and timing policy unchanged.'
    original_timer = testing_utils.bench_gpu_time
    def observed_timer(*args, **kwargs):
        if active_measurement is None:
            return original_timer(*args, **kwargs)
        assert kwargs.get("dry_run_iters") == 10
        assert kwargs.get("repeat_iters") == 100
        assert kwargs.get("cold_l2_cache") is True
        assert kwargs.get("enable_cupti") is True
        assert kwargs.get("use_cuda_graph") is True
        times = original_timer(*args, **kwargs)
        activities, launches, timestamps = testing_utils._handoff_activities.pop()
        assert not testing_utils._handoff_activities
        active_measurement['activities'] = [list(x[:-1]) + [int(x[-1])] for x in activities]
        active_measurement['launches'] = [list(x[:-1]) + [int(x[-1])] for x in launches]
        active_measurement['iter_timestamps'] = timestamps
        active_measurement["milliseconds"] = [float(t) for t in times]
        active_measurement["median_ms"] = float(np.median(times))
        active_measurement["timer"] = "CUPTI"
        active_measurement["event_fallback_forbidden"] = True
        return times
    testing_utils.bench_gpu_time = observed_timer
    # Passive host-only allocation metadata; no tensor contents or synchronization.
    swap_host = importlib.import_module('flashinfer.fused_moe.cute_dsl.blackwell.moe_swap_ab')
    import cutlass.cute as cute
    original_compile = cute.compile
    observations['resources'] = []
    def record_compile(*args, **kwargs):
        kernel = getattr(args[0], '__self__', None)
        compiled = original_compile(*args, **kwargs)
        if type(kernel).__name__ == 'Sm100BlockScaledGroupedGemmKernel':
            attrs = ('gather_input', 'use_clc_scheduler', 'route_tile', 'cta_group_size', 'tile_k', 'num_stages', 'acc_stages', 'acc_cols', 'sf_cols', 'sfb_cols', 'tmem_cols', 'overlap_acc', 'acc_window_stride', 'protected_acc_cols', 'num_tile_info_stages', 'native_mma_k')
            row = {a: getattr(kernel, a) for a in attrs}
            row.update(bulk_tokens=kernel.epilogue.bulk_tokens, bulk_stages=kernel.epilogue.bulk_stages, shared_bytes=kernel.storage_type.size_in_bytes(), operand_stage_bytes=kernel._stage_storage_bytes(kernel.tile_k, kernel.allocated_n, kernel.cta_group_size, kernel.channel_tiles, kernel.activation_dtype, kernel.weight_dtype, kernel.sf_vec_size))
            observations['resources'].append(row)
        return compiled
    cute.compile = record_compile
    original_gemm = swap_host._run_blockscaled_gemm
    def observe_gemm(**kw):
        result = original_gemm(**kw)
        if active_measurement is not None and kw['scatter_output']:
            out = kw['output']
            record = dict(num_tokens=kw['num_tokens'], top_k=kw['top_k'],
                          output_shape=list(out.shape), output_bytes=out.numel()*out.element_size(),
                          route_capacity=kw['token_mapping'].numel(), dtype=str(out.dtype),
                          mma_tiler_mn=list(kw['mma_tiler_mn']), cluster_shape_mn=list(kw['cluster_shape_mn']),
                          use_clc_scheduler=kw['use_clc_scheduler'], use_fused_finalize=kw['use_fused_finalize'])
            seen = active_measurement.setdefault('fc2_outputs', [])
            if record not in seen: seen.append(record)
        return result
    swap_host._run_blockscaled_gemm = observe_gemm
    original_measure = benchmark._measure_or_profile
    def observed_measure(*args, **kwargs):
        nonlocal active_measurement
        assert active_measurement is None
        assert expected_operation is not None
        tuner = AutoTuner.get()
        assert not tuner.is_tuning_mode, "Public measurement must use replay mode"
        policy = tuner._effective_measure_policy
        current = {"cache_hits": [], "expected_operation": expected_operation,
                   "tuning_mode": tuner.is_tuning_mode,
                   "measurement_policy": policy.manifest_fields() if policy else None,
                   "profile_calls_before": profile_calls}
        active_measurement = current
        try:
            result = original_measure(*args, **kwargs)
        finally:
            active_measurement = None
        current["profile_calls_after"] = profile_calls
        assert current["profile_calls_before"] == profile_calls
        assert len(current["milliseconds"]) == 100
        assert any(record["operation"].startswith(current["expected_operation"])
                   for record in current["cache_hits"]), current
        observations["measurements"].append(current)
        return result
    benchmark._measure_or_profile = observed_measure
    original_search = AutoTuner.search_cache
    def observed_search(self, custom_op, runners, input_shapes, tuning_config, inputs=None, **kwargs):
        result = original_search(self, custom_op, runners, input_shapes, tuning_config, inputs, **kwargs)
        is_cute = custom_op.startswith(("CuteDslMoEWrapper::", "CuteDslFusedMoE::"))
        is_trtllm = custom_op in ("flashinfer::trtllm_fp4_block_scale_moe",
                                 "flashinfer::trtllm_fp8_block_scale_moe")
        if is_cute or is_trtllm:
            hit, runner_id, tactic, _ = result
            record = {"hit": bool(hit), "operation": custom_op,
                "tactic": _tactic_to_json(tactic)}
            if is_cute and hit and tactic != -1 and "w4a16" not in custom_op.lower() and "--swap-ab" in cli:
                from flashinfer.fused_moe.cute_dsl.blackwell.moe_swap_ab_tuner import (
                    canonicalize_swap_ab_tactic,
                )
                use_clc = canonicalize_swap_ab_tactic(tactic)[4]
                record["fc1_clc"] = use_clc
                record["fc2_clc"] = use_clc
            if hit:
                runner = runners[runner_id]
                key = self._get_cache_key(custom_op, runner, input_shapes, tuning_config,
                    runner.get_cache_key_extras(inputs) if inputs is not None else ()).file_key
                record.update(key=key, runner=type(runner).__name__)
                record["profiling_policy"] = list(self._profiling_policy(tuning_config))
                record["use_cuda_graph"] = tuning_config.use_cuda_graph
            if active_measurement is not None:
                assert hit, "Native winner must exist before public measurement"
                active_measurement["cache_hits"].append(record)
            # Compile/tune observations can be numerous; only save unique facts.
            if record not in observations["searches"]:
                observations["searches"].append(record)
        return result
    AutoTuner.search_cache = observed_search

    receipt = {
        "complete": False,
        "native_diagnostic": observations,
        "benchmark": str(source),
        "benchmark_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "benchmark_argv": [str(source), *cli],
        "swap_ab": swap_ab,
        "use_fused_finalize": use_fused_finalize,
        "arm_contracts_sha256": hashlib.sha256(Path(__file__).with_name("arm_contracts.py").read_bytes()).hexdigest(),
        "rows": [],
        "boundary": "Native medians and their 100 raw public timing samples, existing route identities, and observed native AUTO admission counts. No new numerical test or tactic selection override.",
    }

    def save():
        (output / "results.json").write_text(
            json.dumps(receipt, indent=2, allow_nan=False) + "\n"
        )

    quant_env_keys = (
        "FLASHINFER_DISABLE_FP4_QUANT_FAST_MATH",
        "TRTLLM_DISABLE_FP4_QUANT_FAST_MATH",
        "FLASHINFER_NVFP4_4OVER6",
        "FLASHINFER_NVFP4_4OVER6_ERR_MODE",
        "FLASHINFER_NVFP4_4OVER6_ERR_USE_FAST_MATH",
        "FLASHINFER_NVFP4_4OVER6_E4M3_USE_256",
    )

    def quant_env():
        return {key: os.environ.get(key) for key in quant_env_keys}

    receipt["ambient_quantization_environment"] = quant_env()
    original = benchmark._benchmark_single
    original_histogram = benchmark._collect_expert_histogram
    pending_routes = {}

    def observed_histogram(inputs, num_local, local_offset):
        allocator = benchmark._routing_tensors
        captured = []

        def capture_existing_routes(*route_args, **route_kwargs):
            routes = allocator(*route_args, **route_kwargs)
            captured.append(routes)
            return routes

        # This wrapper is installed only during the benchmark's existing,
        # untimed histogram collection, then removed before backend work.
        benchmark._routing_tensors = capture_existing_routes
        try:
            result = original_histogram(inputs, num_local, local_offset)
        finally:
            benchmark._routing_tensors = allocator
        if len(captured) != 1:
            raise RuntimeError(
                "Expected one native routing allocation for the histogram"
            )
        pending_routes.update(
            tensors=captured[0],
            num_experts=benchmark.CFG.num_experts,
            num_local=num_local,
            local_offset=local_offset,
        )
        return result

    def observed_single(*call_args, **call_kwargs):
        pending_routes.clear()
        if call_kwargs.get("include_activation_quant", False) != include_activation_quant:
            raise RuntimeError("Benchmark did not forward the quantization timing flag")
        before_env = quant_env()
        if args.w4a16_only or args.w4a4_only:
            assert call_kwargs.get("profile_backend") is None
            assert not call_kwargs.get("profile_cuda", False)
            call_kwargs["profile_backend"] = (
                "cute-dsl-w4a16" if args.w4a16_only else "cute-dsl"
            )
        result = original(*call_args, **call_kwargs)
        after_env = quant_env()
        if before_env != after_env:
            raise RuntimeError("Benchmark leaked per-arm quantization environment")
        rows, histogram = result
        labels = [row.backend for row in rows]
        if len(labels) != len(set(labels)):
            raise RuntimeError("Duplicate backend labels would overwrite native medians")
        unavailable = {label: skip_reason(label) for label in requested_labels if skip_reason(label) is not None}
        if set(unavailable) != set(expected_unavailable) or not all(isinstance(reason,str) and reason for reason in unavailable.values()):
            raise RuntimeError("Model unsupported backend contract differs")
        supported = set(requested_labels) - set(unavailable)
        if set(labels) != supported:
            raise RuntimeError("Supported backend is missing or unsupported backend was timed")
        token = int(rows[0].tokens)
        cache = output / f"token_{token}.managed-cache-manifest.json"
        cache.write_text(json.dumps(cache_manifest(), indent=2) + "\n")
        weights, ids = (
            tensor.detach().cpu().contiguous() for tensor in pending_routes["tensors"]
        )
        full_histogram = (
            ids.reshape(-1).bincount(minlength=pending_routes["num_experts"]).tolist()
        )
        route_identity = {
            "ids_sha256": hashlib.sha256(ids.numpy().tobytes()).hexdigest(),
            "weights_sha256": hashlib.sha256(weights.numpy().tobytes()).hexdigest(),
            "ids_dtype": str(ids.dtype),
            "weights_dtype": str(weights.dtype),
            "shape": list(ids.shape),
            "full_expert_histogram": full_histogram,
            "local_expert_offset": pending_routes["local_offset"],
            "num_local_experts": pending_routes["num_local"],
            "capture": "Existing untimed histogram routing outputs; no extra routing invocation",
        }
        receipt["rows"].append(
            {
                "tokens": token,
                "include_activation_quant": include_activation_quant,
                "results": [asdict(row) for row in rows],
                "backend_labels": labels,
                "unavailable_backends": unavailable,
                "arm_contracts": {label: arm_contract(label) for label in labels},
                "quantization_environment_before": before_env,
                "quantization_environment_after": after_env,
                "histogram": histogram,
                "routing_identity": route_identity,
                "autotune_cache": cache.name,
                "autotune_cache_sha256": hashlib.sha256(cache.read_bytes()).hexdigest(),
            }
        )
        save()
        return result

    benchmark._collect_expert_histogram = observed_histogram
    benchmark._benchmark_single = observed_single
    sys.argv = [str(source), *cli]
    save()
    exit_code = benchmark.main()
    assert len(observations["measurements"]) == sum(len(r["results"]) for r in receipt["rows"])
    assert [r["latency_ms"] for row in receipt["rows"] for r in row["results"]] == [m["median_ms"] for m in observations["measurements"]]
    receipt["managed_cache"] = str(input_cache)
    receipt["managed_cache_before"] = cache_before
    receipt["managed_cache_after"] = cache_manifest()
    receipt["profile_calls"] = profile_calls
    if not native_search:
        assert cache_before == receipt["managed_cache_after"], "Replay mutated managed winners"
        assert profile_calls == 0
    receipt["complete"] = exit_code in (None, 0) and [row["tokens"] for row in receipt["rows"]] == requested_tokens
    receipt["exit_code"] = exit_code
    save()
    return exit_code


if __name__ == "__main__":
    from guard_observer_adapter import run
    sys.exit(run(main, __file__))
