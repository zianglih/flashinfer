# TP small-GEMM optimization round

Initial base: `1054743780dda2919c1424124c1e3258248b8c19`. Current retained head: `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8` (PR7290).

All source experiments in this round are closed; no active review clone remains. Retained changes are singleton-cluster rank normalization, scale-row/shared-quantization simplification, and the static launch-capacity bound. See [grid retention and cleanup](static-grid/composed/RETENTION.md) and the source-bound ledgers below. Final full-table refresh is a separate campaign in `retained-refresh/`.

During the round, experiments used isolated unstaged review clones. Common remote source has348 verified Python/benchmark source hashes; each variant uses a private compilation workspace and CWD, while native C++ caches remain on cluster persistent storage. No sanitizer is run, as requested. Existing external baselines and frozen autotune winners/routes are reused.

- `finalizer/` (rejected): extend the existing bounded exact-divisor prefill geometry to routed output. One-line removal of the expanded-layout gate; no new tuning axis, dtype/model branch, arithmetic or alignment change. Historical attribution was corrected: scaled public calls already use the exact-divisor policy, even with compact output; the actual affected cases were W4A16. See `finalizer/ATTRIBUTION-CORRECTION.md`. Source-paired exact/codegen gate precedes fixed-winner CAAC timing.
- `scheduler/` (rejected): publish route in the existing unused fourth CLC metadata word to remove repeated ticket division. Preserve ordinary scheduling, synchronization and queue depth.
- `producers/` (retained): compile-time normalize cluster rank to remove rank-derived work for the existing one-CTA launch. Verify two-CTA identity and resource/codegen evidence.
- `epilogue/` (rejected): derive compact tail row addresses directly; avoid preloading/shuffling mapping that is affine. Preserve expanded layout and shared/TMEM lifetimes.

Initial lane allocation was primary C3 GPUs0 finalizer gate,1–2scheduler,3–4producers,5–6epilogue, with the secondary box for controlled timing. These experiment lanes have been released. Both are8×B300 with `nvcr.io/nvidia/pytorch:26.05-py3`,CUDA13.2,CuTe4.8; capacity was verified before launch.

Performance retention uses the existing public functional benchmark, unfused swap-AB,10warmups/100CUPTI cold-L2 graph samples, sameGPU C–A–A–C, fixed winners and routing. Source gates are not performance evidence. Model/topology controls are V3 EP8/TP8,V41F EP4/TP4,K3 EP8/TP8,N3U EP8/TP8. Unsupported comparator cells remain excluded. Tokens1/2remain outside retention/display.

- `static-grid/composed/` (retained): safe launch-time capacity cap, unchanged device code. Four affected V3 TP8 T4 FC1 grids shrink148→128 CTAs; CAAC geometric mean+0.096%, per-token−0.236%. Eleven unchanged controls−0.012%; retained as neutral removal of guaranteed-empty launch work, without a broad latency claim.
