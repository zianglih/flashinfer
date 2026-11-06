# Completed N32 qualification evidence

- Upstream FlashInfer `866c80d0c70a90624b4c2056d12d1543d709609e`: 17 logical exact cases / 52 rank passes / 0 skips. EP2 has eight N32 cases on each rank; EP4 has nine epilogue cases on each rank.
- HashInfer `f088518a8b0f24018bfd49420457eb9f873fcfaa`: the same 17 logical exact cases / 52 rank passes / 0 skips.
- HashInfer sanitizer v2: six logical cases / 48 clean rank reports / 0 skips. All eight N32 tactics ran all nine workload rounds on each rank. Full source maps, package origins, runtime versions, receipts, and JUnit identities passed local validation. The HashInfer source map is exactly 110 files before and after sanitizer execution.
- All reports are from the retained source; rejected GLM5 optimization candidates were not applied. Old sanitizer v1's source-guard failure remains archived separately and contributes no case to v2's result.

## Runtime and tool

- Image: `nvcr.io/nvidia/pytorch:26.05-py3`; 8 B300 GPUs, EP8 sanitizer.
- Python 3.12.3; pytest 8.4.2; Torch package `2.12.0a0+5aff3928d8.nv26.5.50603568`; CUDA 13.2; CuTe DSL 4.7.1; CUDA Python/bindings/CUPTI Python 13.2.0; NVSHMEM 3.6.5.
- Compute Sanitizer `2026.3.0.0 (build 38637409)`; binary SHA256 `f23878d03e4a25b8cfd8c3e6e13220d6db8c06684c0e65d02ab074ad1fa32d1f`.
- The kernel filter targets `Sm100W4A16MegaMoEKernel`, including its deterministic combine. It does not claim coverage of unrelated setup/library kernels.
- Memcheck uses `--check-tensor-ops=no` for the documented 2026.3 tensor-checker issue with legal 2CTA peer-barrier TMA; compiler `-g-tmem-access-check` remains enabled. No diagnostic suppression file or pattern is used. Synccheck makes missing barrier initialization fatal. Racecheck retains info-level findings, async memcpy checking, and all reports.

## Coverage

- Tactics: M128/M256 × N32 × K256; group512/1024; `epi_warps`/`reuse_dispatch_warps`; C2; one-CTA MMA for M128 and two-CTA MMA for M256; fused FC2 reduce disabled.
- Workloads: exact expert-count boundaries 15/16/17/31/32/33, an empty source rank, all ranks empty, and refill. All rounds reuse one allocation with capacity33 per rank. Both FC1 and FC2 routing-weight placements are tested.

## Raw sanitizer pytest summaries

```text
test_w4a16_megamoe_sanitizer[topk_fc1-memcheck-n32-ep8-O3]
================= 1 passed, 17 deselected in 329.08s (0:05:29) =================
test_w4a16_megamoe_sanitizer[topk_fc2-memcheck-n32-ep8-O3]
================= 1 passed, 17 deselected in 345.22s (0:05:45) =================
test_w4a16_megamoe_sanitizer[topk_fc1-racecheck-n32-ep8-O3]
================ 1 passed, 17 deselected in 1182.21s (0:19:42) =================
test_w4a16_megamoe_sanitizer[topk_fc2-racecheck-n32-ep8-O3]
================ 1 passed, 17 deselected in 1275.99s (0:21:15) =================
test_w4a16_megamoe_sanitizer[topk_fc1-synccheck-n32-ep8-O3]
================= 1 passed, 17 deselected in 139.22s (0:02:19) =================
test_w4a16_megamoe_sanitizer[topk_fc2-synccheck-n32-ep8-O3]
================= 1 passed, 17 deselected in 154.51s (0:02:34) =================
```

Each of the 32 memcheck/synccheck rank logs contains only `COMPUTE-SANITIZER` and `ERROR SUMMARY: 0 errors`. Each of the 16 racecheck logs contains only `COMPUTE-SANITIZER` and `RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)`.

## Captures and validation

- `correctness/n32-retained-sequence-v1/flashinfer-exact/`
- `correctness/n32-retained-sequence-v1/hashinfer-exact/`
- `correctness/n32-retained-sanitizer-v2/`
- `evidence/n32-qualification-progress/flashinfer-exact-validated-v1.json`
- `evidence/n32-qualification-progress/hashinfer-exact-validated-v1.json`
- `evidence/n32-qualification-progress/hashinfer-sanitizer-v2-validated.json` (SHA256 `7d3c8d01ab6c374eb5b4d98ecd8a142569f16438ed821e2053beb43390a45ab6`)
- Full v2 download: `evidence/n32-qualification-progress/n32-retained-sanitizer-v2-hashinfer-sanitizer-20261009T155101Z.tar.gz` (SHA256 `db4b2cbb752a4ff0a91b1e8bf63fb9f0940e31c0736dc7734cd111231c540a56`). Absolute pytest convenience symlinks are preserved as literal metadata in the adjacent `.links.json`; they are not followed during local extraction.

Independent second-parser audit also passed: `evidence/n32-sanitizer-v2-independent-complete-v1.json` (SHA256 `830c16d5252f7bdc1eaf6b8c9d9aa64ec5accaac26bf6e5b869bc2a33fa3d38a`). It additionally verified all 366 archived regular files byte-for-byte and the final GPU-idle receipt.

The collector exited successfully after the final download and relinquished monitoring ownership. No devbox removal or runtime changes were performed.
