# R11 guarded qualification

Candidate kernel SHA: `3a2b03635a13faa50549de903eebb265a13c50d8ac804c2ae3b1e245da10650f`.
Register policy: control warpgroup 80, gather warpgroup 128, epilogue warpgroup 256; 384 FC1 threads. FC2 keeps the original 256-thread policy.

The qualification guard inspects `compiled.artifacts.CUBIN` before returning the compiled callable. It requests dump-only `--keep-cubin`, uses `no_cache=True` for those CuTe compilations, and checks the binary's `EIATTR_REQNTID`, register count, and `USETMAXREG` instructions. It also verifies the frozen source before and after the process. Native C++ and persistent FlashInfer compilation caches remain intact. Compilation/disassembly happen before benchmark CUDA-graph timing.

Two diagnostic approaches were rejected before any unsafe kernel launch: CuTe's PTX text artifact sometimes described a preceding kernel even when the current CUBIN was correct; direct IR extraction returned no embedded cubin on cached compiled functions. Those failed harness receipts are preserved separately on the devbox. They are not accuracy failures.

Primary NVFP4, MX, and wrapper groups (26 cases) passed with the earlier source-bound guard; the six tail cases and twelve supplemental cases use the final binary-only guard. The supplemental cases cover PDL on/off, one/two CTA, ordinary/CLC scheduling, all four quantization modes, and the existing activation contracts.

`guard_observer_adapter.py` wraps only candidate benchmark compilation. Baseline code, frozen tactics/routes, CAAC order, 10 warmups, 100 CUPTI samples, cold-L2 CUDA graph timing, and initial-quantization scope remain unchanged. Its source and register-policy JSON are recorded in the benchmark observer hashes. Candidate performance using this instrumentation must be described as guarded, dump-enabled compilation; no GPU-timing overhead is included.

The CUDA-dialect compiled function returned by the benchmark did not emit its CUBIN artifact even with both process-level and per-call CuTe cache bypass. This is not a kernel failure and the attempts stopped before launch. Test artifact availability does not establish benchmark artifact availability. The performance guard will query the loaded CUDA function instead; see the final helper/receipt for the active mechanism.

## Active performance guard

The stable helper is `../../r14-r6/runtime-guard/register_guard.py`, SHA `251f758644533c98556eb8d19765345f114d165736789826ce5f9a124cf91aee`. It uses `compiled.library` and CUDA driver `cuKernelGetAttribute` to query the actual executable before launch. Compilation options and caching are unchanged. FC1 pool legality uses source-validated donation targets together with queried `NUM_REGS`; `LOCAL_SIZE_BYTES` is recorded diagnostically. It does not claim to inspect SASS during benchmark replay.

Remote `r11/run_perf.py` and `r14/run_perf.py` are restored to the original SHA `8bd769580477dd838cfd934fb7849ece6ed82a300d6ecf5451ac5d58820440f5`. Use the original `fc1-gather-20261028/launch_selected_perf.py`. The copies of `run_perf.py` and `launch_selected_perf.py` inside this guarded-validation directory preserve the rejected CUBIN-dump attempt and are not active launchers. Failed attempts are excluded from `evidence/perf` analysis.
