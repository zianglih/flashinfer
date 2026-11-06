# Actual-source regular-TMA diagnostic

The original `candidate` remains clean442. The sibling `regular-tma` contains exactly the three unstaged implementation files pinned by `review_snapshots/grid16/manifest.json`; this first actual-source snapshot uses prep grid16, not the grid4 runtime-overlay gate. Native sources/includes resolve through `regular-tma/flashinfer/data` to original candidate paths, preserving the already-built native cache. CuTe compilation uses a separate experiment cache. Neither measurement path replaces kernel or internal host implementations.

The harness forces one explicit existing tactic and records that this is a diagnostic, not native AUTO/primary retention evidence. It hashes every defined MoE input/weight and routing tensor plus complete final output; all hash work is outside timing. Transparent observers are disabled and their scratch references released before graph capture. Scratch remains invocation-local, matching the W4A16 policy at `blackwell/moe_w4a16.py:59–93`: sort, permutation, FC1, FC2, combine all execute on each invocation and propagate PDL. W4A16 also reuses its BF16 hidden workspace for FC2 after FC1; this packed-input experiment needs separate scratch because the type/size differ.

Example preparation-grid phase diagnostic (device agent owns callback and GPU4):

```sh
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
export CUTE_DSL_CACHE_DIR=/workspace/flashinfer-w4a4-split-dynamic-n/cache/regular-tma-source/cute_dsl
CUDA_VISIBLE_DEVICES=4 .venv/bin/python scripts/fc1_regular_tma_experiment/probe_native_source.py \
  --repo regular-tma --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 \
  --arm regular --manifest scripts/fc1_regular_tma_experiment/review_snapshots/grid16/manifest.json \
  --tokens 8192,16384 --tactic '[128,[[512,128],[2,1],false],[[256,128],[2,1],false]]' \
  --prep-callback scripts/fc1_regular_tma_experiment/grid_screen.py --phase-only \
  --output scripts/fc1_regular_tma_experiment/results/source-grid16-phase-r1.json
```

No full-chain timing is performed with `--phase-only`. For a later fixed-tactic full-chain screen, omit callback/phase flags and execute separate baseline/regular processes in complete adjacent ABBA and BAAB orders, with unique output paths. Baseline uses `--repo candidate --arm baseline` and omits `--manifest`; regular uses its exact current source manifest. Do not resync source while an arm is compiling or running. Compare all input/routing/final hashes across arms before interpreting medians. Record all100 samples per arm and memory peaks. `--exact-only` performs the same hash capture and repeatability checks without timings.

MXFP8/mixed helpers run their own runner, so their tensor list is captured explicitly at `BenchmarkSplitMxfp8::<mode>` rather than assuming `CuteDslMoEWrapper.run`. Supply the pinned existing assembly directory using `--assembly-dir`; all helper Python hashes are recorded. Broad modes follow only if the initial NVFP4 full-chain gate warrants them.

## Completed N128 source-copy screen

All16arms and1600samples verified in `evidence/regular-tma-source-grid16-442/raw.tar.gz`, SHA256 `1f5509c3278161e6e9931d55c637822aec3e17b0a8c699e6a8fa9189e66fe664`. Each arm has identical deterministic input/weight/routing/final fingerprints. Four controls and four regular arms per token count:

| Tokens | Baseline µs | Regular TMA µs | Geometric-mean B/A |
|---:|---|---|---:|
|8192|299.777,299.713,299.809,299.601|302.657,303.1045,302.5445,302.7845|0.98993448|
|16384|521.9695,521.2495,521.986,521.442|508.7695,508.4335,509.282,508.386|1.02544442|

Memory receipts show identical peak allocated storage (30.850GiB8K,32.053GiB16K), regular reserved increases of0.262GiB/0.508GiB, and zero post-timing allocated delta in allarms. This establishes bounded actual graph allocation behavior for the measured8K/16K cases; it is not a general concurrency guarantee. The earlier interrupted GPU4 campaign is preserved separately and excluded from this comparison.
