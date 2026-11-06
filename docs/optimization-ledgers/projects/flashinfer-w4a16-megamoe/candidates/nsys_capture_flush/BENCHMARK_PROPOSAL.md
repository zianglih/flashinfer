# Minimal benchmark profiling proposal

Reviewable, unapplied patch: `benchmark_patch/nsys-options.patch`. Base/candidate source and hashes are saved beside it. No active repository edit. The validated capture is `tmem-fitted5-transform2-nsys-software-001`, exact source fe4f8132, both T32/T4096. Its expected 16 measured launches across eight devices pass the strict check; the prior hardware-trace finite-exit capture still missed GPU2.

Add two independent optional arguments to `benchmarks/bench_cute_dsl_moe_distributed.py`:

- `--nsys-cuda-trace {cuda,cuda-sw}`, default `cuda`. Build the existing trace list as `<selected>,nvtx,nccl`. Help text states that `cuda-sw` requests Nsight software CUDA tracing when hardware tracing loses events. It requires a Nsight version supporting that token; propagate normal profiler errors rather than inventing version fallback logic.
- `--nsys-capture-range-end {stop,none}`, default `stop`. Pass the value to the existing Nsight option. `none` leaves collection open after `cudaProfilerStop` until the finite worker tree exits. Nsight already defaults to waiting for all children; no extra wait/kill/session controls are needed for natural finite exit. Retain the existing measured NVTX filtering to exclude teardown activity.

These are launcher-only controls. They do not alter worker kernels, timing loops, numerical checks, precision, backend selection, NCU mode or graph behavior. They need not be forwarded to worker arguments because only the outer process invokes Nsight. The verbose command already records the resolved values. A named session and external-stop/held-worker machinery are unnecessary for finite-exit operation and should remain effort-only diagnostics.

The reproducible direct command would be:

```bash
python3 benchmarks/bench_cute_dsl_moe_distributed.py \
  --num-gpus=8 --parallel-modes=ep --variants=w4a16_megamoe \
  --num-tokens=32,4096 --warmup=3 --iters=1 --no-fused-finalize \
  --megamoe-knobs='{"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"load_balance_mode":"atomic_counter","token_back_mode":"epi_warps"}' \
  --mode=profile_nsys --profile-iters=2 --verbose \
  --nsys-cuda-trace=cuda-sw --nsys-capture-range-end=none \
  --nsys-output-dir=/workspace/flashinfer-w4a16-megamoe/profiles/<fresh-run>
```

Validation after approval: CPU parser/command-construction checks must preserve existing default argv exactly, keep JSON boundaries and verify each flag independently. Then repeat both measured shapes with the direct benchmark command, removing the effort wrapper from PATH. Require the same 16-instance/eight-device resource audit and inspect per-process CUDA diagnostics. The proven wrapper run is evidence for the proposal, not a substitute for validating the final direct launcher.

Artifact CPU validation passes: five AST-extracted parser/command tests check default full argv equality, each independent option, combined flags with exact worker JSON boundaries, rejection of invalid values and unchanged ASTs for every other benchmark function. `python3 candidates/nsys_capture_flush/benchmark_patch/test_cli.py` imports no GPU libraries and launches nothing. Candidate syntax, Ruff/format and `git apply --check` pass. The production patch is exactly two command substitutions and two parser options; it includes no effort tests, wrapper, sessions, tail workers or extra default flags.

Do not make software trace or finite-exit capture the default on this evidence. Only this B300/Nsight2026.2.1 failure and workaround were investigated; original behavior and compatibility should remain available for existing users/backends. If only one option is desired, `--nsys-cuda-trace` alone has not been GPU-tested with the original `capture-range-end=stop` combination, so retaining both explicit controls is the smallest proposal that expresses the validated setup without coupling unrelated settings.
