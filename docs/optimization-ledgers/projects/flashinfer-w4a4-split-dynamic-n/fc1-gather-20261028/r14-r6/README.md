# Prepared R14 versus R6 quick screen

Measured control is the R6 gathered-FC1 snapshot, **not PR head**. Candidate is
R14. Both use base commit `d35fcfda03875077b3af8455575cc1d20e866a8c` with different,
fully pinned patches. The preparation receipt verifies each source's 513 hashes,
full Git patch and 9 persistent native-cache links. No implementation was changed.

- R6 kernel: `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`.
- R14 kernel: `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372`.
- Jobs: V3 EP8 NVFP4 + per-token; K3 EP8 MXFP4x8; V41F EP4 MXFP8 + MXFP4x8;
  N3U TP8 MXFP8 + MXFP4x8. Tokens 8, 256, 4096, 16384 for each.
- Method: existing public functional benchmark, frozen routing/tactics,
  control-candidate-candidate-control, 10 warmups, 100 CUPTI cold-L2 graph samples.
  NVFP4 includes input activation quantization. No TRTLLM or non-swap reruns.
- Candidate uses the loaded-kernel runtime resource guard. Compiler options,
  CuTe cache and persistent C++ cache remain normal. Control is unguarded.

Prepared remotely under
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/r14-r6`.
No launch has been performed by this agent. After root explicitly allocates
GPUs 0–1, invoke from the project root:

```bash
python3 optimization-20261028/swap-ab-hybrid-output/remote_box.py \
  --box fi-fc1-gather-1028 --namespace ziangli \
  fc1-gather-20261028/r14-r6/launch_remote.py
```

The launcher requires R14's 32 primary and 12 supplemental tests to pass, all four
R11 quick jobs to finish, source/hash checks to hold, and both GPUs to be idle.
GPU 0 runs V3 then N3U; GPU 1 runs K3 then V41F. Phase receipts explicitly identify
R6 as control. `run_perf.diff` shows the only driver edits: comparison labels,
full patch verification and persistent-cache-link verification. The timing
observer, guard adapter and guard are reused unchanged from finalized R14.

## Runtime guard qualification

`runtime-guard/verified-smoke.json` contains the native K3 EP8 T4096 smoke and
verified routes, winner cache, 100 CUPTI samples and source hashes. FC1's loaded
kernel reports 168 registers, 384 maximum threads and 0 local bytes; FC2 reports
108 registers, 512 maximum threads and 0 local bytes. No kernel launches occur in
the query itself: `compiled.library` performs lazy library loading, then driver
APIs enumerate its sole kernel and query attributes before returning the callable.

`MAX_THREADS_PER_BLOCK` is a limit, not `.reqntid`. The guard compares that limit
with the source's launch threads, then validates the FC1 register pool using
those 384 threads. Donation targets/warp roles come from frozen source and prior
SASS validation; runtime querying does not claim to inspect SASS. `LOCAL_SIZE_BYTES`
reports local memory per thread, not instruction-site spill counts.
