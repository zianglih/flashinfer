# R6 CUPTI timeline: FC1 accounts for the K3 regression

K3 EP8, MXFP4x8, 4096 tokens, unfused finalize, GPU 7 on `fi-fc1-gather-1028` (B300, `nvcr.io/nvidia/pytorch:26.05-py3`). This is a bounded diagnostic capture, **not retention timing**: one 100-sample public CUPTI run per role, retained `d35fcfda` versus frozen R6 (`moe_swap_ab_kernel.py` SHA256 `deba8b639fba89e6f76381e8c6bf8bc323ccaf850b973c836f476f8144c4cc0a`). Both roles completed within 18 seconds each; the whole controller took 34 seconds.

| Activity | Retained median duration (µs) | R6 median duration (µs) |
|---|---:|---:|
| Route sorting | 16.608 | 16.512 |
| PrepareRouted | 12.593 | removed |
| FC1 | 223.633 | 1037.849 |
| FC2 | 140.529 | 207.058 |
| Combine | 20.512 | 20.320 |
| End-to-end span | 397.779 | 1203.146 |

The apparent FC2 duration increase is matched by greater overlap with FC1: their median overlap grows from **9.936 to 76.257 µs**. The interval from FC1 completion to FC2 completion remains **130.305 versus 130.657 µs**. Kernel duration includes PDL waits and concurrency; these are not exclusive execution times.

For exact additive accounting, each kernel's *completion increment* is its end minus the largest preceding kernel end. The following means add exactly to the mean end-to-end span; their differences isolate the chain extension without double-counting overlap:

| Completion increment | Retained mean (µs) | R6 mean (µs) | R6 − retained (µs) |
|---|---:|---:|---:|
| Route sorting | 16.59375 | 16.52206 | -0.07169 |
| PrepareRouted | 12.36428 | 0 | -12.36428 |
| FC1 | 220.63931 | 1035.37699 | **+814.73768** |
| FC2 | 130.63959 | 130.62827 | -0.01132 |
| Combine | 18.14767 | 18.12356 | -0.02411 |
| End-to-end span | 398.38460 | 1200.65088 | **+802.26628** |

FC1 also starts earlier (median 25.729 → 16.224 µs) after deleting prepare. Thus the separate prepare removal and other stages do not explain the regression: the additional FC1 time does. The activity trace cannot distinguish payload issue efficiency, scale publication, operand reuse stalls, or other internal FC1 causes. No hardware-counter claim is made; NCU was unavailable.

## Source, route and timing binding

- All 513 source hashes, Git HEAD and candidate full patch verified before and after each role. Both roles retain exactly the same `fused_moe.py` (`d05dc8f9a700243bdc2b90109eba4921682ad31e51cbc9c7ee5d604379be9f4b`) and `testing/utils.py` (`7b67a4c51449ddb241829fc260823397e60fd12a97bac7f73709b3b5fdeba170`). Native persistent compile-cache links remain unchanged.
- Frozen winner and private cache copies verified unchanged, `profile_calls == 0`, no admitted tactics, exact route IDs/weights/histogram identity. Tactic: FC1 and FC2 `(M,N)=(256,128)`, cluster `(2,1)`, no CLC, K steps `(4,4)`.
- Native public benchmark: `--functional-api --model kimi-k3 --ep 8 --tp 1 --quant-family mxfp --backends cute-dsl-w4a8 --num-tokens 4096 --no-autotune --swap-ab --no-fused-finalize --warmup 10 --iters 100`, with the existing observer's CUPTI, cold-L2, graph, no-event-fallback checks.
- Artifact-only injection adds one callback **after** CUPTI collection/flush/disable/finalization, while processing the already captured activity records. Removing that callback yields exactly the original function AST. No GPU work was added or reordered; no repository or existing observer file was modified.
- For every one of the 200 iterations, `max(kernel.end)-min(kernel.start)` equals the observer's original millisecond sample exactly. Raw start/end/correlation IDs and names are retained in `evidence/{control,candidate}/capture/timeline.json`.
- The two grouped GEMM names collide in CUPTI. They are identified by the same-stream source launch/start order, with expected activity sequence and monotonically increasing completion order asserted for every iteration. The common caller launches `moe_sort` at `fused_moe.py:654`, FC1 `gather_gemm` at `:798`, FC2 `finalize_gemm` at `:934`, then `moe_unpermute` at `:963`. The retained FC1 wrapper calls prepare at `moe_swap_ab.py:143–161`; R6 removes that separate launch. This mapping is not based on ambiguous kernel names alone.

## Receipts

- `summary.json`: full per-iteration stages, distributions, overlap, exact sources, winner and route identity.
- `analyze.py`: reproducible CPU-only analysis and assertions.
- `evidence.tar.gz`: 19 raw receipt/log/helper/activity files, SHA256 `3ba59b2c23d999fdcc42dbe3f209315f08cde5d4b8cedfcafaf64671b51ce1cf`.
- `collection.json`: final idle proof: no owned processes, no GPU 7 compute process, 0 MiB / 0% GPU utilization. GPU 7 was explicitly released to root immediately after the capture.

Do not use these single-role diagnostic runs to update PR performance tables or as a retention decision. Use the controlled CAAC screen for that purpose.
