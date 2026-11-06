# Review follow-up host validation

The production audit targets the BF16/NVFP4 autotuner's EP-group plumbing and fail-fast behavior. These durable local harnesses are outside the repository test suite; no test files or production code were edited by this validation work.

- `check_autotune_host.py`: **14 passed**. Executes actual AST-extracted autotuner/backend source with explicit fake CUDA graphs/events/process groups and real CPU Torch score tensors. Covers configured EP group forwarding, WORLD default, no-dist operation, six untimed replays, local event samples, MAX of per-rank medians, graph cleanup, capture/replay errors, and apply/launch/sample failures aborting without advancing to another candidate. Backend group lookup is skipped when distributed is uninitialized; tuning runs only once.
- `check_autotune_gloo.py`: **passed**. Four actual localhost Gloo processes create subgroup `[2,3]`. Ranks0/1 never enter the tuner and wait outside collectives until tuning completes. The subgroup runs actual extracted autotuner source with real readiness/score reductions and barriers; fake CUDA/kernel operations produce known per-rank samples. Both subgroup ranks select the expected winner, with18 graph replays and2 resets each. This also catches implicit WORLD collectives in the timing helper.
- JSON receipts include exact source SHA256 values. The real subgroup receipt verifies control collectives only; it does not test NVSHMEM bootstrap, NCCL, CUDA events, numerical correctness, GPU timing or distributed failure recovery. Candidate errors now propagate, but peers still depend on their launcher to abort a failed job.

Run from the source checkout with the existing CPU Torch environment:

```bash
../.venv-weight-layout/bin/python ../review-followup-20260917/check_autotune_host.py
../.venv-weight-layout/bin/python ../review-followup-20260917/check_autotune_gloo.py
```

The public runtime already resolves EP-group rank/size for NVSHMEM. Its preexisting UID broadcast uses global `src=0`, so subgroups excluding global0 can have a separate bootstrap problem. The local subgroup test deliberately tests the tuner in isolation and does not imply that common-runtime issue is fixed. Shared SM100 autotuners also retain their existing WORLD/recovery behavior; this PR follow-up is scoped to BF16/NVFP4.

## Published outcome

- Host fixes: `b4015a816f96738d197adf1ba42d691cb77ee2a1`; separate DeepGEMM test restoration: `45c1034b`.
- All touched production/docs files and the whole PR pass scoped pre-commit; `git diff --check` passes.
- `device-source-audit.json` verifies all maintained device/helper and staging-kernel files are byte-identical to measured1098, along with frontend launch/compiler/reducer and input-staging function ASTs. Only host validation, lifecycle and autotune control flow changed. No GPU rerun is claimed.
- `combine-output-validation.json`:8 metadata checks (both reduction-mode shapes, CPU/wrong-dtype/wrong-shape rejection) with actual validation AST and metadata doubles.
- The DeepGEMM-only test file is byte-identical to mergedupstreamf17; all six CuTe test files are unchanged by this cleanup.
- Five bot replies are preserved in `posted-reply-*.json`; the extra TMEM fence is explicitly declined with PTX documentation and existing ownership waits. No human-reviewer reply was posted.
- `PR_BODY.md`/`publication-readback.json` preserve final publication; the prior1–8192 performance table remains tied to1098, with no relabeled timings.
