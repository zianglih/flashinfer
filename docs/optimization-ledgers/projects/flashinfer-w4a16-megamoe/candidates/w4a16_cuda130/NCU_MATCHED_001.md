# Matched compiler NCU capture: bounded evidence and limits

No further NCU runs are planned from this series. Both initial captures and the two-collective PC-only control completed on all eight B300 devices with clean FlashInfer6315, fixed M256/N128/K256 CONTROL and two transform groups. Source1572 before/after hashes, actual compiled geometry, native compiler identity and loaded NVSHMEM/NCCL/cudart hashes pass the saved-artifact audit. Profiler execution times are excluded from performance claims.

- Initial direct: `logs/cu130-matched-ncu-001/` and `profiles/cu130-matched-ncu-001-direct/`. The profiler itself succeeded; the effort driver then rejected its report-name assumption. Original helper and failure are retained. Device identity is established using `launch__device_id`, not the NCU communicator suffix.
- Initial fallback: `logs/cu130-matched-ncu-002/` and `profiles/cu130-matched-ncu-002-fallback/`. Each initial report contains one production action and four replay passes.
- Paired PC-only control: `logs/cu130-matched-ncu-pc2-001/` and `profiles/cu130-matched-ncu-pc2-001-{direct,fallback}/`. Both arms have eight reports with two separate actual production actions per rank, one replay pass and unchanged source/runtime/geometry. First and second actions remain separate in `pc-samples.json`.
- Machine-readable audit: `profiles/codegen-comparison/cu130-matched-ncu-{initial-source-runtime,pc2-001-source-runtime}.json`, reproduced by `audit_matched_ncu.py` (with `--pc2` for the latter). All actions use640 threads,96 registers and216576 dynamic shared-memory bytes.

The captures show substantial profiler-induced collective launch skew. Initial direct per-rank instrumented durations range about0.47–288ms and fallback0.50–107ms, far from ordinary CUPTI measurements. Early ranks mostly sample scheduler/token-ready waits, while a late rank has many more distinct compute PCs. NCU lockstep coordinates matching collective launch numbers; these observations do not establish simultaneous physical GPU starts. The second PC-only collective still has large rank-to-rank sample disparity, so discarding only the first capture does not solve the problem. Overflow and dropped-byte counters are zero; this does not establish that sampling was free of a heuristic limit (several reports have approximately3.262M samples).

Consequently, tensor utilization, whole-kernel sampled wait shares and cross-rank aggregate ratios are not used to identify a production bottleneck or to attribute the fallback latency gap to decoding. The data retains useful source/CFG locations for future narrowly targeted reasoning, and confirms the same source-matched SASS as the earlier generated-code capture.

| Site, exact TRYWAIT/NANOSLEEP stub | Direct PC | Fallback PC | Pipeline offset |
| --- | --- | --- | --- |
| Transform waits for raw weight/scale | 0x14ca0 / 0x14d60 | 0x17180 / 0x17260 | +0x00 |
| Transform waits for reusable decoded TMEM | 0x14d00 / 0x14dc0 | 0x171f0 / 0x172d0 | +0x60 |
| MMA waits for accumulator availability | 0x14fa0 | 0x17560 | +0xa0 |
| MMA waits for decoded weight | 0x15000 | 0x175d0 | +0x50 |
| MMA waits for activation tile | 0x15060 | 0x17640 | +0x70 |
| Epilogue waits for FC1 accumulator | 0x151d0 | 0x17810 | +0x90 |

The offsets refer to the actual matching barrier base in each instruction sequence. Optimized source-line attribution alone is insufficient: arithmetic can inherit a wait-call line, so these labels require the adjacent SYNCS.PHASECHK TRYWAIT control sequence. Matched SASS remains5672 direct versus6288 fallback instructions; the already independently traced fallback widening/packing dependency is static evidence, not a measured latency contribution. See `MATCHED_CODEGEN_002.md` and `profiles/codegen-comparison/cu130-matched-002-decode-independent.json`.
