# Preparation PDL half-grid — rejected

Frozen source: `0b7fe90151340d4fca6a5ec41a91019dde743819` plus the single `moe_prepare.py` hardware-thread-budget change, local source-only patch `4885591cfacff2ec2cb8f6469b9eb77749a28bbf218110151a4618f9f4f15b72`. Candidate and control use the same frozen Nemo benchmark overlay `cf5cd581...`; complete deployed identities are in `deployment.json`, `config-v2.json` and `evidence/sources/`.

The candidate divides the preparation resident block budget by two when PDL is enabled. It leaves payload/SF layouts, mapping, quantization, launch dependencies, GEMM kernels and selected tactics unchanged. Measured scaled preparation grids were 2,368 blocks in control and 1,184 in candidate for all four cells.

Validation: 36 exact graph byte checks cover BF16, 16-byte-aligned views, FP4 SF16/SF32 and FP8 SF32, PDL on/off, empty/partial/full routes. The completed gate was reused after a helper-only single-format assertion fix. The original failed observer attempt remains in `evidence/prepare-pdl-screen/` (100 samples, no completed result row); none of its samples enters the final analysis.

Performance uses fixed source-native functional-API winners, unchanged routes and quantization, unfused finalize, C–A–A–C ordering, ten warmups and 100 cold-L2 CUPTI graph samples per pass. NVFP4 includes input quantization; MXFP8 uses prequantized input. `summary.json` and `raw-samples.csv` cover 4 cells / 1,600 measured samples; all 86 collected artifact hashes, 80 cache hits and 32 actual GEMM dispatches validate. `results.md` contains the complete table.

Decision: reject the universal half-grid policy. The four-cell geometric mean is 0.997090×; V3 NV128 improves 0.78%, but V3 NV16K loses 0.42%, V3 MXFP8 16K is neutral (+0.12%), and Nemo NV16K loses 1.62%. All candidate repeats differ by at most 0.12%; Nemo's control drift is +0.79%, with both candidate passes slower than both controls. These results do not justify retaining the additional policy. This does not disprove PDL overlap generally; no trace of candidate overlap was collected, so no causal overlap claim is made.

No rerun or AUTO expansion is requested. Helpers, raw results and persistent native/DSL caches are retained. `cleanup.json` records verified removal of the completed local and remote candidate source copies only.
