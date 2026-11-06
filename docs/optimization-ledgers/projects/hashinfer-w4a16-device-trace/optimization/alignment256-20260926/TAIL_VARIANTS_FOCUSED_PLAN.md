# Fresh focused tail and score comparison

Prepared after parent confirmed both new fixed diagnostics passed reference checks with REG96,STACK0,LOCAL0. This experiment is an independent comparison of three candidates against the original retained baseline; it is not a cumulative retained stack.

| Arm | Source label | Commit | Payload / score load intent |
|---|---|---|---|
|A|before|cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7|Original128-bit payload and scores|
|B|late-no-prefetch-candidate|679aa752f9292d5cbfe4f129c076e347089b58f2|256-bit payload, late state with no cross-worker score prefetch|
|C|late-participant96-candidate|f8c97bb6eb9026ec6af87c825a5bd99c157a1d52|256-bit payload, late state,96 registers for reduction participants|
|D|score-only-candidate|adadbd6b63fa43c4e5a305ccc08fa1f103ee15f6|Original128-bit payload,256-bit score load|

Exact Python-package digests and remote paths are in `tail-variants-focused-sources.json`; the runner independently checks all current source bytes and fixtures before/after each sweep. Campaign and run receipts retain actual source labels plus full source identities.

Order: **A1/B1/C1/D1/D2/C2/B2/A2**. Workload: uniform H6144/I2048/E256/top8, EP4, global T128/4096/8192/16384. Each sweep uses a separate process and empty caches, all8 native AUTO candidates,3 warmups and100 untrimmed cold-L2 CUDA-graph CUPTI per-iteration rank-MAX samples. Every A/candidate comparison pools only that arm's own two sweeps:200 samples per source/shape. The three projections retain actual phase names. No earlier A1, failed/cancelled wide run, previous focused128 run, or fixed-probe sample is reused.

The frozen `alignment_benchmark.py` remains unchanged at SHA256 `3cc8d7670664e07113a0df7bc99a19ee980379883507e322bb91414f269970f9`. The new runner and auditor adapt the proven original128 helpers; all timing and nativeAUTO machinery remains in the frozen worker.

Expected completed evidence:8 trials,32 cold rows,3200 cold rank-MAX samples,10240 hot rank samples,128 winner exports,32 independent T128 rank-reference records,128 finite/repeat output records. Reference checks remain at T128; larger shapes have finite/repeated/cross-arm bitwise output hashes. Native EP4/EP8 broad qualification and full-catalog spill coverage remain separate requirements before retention.

## Readiness

`tail-variants-focused-cpu-plan-v2.json` passes exact source identity checks. `tail-variants-focused-cpu-checks-v1.json` passes CPU-only imports, trial order, token matrix, comparison pools, identical eight-candidate catalog, current source identities and frozen worker hash. Independent peer review found no blocker in source binding, fresh phase directories, comparison aliases, serial receipt ordering, loopback torchrun or prior-evidence exclusion. No GPU run was launched by the preparation agent.

| Artifact | SHA256 |
|---|---|
|run_tail_variants_focused.py|2fb1fcb0372ad858a6c503cddb699883c9718756554aa1fb0d3ae687aa62f3ac|
|audit_tail_variants_focused.py|e0ebdd4637904cafed49e16255d2d795cd312abe585d7e5d5a0df4449a3f1187|
|tail-variants-focused-sources.json|dacf0b7752e12c0b298822ac740bb43a495bcf1e7093f05bb8a6857d8934defc|

## Parent-controlled remote command

Copy those three files beside the existing worker/helpers. The manifest already uses the verified remote checkouts. The runner's own GPU-idle guard runs immediately before each sweep.

```bash
/workspace/hashinfer-alignment256-20260926/venv/bin/python -B \
  /workspace/hashinfer-alignment256-20260926/optimization/alignment256-20260926/run_tail_variants_focused.py \
  --output /data/ziangli/hashinfer-w4a16-device-trace/alignment256-20260926/tail-variants-focused-v1 \
  --run
```

Omit `--run` for a source-bound CPU plan. `--max-trials N` stops between completed sweeps and leaves the campaign incomplete. A later `--run --resume` verifies all prior completed source/helper/receipt bindings before continuing the exact original order. Do not mutate any source or measurement helper after the campaign is created.

After all eight sweeps complete, audit locally after copying immediate evidence, using the local source override:

```bash
python3 -B audit_tail_variants_focused.py \
  --campaign tail-variants-focused-v1 \
  --source-root "$PWD" \
  --output-prefix tail-variants-focused-audit-v1
```

Expected wall time is roughly34 minutes from prior four-shape sweep durations; this is an estimate, not a deadline.
