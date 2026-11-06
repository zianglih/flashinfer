# Independent FC1 A/SFA and B/SFB TMA pipelines

Task-local, unstaged experiment. Base `442d2aa53f68b4640c3ab5118a76f1599ff60d34`.
Local independent clone: `flashinfer-regular-tma-pipeline`; remote sibling:
`regular-tma-pipeline`. The production candidate and the regular-TMA control
are untouched. [Source manifest](manifest.json) records the three source files.

**Decision: reject the separate-pipeline delta.** N128 is slower at 8K in both
orders, and its 16K result changes sign. N256 is slower in both orders at both
token counts. See [all raw medians and validation](../../evidence/regular-tma-pipeline/RESULTS.md).
All 24 native rows are fingerprint-exact, with 100 timing samples preserved
per row. No further dtype timing or sanitizer is warranted for this variant.

The reference structure is documented in
[W4A16_PIPELINE_COMPARISON.md](../fc1_regular_tma_experiment/W4A16_PIPELINE_COMPARISON.md).
The regular-TMA preparation/kernel contracts are audited in
[INDEPENDENT_AUDIT.md](../fc1_regular_tma_experiment/INDEPENDENT_AUDIT.md).

## Change and ownership

For prepared FC1 N128/N256, retain A/SFA TMA on warp0 and move B/SFB TMA to
existing idle warp1. The B `PipelineTmaUmma` reuses inactive `ab_barriers`.
No extra warp, SMEM payload stage, TMEM column, output allocation, or data
conversion is introduced. CTA size remains288/160; stage counts and all
operand/epilogue layouts remain unchanged. FC2 and small-N SF cp.async retain
their paths. Both pipelines use the existing CTA-group completion protocol.

Expected transaction bytes partition the original total:

```text
A = G * channel_tiles * (128 * tileK * weight_bits/8 + sf_stage_bytes)
B = G * (b_rows * tileK * activation_bits/8 + sfb_stage_bytes)
```

Both full barriers must be ready before S2T/MMA. The leader releases both only
after both NB2 MMAs. Each producer advances and drains independently. PDL wait
and dependent-launch placement are unchanged; this isolates producer pacing
from any future weight/preparation overlap.

Independent source review checked group2 byte accounting, complete local SFB,
NB2 ownership, 160-thread inline epilogue, fallback bindings, and marker pairs.
Python AST parsing and `git diff --check` pass. The actual GPU compiler exposed
one additional state-lowering issue, described below.

## Compiler repair and exactness

The first actual-source smoke failed **before execution**, at CuTe IR dominance
verification. Its numerical reference compiled and ran. `producer_tail` mutates
the Python `PipelineState`; draining A in a warp0 branch left warp1's B tail
referring to SSA values defined inside that sibling branch. Cloning A's tail
state fixed compilation, matching the existing cp.async-tail pattern.

- Failed source SHA: `453e985b333cdf8b9447fd7f2e3af5fe4e39f423cd270e670b5907a0db515995`.
  All three files are retained under `snapshots/v1-shared-tail-state/`.
- Corrected source SHA: `5faf74ca89b38ef3277013d69dd358ee21590053f99d8a1252a69c2107906fb0`.
- GPU6 exactness: **20/20 paired cases passed**: two smoke cases, twelve NVFP4
  route/K/channel boundary cases, and six N16/32/64 controls. Per-token mode is
  exercised both ways. N16 includes a full-capacity physical-N32 read boundary.
- `probe_exact.py` calls the actual source-copy host, preparation, and kernel.
  Only the numerical reference uses the frozen442 host function and class;
  no implementation overlay or preprepared input replaces the tested path.
- The six-format matrix and sanitizer were not run; the native NV performance
  gate rejected the variant. Fused-finalize is excluded.

## Native comparison

Both arms use the same frozen grid16 preparation
`125d0f15910debc75ca1a128c6c59ad83db84558ef66fe338d362371955d4392` and host
`2a8a4a3ad8e927cc8bccc8adf3fc3668e9b7b581eb4eb9d35d1416e21abc2ce0`.
The regular core control is `9f53fd0a8a775f0091d3b718d944e0271708ae8022d9fac59ae7dba6425d1c0a`.
The direct-source harness is pinned to
`094ebfe2f2eec471e27edd0c936e6dcae5412973cbed322ae0273da95f0a5d26`.

Environment: replacement C1 `fi-w4a4-pipeline-1025`, B200 GPU6,
`nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.7.1. Every shell sources
`../recovery442/env_candidate.sh`; native candidate cache/source paths remain
unchanged. Control and pipeline use separate private CuTe cache directories.
Vendor symlinks resolve inside the project and match442's three gitlinks.

Fixed tactics:
`[128, [[512,128],[2,1],false], [[256,128],[2,1],false]]` and
`[256, [[256,256],[2,1],false], [[256,256],[2,1],false]]`.
Actual native DeepSeek routing, hidden7168, intermediate2048, top-k8,32local
experts; preparation is inside every full-chain invocation. Ten warmups,
100cold-L2 CUDA-graph CUPTI samples per row. Each arm runs in a fresh process;
the driver verifies complete native input/routing/final-output fingerprints.
These are adjacent fixed-tactic diagnostics, not primary AUTO retention data.

```bash
python3 scripts/regular_tma_pipeline_experiment/run_native_screen.py \
  --tag nv-n128-forward --variants control,pipeline,control --tokens 8192,16384
python3 scripts/regular_tma_pipeline_experiment/run_native_screen.py \
  --tag nv-n128-reverse --variants pipeline,control,pipeline --tokens 16384,8192
python3 scripts/regular_tma_pipeline_experiment/run_native_screen.py \
  --tag nv-n256-forward --variants control,pipeline,control --tokens 8192,16384 \
  --tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]'
python3 scripts/regular_tma_pipeline_experiment/run_native_screen.py \
  --tag nv-n256-reverse --variants pipeline,control,pipeline --tokens 16384,8192 \
  --tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]'
```

Raw100-sample JSONs, command receipts and logs are in
`../../evidence/regular-tma-pipeline/`. `finalize_evidence.py` rechecks source
manifests, all samples, cross-order native fingerprints, post-timing outputs,
and the 20 exact receipts, then generates `validation-receipt.json` and
`RESULTS.md`. GPU6 was released with no processes and 0 MiB used.

`provision_remote.py` is a historical receipt for the initial failed v1 core;
it is not the current source deployment command. It refuses to overwrite the
existing clone. The corrected source and pinned harness are frozen under
`snapshots/v2-tail-state-clone/`; the failed source remains under
`snapshots/v1-shared-tail-state/`.
