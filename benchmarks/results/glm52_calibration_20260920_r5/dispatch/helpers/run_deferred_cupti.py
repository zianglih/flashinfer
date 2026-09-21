"""Experiment wrapper: untimed graph checks and one final CUPTI detach.

The pinned benchmark and its measured callable/timing helper remain unchanged.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


class DeferredFinalize:
    def __init__(self, cupti):
        self.cupti = cupti
        self.callbacks = []
        self.finalize_calls = 0
        self.finished = False
        self.original_register = cupti.activity_register_callbacks
        self.original_finalize = cupti.finalize
        cupti.activity_register_callbacks = self.register
        cupti.finalize = self.defer

    def register(self, *callbacks):
        self.callbacks.append(callbacks)
        return self.original_register(*callbacks)

    def defer(self):
        self.finalize_calls += 1

    def finish(self):
        if self.finished:
            raise RuntimeError("CUPTI finish must execute exactly once")
        self.finished = True
        try:
            # Keep callback references alive until this one detach completes.
            self.original_finalize()
        finally:
            self.cupti.activity_register_callbacks = self.original_register
            self.cupti.finalize = self.original_finalize
        return {
            "deferred_finalizes": self.finalize_calls,
            "registrations": len(self.callbacks),
            "final_detaches": 1,
        }


def emit(prefix, record):
    payload = (
        prefix + "," + json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    if len(payload) >= 4096:
        raise ValueError("Wrapper record exceeds the atomic pipe-write budget")
    os.write(1, payload)


def install_graph_check(native, torch):
    original = native._run_distributed_iterations

    def checked(args, run_once, profile_once, l2_flush, dist, device, label, tokens):
        if args.cuda_graph:
            if not args.refcheck or args.mode != "benchmark":
                raise ValueError(
                    "Graph output validation requires benchmark --refcheck"
                )
            if not label.startswith("ep::"):
                raise ValueError("Calibration graph checks support EP outputs only")
            local_tokens, _ = native._token_partition(
                tokens, dist.get_rank(), dist.get_world_size()
            )

            def valid_output(output):
                # A2A combine may return padded/3D storage. Match the native
                # reference's slice of the source rank's real, owned rows.
                return output.reshape(-1, native.CFG.hidden_size)[:local_tokens]

            # Match the benchmark's ordinary side-stream capture arrangement.
            # Warmups, reference, capture, and checks are all outside its timer.
            for _ in range(3):
                eager = run_once()
            reference = valid_output(eager).detach().clone()
            torch.cuda.synchronize()
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                captured = run_once()
            maximum_error = 0.0
            try:
                for replay in range(2):
                    # These benchmark paths return owned output (or the
                    # gather path's dedicated reduced buffer), not input/state.
                    # Poison real rows so a no-op replay cannot reuse correct
                    # values left by capture or the previous replay.
                    valid_output(captured).fill_(float("nan"))
                    graph.replay()
                    torch.cuda.synchronize()
                    actual, expected = valid_output(captured).float(), reference.float()
                    error = (actual - expected).abs()
                    invalid = (
                        ~torch.isfinite(actual)
                        | ~torch.isfinite(expected)
                        | (error > 1e-2 + 1e-2 * expected.abs())
                    )
                    maxima = torch.stack(
                        (
                            invalid.any().float(),
                            error.max()
                            if error.numel()
                            else torch.zeros((), device=device),
                        )
                    )
                    dist.all_reduce(maxima, op=dist.ReduceOp.MAX)
                    maximum_error = max(maximum_error, maxima[1].item())
                    if maxima[0].item():
                        raise AssertionError(
                            f"Graph/eager mismatch {label} N={tokens} replay={replay + 1} "
                            f"atol=rtol=1e-2 max_abs={maxima[1].item()}"
                        )
            finally:
                graph.reset()
            if dist.get_rank() == 0:
                emit(
                    "GRAPH_REFCHECK_JSON",
                    {
                        "profile_label": label,
                        "global_tokens": tokens,
                        "world_size": dist.get_world_size(),
                        "status": "PASS",
                        "atol": 1e-2,
                        "rtol": 1e-2,
                        "max_abs": maximum_error,
                        "extra_untimed_eager_forwards": 3,
                        "extra_untimed_captures": 1,
                        "checked_untimed_replays": 2,
                        "outputs_poisoned_before_each_replay": True,
                        "all_ranks_checked": True,
                        "timed_replays_checked": False,
                    },
                )
        return original(
            args, run_once, profile_once, l2_flush, dist, device, label, tokens
        )

    native._run_distributed_iterations = checked


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--validate-graph-output", action="store_true")
    wrapper_args, native_args = parser.parse_known_args()
    sys.argv = [sys.argv[0], *native_args]
    source = Path.cwd()
    sys.path.insert(0, str(source / "benchmarks"))
    spec = importlib.util.spec_from_file_location(
        "frozen_benchmark", source / "benchmarks/bench_cute_dsl_moe_distributed.py"
    )
    native = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = native
    spec.loader.exec_module(native)
    import torch
    import flashinfer

    if not Path(flashinfer.__file__).resolve().is_relative_to(source / "flashinfer"):
        raise RuntimeError(f"Unexpected FlashInfer import: {flashinfer.__file__}")
    lifecycle = None
    if (
        "--timing" in native_args
        and native_args[native_args.index("--timing") + 1] == "cupti"
    ):
        from cupti import cupti

        lifecycle = DeferredFinalize(cupti)
    if wrapper_args.validate_graph_output:
        install_graph_check(native, torch)
    try:
        return native.main()
    finally:
        # native.main destroys its process group before returning/raising. Do
        # not introduce a barrier in failure cleanup: another rank may have died.
        try:
            torch.cuda.synchronize()
        finally:
            record = (
                lifecycle.finish()
                if lifecycle
                else {
                    "deferred_finalizes": 0,
                    "registrations": 0,
                    "final_detaches": 0,
                }
            )
            emit(
                "CALIBRATION_WRAPPER_FINISH_JSON",
                {
                    **record,
                    "rank": int(os.environ.get("RANK", "0")),
                    "cupti_used": lifecycle is not None,
                    "graph_output_validation_requested": wrapper_args.validate_graph_output,
                },
            )


if __name__ == "__main__":
    raise SystemExit(main())
