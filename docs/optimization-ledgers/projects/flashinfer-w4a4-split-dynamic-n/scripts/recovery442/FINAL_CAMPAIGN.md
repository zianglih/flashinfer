# Final442 campaign completion after recovery

Production SHA `442d2aa53f68b4640c3ab5118a76f1599ff60d34` is frozen. Reuse original B1 and the completed442 A1 unchanged. Complete A2 and B2 once each. No B1 launch path exists, and attempting A1 for442 is refused. Tokens1/2 remain measured and excluded from all retention aggregates.

The replacement devbox `fi-w4a4-pipeline-1025`, C1/ziangli, uses the same B200-83 host and all8 GPU UUIDs/indices/names/driver580.178.04 as original B1/A1. Image `nvcr.io/nvidia/pytorch:26.05-py3`, actual nvcc13.2.78, active CuTe4.7.1, CUPTI Python13.4.0 are unchanged. Both arm native modules were prewarmed separately without timings. Parent owns execution approval.

## Exact preserved inputs

`restore-manifest.json` enumerates each original B1/A1 JSON, log,13 AUTO-cache files, frozen helper and audit receipt with its original local/archive path, destination, SHA256 and byte count. `restore_campaign.py --send` accepts only absent or byte-identical destinations. It never overwrites differing files or restores old executable caches.

NV B1 JSON SHA256 `c3d181bca280b85b89afa3c8f7ee9763103b220b629f6fa34d9793ec45c5958f`; MXFP8 B1 `78b71daa375b332b8dad839a29cfe66c605e8066fab7755d68595a775df692e4`; mixed B1 `1f1b19b45c2a3e109b90894d142de4f1db0b96eedf5cc202a86a6f3274fb355b`. A1 hashes are pinned in the restore manifest from `evidence/combined-screen-442d2aa5/raw/results`.

Frozen `scripts/run_split_benchmark.py` and the full original `results/unfused-baseline-epoch-v2-tools` set are unchanged. MXFP8/mixed source overlays use old gated-group64 versus new16. Runtime uses normal native AUTO, unfused finalization for every mode, per-tensor NVFP4,10 warmups/100 cold-L2 CUDA-graph CUPTI samples, all13 tokens. No saved AUTO cache is loaded. GPU0 runs NVFP4; GPU1 runs MXFP8 then mixed sequentially. Each arm completes all modes before the next arm starts.

## Recovery environment boundary

Only three recorded environment values may differ:

- `CUTE_DSL_CACHE_DIR`: `/root/.cache/flashinfer/cute_dsl` → exact private arm cache path below.
- `FLASHINFER_WORKSPACE_BASE`: previously unset → `/workspace/flashinfer-w4a4-split-dynamic-n/cache/candidate-442` or `.../cache/baseline-a65`.
- `FLASHINFER_CUDA_ARCH_LIST`: previously unset → `10.0a`.

All other recorded runtime keys must match byte for byte. No compiler override (`CC`, `CXX`, `CUDACXX`, `CUDAHOSTCXX`, compiler flags) is allowed. Native source and header trees, source-generator files, packages, actual nvcc and every emitted ninja flag/rule are verified. `native-build-equivalence.json` proves original visible B200 detection and explicit10.0a produce identical SM100a flags through unchanged pinned source. Both recovered arm ninja rules match after named path substitutions. Original build.ninja/cubins were not archived; this establishes target/toolchain/source equivalence, not original cubin byte identity. New private caches were rebuilt; original B1/A1 results retain their original environment unchanged.

The only preparation-contract exception remains the already authorized measured `blackwell/moe_finalize.py`; every other original preparation/routing/quantization AST invariant remains enforced. Current validation:56 capability/tactic/architecture checks,72 composed phase cases and15 native exact configurations. Broad numerical and sanitizer checks remain deferred.

## Reviewed execution commands

Run these from the remote project root after restoring the bundle and reviewing CPU policy results. `prepare` performs CPU/source/environment checks and no kernel benchmark. Explicit selectors make B1 reruns impossible.

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
.venv/bin/python scripts/recovery442/final_campaign.py prepare \
  --validation-scope '56 capability/tactic/architecture checks;72 composed phase cases and15 native exact configurations; broad numerical/sanitizer deferred'

# Parent-authorized timings only. Do not repeat an attempted arm.
.venv/bin/python scripts/recovery442/final_campaign.py run-arm --arm A2 \
  > logs/final-442-A2-driver.log 2>&1
.venv/bin/python scripts/recovery442/final_campaign.py run-arm --arm B2 \
  > logs/final-442-B2-driver.log 2>&1
.venv/bin/python scripts/recovery442/final_campaign.py verify
```

The runner sets the correct arm environment itself; sourcing candidate env before B2 does not select its cache. Output lives in `results/final-442-recovery`, with exclusive-create command receipts, per-mode raw JSON/log/cache evidence and completed-arm receipts. A failure preserves all partial evidence and prevents automatic rerun/continuation. For any changed candidateSHA use a fresh directory and fresh A1; never relabel442 A1.

Final verification covers156 token rows and156 cache hashes, source maps within each arm, exact routing histograms, timing/helper contracts, and B1→A1→A2→B2 chronology. Per-token paired speedup is `sqrt(B1*B2/(A1*A2))`; report raw medians and B2/B1 plus A2/A1 drift. Decode aggregation uses4..512; prefill4096/8192/16384; overall all tokens except1/2. Final retention decisions remain parent-owned.
