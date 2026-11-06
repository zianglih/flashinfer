# W4A16 tracing sync to FlashInfer PR5019

Current local source: `74ba96d551640938edde68d628b36ba404a7f331`, parent `19e8aebb541684df09e12cc79610338aa429a2cf`. Published to the existing open PR; title and non-draft state are preserved. User authorization is limited to W4A16 implementation code; no scripts, new tests, documentation or protected vendored source are ported upstream. Neither PR is to be merged.

The four-file change adds 87 source push/pop sites. The shared decoder exposes two no-op tracing hooks; `_MegaMixedInput` overrides them with the existing public IKET export. This avoids loading the SM100 vendored `common`/`src` namespace into standalone shared W4A16. The four per-K sections are raw-weight TMA readiness, free decoded-weight TMEM slot, NVFP4 load/decode, and BF16 TMEM store/commit. No bulk transform implementation is copied. Raw-TMA/TMEM probes, x8 stores, scheduling and arithmetic retain the baseline computational AST.

- [Committed source audit](committed-audit.json): all four computational ASTs match the parent after narrowly removing validated instrumentation; all 87 marker payloads, control contexts and endpoints match HashInfer. Protected source and scripts/tests/docs are unchanged.
- [CPU/style validation](validation.json): four Python files parse; scoped pre-commit and whitespace checks pass.
- [GPU tests](test-audit.json): 15 logical cases / 36 rank reports pass with zero failures, errors or skips. Four shared-kernel cases exercise 1CTA/2CTA scale mapping and both finalize paths; four EP1 cases exercise config/runtime scales, routing and both return modes; seven EP4 cases exercise activation/normalization contracts and manual/automatic lockstep graph replay.
- [Exact setup](setup-c2.sh), [test commands](test-c2.sh), [per-rank JUnit wrapper](pytest-rank.py), complete logs/JUnit under [remote-validation](remote-validation/).
- [Allocation receipt](runtime-allocation.json): C2/infra `fi-w4a16-trace-0925`, node `hu-pdx-38`, eight B300 SXM6 AC, image `nvcr.io/nvidia/pytorch:26.05-py3` with recorded digest; devbox is retained. Tests used GPUs0-3 serially. [Installed versions](pip-freeze.txt) and [setup log](setup.log) retain the container PyTorch. Runtime reports NVSHMEM3.6.5; the installed NVSHMEM wheel is3.8.0.
- [External native smoke](SMOKE-IKET.md) and [launch script](run-smoke-c2.sh). These helpers remain outside the repository.

## Runtime observations and retries

1. EP4 rendezvous initially retried because the container hostname was absent from `/etc/hosts`. [Environment correction](hostname-setup.md) restored same-node resolution; the original test log retains the warnings. All test groups subsequently exited0.
2. First external smoke attempt failed before GPU work because torchrun abbreviated the helper's `--run` as its own `--run-path`. Added a `--` separator before the training script. Log retained in `remote-validation/validation/iket-smoke-argparse-failed-1`.
3. Second attempt reached fixture/reference setup but rejected the helper's unsupported public-config `opt_level` keyword before target construction. Removed that helper-only argument, retaining native compiler defaults. Log retained in `iket-smoke-config-failed-2`. No repository change.
4. Third attempt completed native tracker and profiler with exact finite BF16 outputs on all four ranks (4,096 elements/rank). Its small E16/T4-per-rank fixture left selected cluster0 idle on ranks0 and3; ranks1 and2 each showed16 transform warp ranges and64 instances of every per-K subsection. The strict all-rank work audit correctly rejected this as full smoke qualification. Its reports/logs are retained in `iket-smoke-idle-cluster-3`, and native artifacts remain on the devbox. The subsequent E256/T32 smoke passed with atomic scheduling and the full grid.

The HashInfer default128-global-token run uses the same devbox, serially after these initial FlashInfer tests/captures. Historical PR performance tables remain separate and are not relabeled as new-source measurements. No new performance, full-suite, Compute Sanitizer or older-CuTe-wheel qualification is claimed by this sync.


## Final result

Published74ba96d; [body readback receipt](published.json) and [final validation index](validation-final.json). Fresh E256/T32-per-rank/H1024/I1024/top8 EP4 native smoke completed with zero nonfinite or bit-mismatched values on all four ranks (32,768 elements/rank), one recorded target launch/rank,40 warp tracks and all16 transform warps. All four ordered transform subsections occur640/640/704/640 times for ranks0/1/2/3. [Native audit](remote-validation/validation/iket-smoke/audit.json), [complete test evidence](completed-test-section.md), [current PR body](PR-body.md). Current-head pre-commit/API/docs build pass; upstream GPU matrix remains unauthorized, and its summary reports failure for that gate. No upstream test failure was observed because the GPU matrix did not run. C2 tests and profiling succeeded independently. The devbox is retained.
