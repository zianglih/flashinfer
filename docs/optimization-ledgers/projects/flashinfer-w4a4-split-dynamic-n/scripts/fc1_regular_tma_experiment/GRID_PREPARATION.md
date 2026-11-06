# Routed preparation grid diagnostic

The source under review is the unstaged `flashinfer-regular-tma` checkout based on `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. The selected preparation grid uses the GPU thread-capacity limit, verified against the compiled kernel's actual occupancy for this screen. This is a preparation-only result; full-chain performance is a separate gate owned by `run_source_pairs.py` on GPU5.

## Structure and source evidence

The implementation preserves the established W4A16 permutation structure: one persistent CTA per routed row, source row `mapping[row] / top_k`, and 128-bit payload copies. Native `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:66–103` contains that row/copy loop; lines112–121 use256threads and `cudaOccupancyMaxActiveBlocksPerMultiprocessor` to choose the persistent grid. Its SF handling is still a stub at line97.

The new128-thread preparation extends that structure with byte-preserving SF copies into the existing canonical blockscaled layout, invalid-row zeroing, and only the bounded payload/SF padding needed by TMA. It does not quantize values or permute per-token scale metadata. It keeps fused FC1 activation in the GEMM. The source is unchanged during every reported compile and measurement.

The initial four-CTA-per-SM grid limited the kernel to at most16resident warps/SM. The grid16 specialization has32registers/thread,0staticSMEM,0localmemory, and the CUDA driver reports16active128-thread CTAs/SM. Thus the thread-capacity bound used in the actual source matches actual resource-limited residency for this specialization. No dimension-specific cutoff was introduced.

## Measured preparation medians

C1 `fi-w4a4-pipeline-1025`, GPU4 B200,148SMs, CUDA13.2, PyTorch26.05, DSL4.7.1. Inputs and routing are the native benchmark's NVFP4 DeepSeek shape with7168hidden, top8,32localexperts, fixedN128NB2 tactic. Each arm uses unchanged10warmups/100cold-L2 CUDA-graph CUPTI samples. All100 samples are archived. Order is4→8→16→16→8→4 CTAs/SM.

| Tokens | Grid4 forward | Grid8 forward | Grid16 forward | Grid16 reverse | Grid8 reverse | Grid4 reverse | Native payload-only floor |
|---:|---:|---:|---:|---:|---:|---:|---:|
|8192|29.344|20.480|17.728|17.728|20.577|29.408|13.984|
|16384|54.720|35.184|30.0805|30.049|35.296|54.6885|24.321|

All values areµs. The native payload-only floor deliberately omits SF preparation and invalid/padding zeroing; it is not a candidate full-chain implementation. The grid16 gain is about1.66×at8K and1.82×at16K for preparation alone.

Before timing, each grid's entire payload and SF output allocation matched grid4 byte-for-byte, including untouched-capacity canaries. `results/source-grid16-phase-r2.json` contains native input/final fingerprints, routing, full samples, source hashes, and the resource query results. `grid-phase-receipt.json` is a compact derived receipt.

The initial r1 callback closed over a pre-capture CUDA stream, producing an empty graph and an explicit CUPTI error. No timing samples from that attempt are used. The r2 callback retrieves the current stream inside each launch. Both logs are retained.

## Bounded actual-source graph checks

`probe_prep_source_graph.py` imports the actual review checkout and verifies its prep SHA before compiling. NVFP4/SF16 and E4M3/SF32 each cover routeN16/32/64 and the same captured graph/buffers replayed with active tile counts0→1→5→2→0:30checks. Every complete output allocation matches an independent CPU byte reference, including inactive-capacity and suffix canaries. This covers N16's bounded extra16payload rows, canonical128-row SF padding, and zero-route no-write behavior.

`results/source-prep-graph-r1/receipt.json` records all30checks. Three cubins were regenerated afterward using the identical immutable source, grid specializations, and `--keep-cubin` option; their hashes/resources are archived there. They were not saved during the timing run. All report32registers/thread, no local memory, no staticSMEM, and16activeblocks/SM.

A duplicate GPU4 full-chain driver briefly started after crossed coordination messages and was explicitly stopped by exact PID plus descendants. Its incomplete `source-grid16-native-gpu4-r1` directory is preserved but excluded from the decision. The coordinated GPU5 campaign is the full-chain gate.

## Commands and source identity

- Phase command: `run_grid_source_r2.sh` (executed through managed `/usr/local/bin/h ssh`).
- Graph/cubin command: `run_prep_graph.sh`.
- Read-only archive: `archive_grid_evidence.py`.
- Prep source SHA256: `125d0f15910debc75ca1a128c6c59ad83db84558ef66fe338d362371955d4392`.
- Core source SHA256: `9f53fd0a8a775f0091d3b718d944e0271708ae8022d9fac59ae7dba6425d1c0a`.
- Full three-file source manifest: `review_snapshots/grid16/manifest.json`.
- Raw/cubin archive hashes: `grid-archive-manifest.json`.

No original `flashinfer/` production files were edited, no changes were staged/committed/pushed, and no full primary benchmark or baseline campaign was rerun for this diagnostic.
