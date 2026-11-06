# Helper-scoped elected-owner IKET smoke

**Passed on frozen `96cfbfbe7c2c779fcdaf9e46ce76f19d2989d879903f5037c8eefeb152925dc8` over `9b4721b0`.** This is the helper-isolated election candidate being timed. The earlier fixed-lane `d8ca478d` evidence remains separately preserved in the parent directory and is not relabeled.

The adapter is byte-identical to the earlier smoke: existing kernel marker opt-in plus IKET compilation, without production/source edits. It reuses the exact public-wrapper gate configs0/1 and original control output/input hashes: one-CTA N16/M128 inline epilogue and two-CTA N256/M256 overlapped epilogue with SiTU. Both FC phases run with PDL off/on and balanced, skewed, empty and reactivated routes, changing input and routing weights.

- Tracker:8 marker-enabled core compilations and16 exact source-paired replays passed.
- Actual NativeDump profiling:8 marker-enabled core compilations and16 exact source-paired replays passed.
- Trace:52 instrumented GEMM launches, comprising20 regular launches and32 GEMMs from16 graph replays. Every launch contains scheduler markers;174,616 ranges have matching start/end locations and nonnegative durations.
- Owner placement: scheduler ranges occur only on warp5 or9 as appropriate; both CTA parities are present for the two-CTA geometry. This is warp-granular evidence, not individual-lane or cancellation-success instrumentation.
- Source integrity: HEAD, complete patch and all pinned source hashes verified unchanged before/after. The source-private workspace and existing shared native C++ artifacts remain unchanged.

GPU7 B300, CUDA13.2, CuTe DSL4.7.1, image `nvcr.io/nvidia/pytorch:26.05-py3`. The600-second bounded command completed in148.21seconds. GPU7 was verified0MiB/0% and released immediately after completion; no other GPU was used. The profiler's unsupported logical-endpoint capability warning and conservative42.69GiB context-buffer allocation warning are retained in the logs. Both passes and trace export succeeded; no overflow/error was reported. This is marker lowering/runtime validation, not a timing or sanitizer result.

`evidence/receipt.json` contains exact commands, environment, source/cache and helper receipts. `evidence/marker-summary.json` records every marker launch and the instrumented scheduler sites. PTX/cubin/SASS/resource files and output receipts from both processes are included. `evidence/artifact-manifest.json` hashes all artifacts; large raw JSON traces remain under persistent remote `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/clc-elected-owner-20261026/iket-smoke-v3`.

Verified local bundle `evidence.tar.gz`: SHA256 `8645de98af8b47b66d6e371e2a354a96334f32b1d35aa4d4f69b75a23154807f`,97files,1,273,730bytes. Trace SHA256 `0e7cda1464cf799e55921b44d635ccf8b362dcb305a35d79f09c88b10b9af9d5`. Marker-summary SHA256 `fa78a2dae0d4dd931419caf18fcf8772d4992e4c502aa68d54ddd61fcee1d9c1`.
