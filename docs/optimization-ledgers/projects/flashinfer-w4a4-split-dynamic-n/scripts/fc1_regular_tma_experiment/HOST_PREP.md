# Regular-TMA routed input preparation

This task-local prototype uses immutable production442 as control. No upstream source or native JIT epoch changes. `regular_trial/regular_core.py` is owned by the device-core agent; `prep.py`, `install.py`, `probe_native.py` are owned by the host/preparation agent.

## Exact buffer and API contract

- Payload retains original byte encoding: packed FP4 `[capacity,K/2]` or E4M3/E5M2 `[capacity,K]`. No conversion, requantization or extra activation stage.
- Linear source SF `[original_tokens,K/sf_vec]` becomes canonical128-row/four-scale storage. Four scale bytes are copied as one UInt32; output word offset is `(row//128)*Kblocks*128 + kblock*128 + (row%32)*4 + (row%128)//32`, where `Kblocks=K/(4*sf_vec)`.
- Mapping, original token count and original per-token scale vector remain unchanged. The regular core still uses original mapping/token IDs for epilogue scaling.
- Read `num_tiles` and per-tile absolute `mn_limit` before reading mapping. Invalid mapping slots can contain poison and are never read.
- Zero payload only within physical active extent: `min(capacity,num_tiles*routeN+max(0,allocatedN-routeN))`, with zero extent when no tiles. N16 requires a final extra16 rows because physical B has32 rows. N128/256 have no extra payload rows. Zero SF rows through the final128-row atom, and preserve unused capacity/suffix canaries.
- Supported reduction geometry has `K % (4*sf_vec)==0`; TMA itself zero-fills any wider final K-stage tile. There is no hidden SF tail loaded from the next canonical row block.
- Preparation uses a bounded persistent grid and device runtime tile count. It never reads `.item()` or synchronizes metadata on the host.

`install.py` intercepts the internal host call after the unchanged public FC1 wrapper has validated its original tensors and allocated output. It prepares payload/SF and forwards original token metadata into a separate regular-core compiler cache. Public function signatures/workflow and output allocations stay intact. FC2 always uses the frozen442 class/cache. Scratch buffers are allocated before captured timing; preparation executes on every full-chain call.

## Current checks

`probe_prep.py --minimal` passed6 NVFP4 cases: routeN16/128/256 × K64/7168, exact arbitrary payload/SF bytes, poisoned inactive mapping, padded rows, untouched remaining capacity/suffix guards, and zero-tile reuse. A first compile attempt required an explicit Uint32 conversion for a loaded scale word; failed source is preserved at `history/prep_compile_v1.py`, remote failure log `logs/regular-tma-prep-smoke.log`. No GPU data was produced by that compile failure.

Native T128 N128NB2 baseline/regular full final outputs matched exactly. The low-level device agent independently passed12 NVFP4 and36 broader-format cases. This does not replace later integration coverage or sanitizer checks if performance is retained.

## Native gate

GPU5, same recovered C1 B200 and candidate cache environment. Native DeepSeek routing, H7168/I2048, topk8, simulatedEP8, unfused finalization. Fixed diagnostic tactic `[128,[[512,128],[2,1],false],[[256,128],[2,1],false]]` keepsFC2 unchanged. Run8K/16K, both baseline→regular→baseline and regular→baseline→regular orders. Each arm retains all100 cold-L2 CUDA-graph CUPTI samples after10warmups. Full-chain timing includes preparation. Prep-only timing is separately labeled diagnostic and never subtracted to claim pipeline latency.

These are adjacent fixed-tactic diagnostics, not replacement primary B1/A1/A2/B2 data. Source/metadata/software hashes accompany each result. The ordered `arms` list retains repeated bracketing controls without overwriting samples.

## Actual source-copy continuation

The completed first grid4 runtime-overlay gate is archived at `evidence/regular-tma-first-gate-442/raw.tar.gz` (SHA256 `c65c27e9b8aa65882bda2145b5ec9e83344c079b940a03e3a2fc1f57f38dacda`). Every arm was byte-exact, but full chain regressed:8K controls300.129/301.201/302.9605µs vs regular317.2005/317.185/320.209µs;16K controls524.1135/524.113/526.225µs vs regular540.8655/534.578/540.289µs. All raw samples remain in the archive.

User-requested source-copy workflow now supersedes runtime interception for active experiments. `flashinfer-regular-tma` is an independent checkout at442 with unstaged actual device core, internal host preparation call, and `blackwell/moe_prepare.py`. Initial three-file snapshot is immutable under `review_snapshots/initial`. The preparation agent owns the subsequent grid16 source; we own host integration and direct-source harness. No original repository modifications or commits/pushes occurred.

W4A16 precedent: `blackwell/moe_w4a16.py:59–93` deliberately allocates invocation-local sort/hidden/intermediate workspaces for caching allocator reuse and graph-private ownership; lines403–453 execute sort→permutation→FC1 and pass PDL through each stage. This experiment follows that ordering with byte-preserving packed payload+canonical SF preparation, retains original per-token scale addressing, and uses invocation-local allocations. No tensor cache persists across calls. See `DIRECT_SOURCE.md` for actual-source commands and explicit fixed-tactic scope.
