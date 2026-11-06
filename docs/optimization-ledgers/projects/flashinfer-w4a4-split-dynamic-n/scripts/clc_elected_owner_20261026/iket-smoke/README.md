# Fixed-lane owner IKET smoke

**Passed on frozen `d8ca478d88600876d317374b3f07b873a30f4dd550bd7665a8bad88855069d20` over `9b4721b0`.** This verifies the fixed-lane owner version, not the subsequent helper-isolated election candidate. No source or production benchmark was changed.

GPU7 B300, CUDA13.2, CuTe DSL4.7.1, existing `nvcr.io/nvidia/pytorch:26.05-py3` devbox. The task-local adapter reuses the frozen `probe_elected_owner.py` gate and enables only the existing `enable_iket` constructor option plus IKET compilation. Native C++ cache reuse is unchanged; the candidate source/workspace remain pinned. `run-iket` uses NativeDump, a 600-second bound and separate tracker/profile processes. It completed in about133seconds. No timing inference is drawn from instrumented execution.

| Check | Result |
|---|---|
| Config0 | Standard NVFP4, N16/M128, one CTA, inline epilogue |
| Config1 | Standard NVFP4, N256/M256, two CTAs, overlapped epilogue, SiTU |
| Modes/routes | PDL off/on; balanced, skewed, empty, reactivated routes and changed input/router weights |
| Tracker | 8 marker-enabled core compilations; 16 exact source-paired replays passed |
| Actual NativeDump profiling | 8 marker-enabled core compilations; 16 exact source-paired replays passed |
| Marker evidence | `scheduler_item` appears in all52 instrumented GEMM launches:20 regular and32 from16 public-chain graph replays |
| Owner-loop trace | 174,616 matched scheduler ranges, confined to scheduler warps5/9; both CTA parities observed in the two-CTA configuration |
| Source integrity | HEAD, patch and all pinned source-file hashes verified unchanged before/after |

The exact installed SDK marker implementations captured in `../sdk-iket.py` emit IKET push/pop IR directly, without a hidden warp collective. This smoke confirms marker lowering and actual execution complete under fixed-lane ownership for the two tested configurations. It is not exhaustive instrumentation, synchronization or sanitizer coverage. Warp-level trace locations do not identify individual issuing lanes, and marker counts do not distinguish successful live cancellations from padded or failed claims.

The profiler emitted its documented unsupported logical-endpoint warning and allocated a42.69GiB context buffer from the conservative8192timestamps/warp limit. Both passes and trace export completed successfully; no overflow/error was reported. GPU7 was released after the instrumented process exited, with0MiB/0% at inventory; later work may now occupy it. No other GPU was used.

`evidence/receipt.json` binds source, environment, commands, helper hashes, reused control hashes and both output receipts. `evidence/marker-summary.json` binds every marker launch and the instrumentation configuration. PTX/cubin/SASS and resource reports are included for both processes. `evidence/artifact-manifest.json` pins all generated artifacts; the large raw data, decoded JSON and final trace remain in persistent remote storage under `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/clc-elected-owner-20261026/iket-smoke`.

Verified local bundle `evidence.tar.gz`: SHA256 `4da493cc3ba5bfa6d0ec75c97e58534cdbc923b44f8a71dfca861a963bcafc06`, 97files,1,284,164bytes. Full trace SHA256: `f5a8a91915d19f9cd74812753cd6c2e6ff80655cb80a79c068065be3e9b759ad`.
