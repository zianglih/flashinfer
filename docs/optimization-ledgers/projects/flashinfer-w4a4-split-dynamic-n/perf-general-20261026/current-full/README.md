# Full public table campaign at 0def601d

This campaign measures the clean retained source after the NVFP4 arithmetic port. It is a fresh same-sweep comparison against matching TRTLLM backends, not a before/after experiment. Results are local pending the optimization retention decision; this helper does not publish or edit the PR body.

- Source: `0def601d6603df828ea39679b41ccbce64f7f09e`, clean control checkout.
- Host: c3 / infra devbox `fi-moe-nvfp4-port-1026`, B300, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1.
- Models: V3 EP8 on GPU4; V41-Flash EP4 on GPU5; Kimi-K3 EP8 on GPU6. Each model runs NVFP4 then MXFP sequentially on its assigned GPU.
- Tokens: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384. Tokens 1 and 2 are present in raw tables and excluded from summaries.
- Public native AUTO, default backend lists, no CUTLASS, no fused CuTe finalize, 10 warmup / 100 cold-L2 CUPTI CUDA-graph iterations. NVFP4 includes initial activation quantization; MXFP input is prequantized.
- Unsupported K3 TRTLLM arms remain N/A. All comparisons use matching dtype / per-token formats and full-precision medians.

`raw/launch.json` contains the exact three helper invocations; each completed `raw/<model>/receipt.json` contains the exact public benchmark commands and scoped environment. `raw/preflight.json` records source hashes, helper hashes, GPU idleness and runtime. Every source receipt must match before and after measurement.

Run `python3 collect.py` from this directory to fetch bounded campaign artifacts from the assigned remote directory. After all three model receipts are complete, run `python3 summarize.py` to validate native medians, printed table cells, quantizer contracts, routes, source hashes and saved AUTO tactics. It produces `validation.json`, `summary.json`, `summary.md` and six complete `raw-tables.md` output blocks. No compiler cache is downloaded or cleared.

Remote campaign: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/screens/current-0def-full`.

Validation reuses the existing task-local `audit-rebased-20261026/benchmark-summary-parser.py` reader with only its input directory expression adapted. The historical PR renderer is never called.

Completed: all six tables, 78 token rows and 208 printed ratio cells validated against native full-precision medians. All three source-after receipts match, and NVFP4/MXFP routing identities and histograms match for every model. `summary.md` / `summary.json` supersede the earlier `provisional-nv.json` snapshot. `raw-tables.md` contains the complete six public outputs. The result remains local and unpublished.
