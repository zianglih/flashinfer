# FC2 canonical SFB TMA experiment

The candidate selected for integration replaces fragmented activation-scale copies with direct TMA for statically aligned FC2 N128/N256 tiles, and removes the now-empty cp.async/peer-relay pipeline. It preserves activation payload loading, MMA order, accumulator ownership, SF layouts, stage counts, shared allocation, epilogue, and public APIs. FC1 and small-N FC2 retain the old paths. No production edits were made by this diagnostic; the parent applies `integration.patch` after review.

## Address and lifetime contract

The existing canonical SF buffer consists of 512-byte blocks:128 rows ×4 scales. A128-row Kstage is contiguous, but its source rowblock stride is paddedK×128/SFvec. The descriptor uses an Int16 byte-preserving view `(256,Kblocks,row128blocks)`, strides `(1,256,256*Kblocks)`, and tile `(256,tileK/(4*SFvec),1)`. Int16 avoids the 256-element TMA box limit. Both CTAs load the same full-N SF rows locally; no CTA-rank offset belongs in the source. No preprocessing or GMEM payload intermediate is introduced.

K-block and row-block dimensions remain distinct so short-K OOB zero fill cannot cross into the next row block. `Int32(sf_k_blocks)` retains the K descriptor axis when both its source extent and tile extent equal one. It wraps the existing constexpr K-derived value as constant SSA; it adds no runtime launch parameter or cache axis and does not make the GEMM loop bound dynamic.

The no-cast control passes the first 12 FP4 cases, then fails with `cudaErrorIllegalInstruction` at case 13: MXFP8 E4M3/SF32, K128, M256/N128, 2CTA, per-token off. Here Kblocks=1 and tileKblocks=1, unlike the wider FP4 tile. The failure is consistent with static unit-axis removal and a descriptor rank incompatible with the explicit 3D instruction. CUTLASS's C++ analogue removes static unit tile modes (`copy_traits_sm90_tma.hpp:695`) and re-adds source axes only when their extent is not static one (`815–831`). Python CuTe converts Integer shape leaves through SSA (`core.py:166–180`); Numeric values are dynamic layout types (`1597–1605`) while `Int32(constexpr)` materializes constant SSA (`base_dsl/typing.py:950–962`). The exact DSL lowering is opaque, so the GPU control is the decisive evidence. The failing process exited and later retained-cast probes use fresh CUDA contexts.

These source references are retained under `/Users/ziangli/playground/projects/flashinfer-w4a16/flashinfer/3rdparty/cutlass/`, with Python files under `python/CuTeDSL/cutlass/` and the C++ file under `include/cute/atom/`. No-Kcast was rejected; the final patch retains the cast and documents why.

Warp 0 in each CTA issues A/SFA/B/SFB with one `a_pipe` barrier, whose transaction count includes `cta_group_size*sfb_stage_bytes`. The group2 inline TMA clears the peer bit in the completion mbarrier, as existing Gather4/CUTLASS do. Leader MMA waits on that barrier before S2T, then releases it after the last MMA using the stage. This removes only redundant AB/relay waits, arrivals, commits and tails. Unused barrier storage remains allocated, preserving shared layout and epilogue buffering. All producer threads still reach final TMEM deallocation collectives.

TMA reads arbitrary SF bytes in allocated invalid-token rows; these can include NaN encodings. FC2 columns are independent and all metadata/output accesses guard live tokens, with no cross-token reduction. Tests poison those rows and retain output canaries. Short-K zero-fill remains required.

## Evidence and methods

Frozen prototype base 13ca1475d96839f3bf3c46699cc63204b4d3b409. Review patch base 1904964d09db7f9a56d370d510ed03a0222e15c9 adds the existing static shape/cache/rounding and optional iKET markers. Private integration smoke uses the 1904964 host call signature without changing the remote checkout or shared native-JIT epoch.

B200, 148 SM, devbox fi-w4a4-dyn-n-1024, c1, GPUs0/6, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe DSL4.7.1. Actual native top-k 8 routing,32 local experts, hidden 7168/intermediate 2048. Phase and full-chain timings use 10 warm + 100 cold-L2 CUDA graph/CUPTI samples; all raw samples are saved. Fixed N128 uses logical M512 FC1 and M256 FC2; fixed N256 uses M256 for both. No primary benchmark or baseline rerun.

| Diagnostic | Ordered variants | FC2 medians us | Full-chain medians us |
|---|---|---|---|
|NV16K N128 GPU6|base,TMA+emptybarriers,base|159.824,159.776,163.760|556.385,559.056,559.329|
|NV16K N128 GPU6|base,TMA-only,TMA+emptybarriers,base|159.936,150.800,160.096,161.200|561.184,551.041,557.360,557.377|
|NV16K N128 reverseGPU6|TMA-only,base,TMA-only|151.072,160.352,154.240|549.313,560.944,549.041|
|NV8K N128 reverseGPU6|TMA-only,base,TMA-only|91.647,102.080,91.712|315.873,322.624,316.224|
|NV16K N256 GPU0|base,TMA-only,base|136.224,133.423,138.607|576.846,581.006,577.391|
|NV16K N256 reverseGPU6|TMA-only,base,TMA-only|132.576,137.041,135.344|569.841,573.489,574.625|
|NV16K N256 phase-attributionGPU6|base,TMA-only,base|135.168,132.369,134.432|573.425,569.858,572.993|
|MXFP8 16K N128 GPU0|base,TMA-only,base|268.959,248.064,270.512|902.798,850.478,890.254|
|MXFP4×MXFP8 16K N128 GPU0|base,TMA-only,base|251.136,228.672,259.744|816.478,788.846,827.550|

N128 repeats support a meaningful gain. N256 gives a smaller consistent phase gain and a near-neutral/small full-chain gain with drift; do not attribute individual full-chain changes to SF caching. In the N256 attribution run, FC1 was334.033/326.113/325.856us across base/TMA-only/base, so there is no consistent FC1 regression from the descriptor change. Full output and individual FC2 outputs are bitwise equal for every native variant.

## NCU mechanism

Matched GPU6 native NV16K N128 current versus TMA-only (full metric set,40 replay passes):

| Metric | Current | TMA-only |
|---|---:|---:|
|Profiled FC2 us|164.192|155.552|
|Registers/thread|124|120|
|Shared bytes/CTA|178688|178688|
|HBM read MB|284.481|284.439|
|TMA read GB|1.693712|1.823998|
|SF cp.async cache-access MB|128.221|0|
|LSU global-load requests|1289444|285924|
|SIMT executed instructions|43975241|29653328|
|Tensor active elapsed%|37.453|38.369|

SASS has 0 LDGSTS sites. New direct SF loads use `UTMALDG.3D.2CTA`. The gain comes with 77.8% fewer LSU requests and 32.6% fewer SIMT instructions; HBM traffic is unchanged. These profiler durations are replay observations, separate from CUPTI benchmark medians. Raw report, raw metric CSV and source/SASS CSV are retained.

## Validation

- Original TMA-with-emptybarriers: 48 strict byte comparisons across six formats, N128/N256, per-token on/off, short K andtail K.
- TMA-only frozen13ca: 96 strict comparisons:48 above, plus 24 one-CTA short K cases with NaN invalid SF, plus 24 two-CTA tail K cases with NaN invalid SF. Output canaries and untouched scatter rows checked.
- Private marker/static-shape integration: 96 strict comparisons passed: 48 N128/N256 short-K and tail cases, 24 small-N16/N64 one-CTA fallback cases, and 24 fused-finalize top-k1 cases. Fused checks initialize output to zero, verify nonzero live results, retain canaries, and poison invalid SFs. The no-cast negative is excluded.
- Six formats: NVFP4, FP4/E8M0 SF16, MXFP4 SF32, MXFP8 E4M3 SF32, MXFP8 E5M2 SF32, mixed FP4weights/FP8activations SF32.
- Local integration patch parses, is Ruff-formatted, applies cleanly to 1904964, and preserves every existing iKET marker name. Markers are disabled for performance measurements.

## Representative commands

From the remote project root:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=candidate SFB_SHORT=1 .venv/bin/python scripts/sfb_tma_experiment/run_paired.py --variant tma_only
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=candidate SFB_GROUP=1 SFB_POISON=1 SFB_SHORT=1 .venv/bin/python scripts/sfb_tma_experiment/run_paired.py --variant tma_only
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=candidate .venv/bin/python scripts/sfb_tma_experiment/profile_native_fc2.py --repo candidate --tokens 16384 --tile 128 --variant tma_only,baseline,tma_only --full --output logs/new-reverse.json
CUDA_VISIBLE_DEVICES=0 PYTHONPATH=candidate .venv/bin/python scripts/sfb_tma_experiment/profile_native_mixed.py --repo candidate --tokens 16384 --tile 128 --weight-format mxfp8 --variant baseline,tma_only,baseline --full --output logs/new-mxfp8.json
```

Task-local harnesses, immutable cores, review patch, raw 100-sample timing JSON, logs, NCU report and CSVs live in the evidence archive. No architecture-specific payload fallback, extra GMEM staging, per-token arithmetic changes, or format exclusions.

The first small-N control accidentally requested unsupported M256/N16 and was rejected by host validation before kernel launch; the corrected one-CTA control passes 24 cases. That log is retained as harness history. GPU0 and GPU6 were released after completion; the failed no-cast process exited, and fresh retained-cast CUDA contexts passed the final checks.
