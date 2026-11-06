# Prospective same-node native compiler control

Status: plan only. The replacement130 devbox became unavailable before the static-FC2 upload; root has held another request until the CUDA13.2 retained source is known. This plan launches nothing and changes no source, native environment or timer. See `NEXT_RECOVERY.md` for that boundary.

The next useful control is **fallback12.9 → direct13.3 → fallback12.9 on one node, one exact retained source and one fixed actual Mega tactic**. It removes source, tactic, image, Torch and host-library differences from the current cross-stack comparison. It isolates the native compiler/backend plus its capability-selected decode implementation together; it is not an arithmetic-only fallback ablation.

## What the current evidence establishes

The same-node C1/e2d88 report in `logs/cu130-recovery0908b-c1-vs-zero-dest512-001-analysis/` retains all104 raw values,416 split selections,416 compiled records and208 automatic winner records. All104 fixed source-to-source public configs match. The fixed512 result is lower in8/13 rows; automatic512 is lower than automatic C1 in6/13. Eleven automatic winners differ, and the exact fixed/auto512 config is unchanged atT1/2048/4096 despite different measured times. This cannot identify a compiler cost. The independent verification JSON reproduces these facts from the original logs.

The previous same-node compiler arm used **source6315,640 threads** on the now-lost original130 node. Its direct arm completed; the immediately following fallback arm stalled before Mega4096. The later successful uninstrumented fallback repeat is a separate run, not completion of that bracket:

| T | Earlier direct13.3 Mega ms | Separate completed fallback12.9 Mega ms |
| ---: | ---: | ---: |
| 1 | 0.087633 | 0.088704 |
| 256 | 0.245011 | 0.273667 |
| 4096 | 0.509397 | 0.543476 |

Read the original `logs/cu130-same-node-compiler-001/direct.json`, partial fallback log and `logs/cu130-uninstrumented-repeat-001/results.json` together with `candidates/w4a16_cuda130/README.md`. The missing original fallback4096 stays missing. Debugger attachment subsequently failed and produced crashes; no reliable device PCs explained the preceding stall. Tiny-token variation was substantial across separate runs. These old values are context, not current512 or retained-source performance.

Matched old6315 codegen is stronger mechanism evidence: `candidates/w4a16_cuda130/MATCHED_CODEGEN_002.md` and `profiles/codegen-comparison/cu130-matched-002*` preserve all16 production rank captures. The fallback adds256 FP16→FP32 widening operations and128 BF16 packs in the marked transform interval, producing an actual dependency chain before the same16 STTM.x8 operations. Direct/fallback have809/1280 transform-interval instructions and5672/6288 total instructions. Both have the same21 existing FC2 local operations and no transform-interval local accesses. Other compiler differences remain. These are not current512 PCs or resource claims.

The associated EP8 NCU and two-action PC runs suffered severe collective launch skew; even the second action was unsuitable for duration, utilization or wait-share attribution. `NCU_MATCHED_001.md` retains source/CFG-resolved sites only. Repeating that skewed profiler series is not the proposed first step. Previously exact register-table and scalar-tail decoder alternatives both regressed in integrated A/B/A and were restored; no new decoder rewrite is justified by static instruction count alone.

## Exact bounded experiment after recovery and source selection

1. Freeze the retained complete source inventory. If root retains28a, use28a in all three arms; do not combine an e2d88 fallback row with a28a direct row. Keep two transform groups. No new public knob or source capability override.
2. Preserve the actual DSL4.7.1/cu12-only fallback venv, native12.9 and gateFalse. Create a separate matching4.7.1/cu13-only venv using the prior `candidates/w4a16_cuda130/setup_direct_control.sh` pattern, with native13.3 and gateTrue. Preserve image Torch/systemCUDA13.0 and library paths. Do not spoof `CUDA_VERSION`. Compare actual imported Python DSL files, interpreter/torchrun bindings, native extension paths/hashes and distribution metadata. The two native extensions are the intended difference; compiled code beyond the decoder may change.
3. Before any timing, run the new-source actual resource admission on each compiler and the established EP1/EP2 numerical gates with original tolerances. For a retained512 source, require actual REG128/512threads/two groups/65,536-register pool before every Mega invocation. Old640 or cross-compiler objects cannot satisfy that gate.
4. Run three independent processes in A/B/A order, each using the primary distributed benchmark atEP8,H7168/I2048/E256/top8 and globalT1/256/4096,100CUPTI iterations. Fixed CONTROL remains M256/N128/K256,C2,F4,epi,(2,4),group512,atomic. Inspect actual per-rank config and compiled records. Leave warmup, cold-L2 behavior, graph replay, activity spans and rank aggregation untouched. Use the existing600s timeout derivation; no profiler, breadcrumbs, debugger or per-iteration tracing.
5. Use fresh DSL and driver cache namespaces per arm. Reuse native routing/Torch caches only from a completed, same-node/source/Torch/nvcc owner with strict native/source admission; otherwise build fresh. A compiler-only difference does not automatically prove native ABI/cache compatibility. Preserve before inventories without claiming cache bytes are unchanged afterward. No lost-node cache identity is reusable.
6. Capture all8 live worker maps independently of the benchmark, with stable PID/start-time/argv/stack/rank binding and the established marker-attribution limit. Require equal loaded NVSHMEM/NCCL/cudart hashes across the bracket, as well as actual intended native extension hashes and decoder gates. Save full source/helper before/after inventories and per-arm preflights.
7. Require all24 split and24 compiled rank/shape records plus six raw latency values in every arm. Split independently retunes and also uses the selected compiler/decode path: retain its absolute timings and actual tactics, and do not call split an unchanged control. Compare absolute Mega against both fallback baselines. A persistent >5% movement against both controls warrants follow-up; report smaller/control-sized changes without a win claim.
8. Stop dependent arms on a failure. Preserve completed and partial arms separately, raw logs and bounded host/process/GPU state. No native cuda-gdb attachment in this stack after the historical attachment failure. A partial bracket cannot replace the successful full13 tables.

The prior `run_compiler_control.py` establishes the orchestration pattern, but its frozen6315 owner/source admission is not a valid512 launcher. Implement a distinct retained-source sibling when scheduled, preserving the same benchmark payload and adding the existing actual-resource gate. Do not broaden the old validator or use its old cache owner on a replacement node.

## If the bracket still shows a gap

First capture matched retained-source production codegen under both compilers, with timing instrumentation disabled, and attribute dependency chains and local accesses by role. The old6315 offsets must not be carried forward as current PCs. A focused EP1 NCU control using the prepared production-profile resource gate could then examine decoded-stage waits and LDS→convert→STTM dependencies without eight-rank profiling skew; it must disclose the changed EP1 expert/routing workload and cannot be substituted for EP8 throughput.

If an arithmetic-only ablation is needed later, it is a distinct experiment: keep one compiler/runtime fixed and explicitly compile the original fallback helper body in an effort-only alternate function while leaving the actual reported capability honest. That requires separate parent scheduling, the existing65,536-output exactness gate and integrated source-attested A/B/A within the already authorized optimization work. It would test a code path under one compiler, not establish actual pre13.2 support. No such source change is prepared or executed here.
