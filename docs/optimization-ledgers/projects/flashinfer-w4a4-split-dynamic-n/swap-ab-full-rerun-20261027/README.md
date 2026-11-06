# Fresh swap-AB benchmark rerun

This campaign compares PR head `e2728a290` on C3 B300 GPUs with current non-swap CuTe DSL and TRTLLM implementations. W4A16 alone uses pre-PR `002529e17b22567a071091053c6c4dc2a55e050e` as its control. The clean PR source is production-identical to `5ac452450f65c6cec179290a66503ae86143a13f`; the external prepare work in progress is excluded.

Eight independent GPU groups cover V3 EP8, V4.1-Flash EP4, Kimi K3 EP8, and Nemotron3-Ultra EP8, each with NVFP4 and MX families. Each source/mode arm runs native AUTO using an empty selection cache, then frozen C-A-A-C passes. CUDA 13.2, Torch 2.12.0a0+5aff3928d8.nv26.05, CuTe DSL 4.8.0, and private CUPTI Python 13.4.0 are common across all fresh arms. Native C++ and JIT file caches persist on cluster storage; direct CuTe compilation memoization remains process-local.

The public benchmark uses 10 warmups and 100 cold-L2 CUPTI CUDA-graph samples per median. Both event fallback functions are forbidden during reported measurements. Every measurement must observe a matching functional CuTe DSL or TRTLLM operation with a native winner; frozen measurements verify the saved runner and tactic and cannot change the selection cache. NV includes the input activation quantizer; MX inputs are prequantized. Current swap-AB is unfused; legacy MX uses its supported fused path. Legacy K3 MX and unsupported TRTLLM SiTU cases remain N/A. Tokens 1 and 2 are measured but excluded from the summary and retention decisions.

Remote root: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/swap-ab-full-rerun-20261027`.

- `tools/`: observer and group orchestration; no source implementation patches.
- `make_launch.py`: build the deployment launcher with exact helper contents.
- `observer-pilot`: remote one-token AUTO/frozen preflight for the observer contract.
- `progress_remote.py`: compact group status.
- `fetch_evidence.py`: download logs, receipts, selection caches, and all raw timing samples.
- `assemble_results.py`: validate provenance and produce the final tables and raw output.

Attempt 1 was stopped to strengthen TRTLLM winner verification and include the autotuner and timer source in the manifest. Attempt 2 stopped at the new assertion because functional CuTe DSL operations use `CuteDslFusedMoE::`, not the wrapper prefix. Attempt 3 exposed a recorder serialization issue with TRTLLM's TVM FFI tactic arrays; the observer now uses the autotuner's native serializer. None supplies final timing data. The final attempt passed AUTO and frozen pilots for every arm family before the full restart; production code and benchmark policy were unchanged.

## Publication and audit

The interim PR body uses 44 summary rows and labels `V3 EP8`, `V41F EP4`, `K3 EP8`, and `N3U EP8`. It is archived in `../swap-ab-exact-20261027/pr-compact-models.md`. `build_pr_body.py` replaces historical evidence only after the complete fresh campaign passes the assembler's checks. The baseline comparison is `100 * (baseline_ms / current_ms - 1)` using geometric means of paired pass medians.

Independent source audit verified identical old/current model configurations, seeded input generation, routing, activation selection, histogram collection, autotune context, and timing boundaries. Weight quantization arithmetic/dtypes/scales are unchanged; W4A16's gate/up layout and implementation are the intended differences. All 6,551 production/benchmark files in the clean current source match the prior validated production source. The devbox image is `nvcr.io/nvidia/pytorch:26.05-py3`.

The final evidence contains native A2 CSV output because explicit `--backends` makes the benchmark print CSV. It preserves every printed latency and TFLOPS value; all frozen-pass raw medians are included separately. No ASCII tables are reconstructed. No sanitizer GPU run is authorized in this campaign.

Completed and published to PR #7290 on 2026-10-27 at 18:22 Pacific. All eight groups and 69 phases passed: 676 AUTO medians (67,600 samples) and 1,352 frozen medians (135,200 samples). The strict assembler verified source/configuration/helper hashes, routes, native tactic cache hits, CUPTI-only samples, and printed CSV values. An independent audit recomputed all 352 visible numeric cells directly from phase results. The final 44-row table and eight raw output blocks replace historical evidence; live readback matches `pr-body-fresh.md`. See `publication.json`, `evidence-final-verification.json`, and `assembled/provenance.json`.

Remaining prefill gaps are retained in the published table, including V3 MXFP4x8 at 16K (-14.41%), N3U W4A4 at 16K (-12.83%), and V41F W4A4 at 16K (-8.37%) versus non-swap. These results do not imply all performance gaps are closed. No production changes were made during this campaign; the separate review checkout's prepare WIP was excluded and preserved.
