# Register128 codegen decision

Rejected before timing. No correctness or performance claim is made; only compilation and generated-code evidence was collected.

| Fixed FC1 tactic | Retained instructions | Candidate instructions | Gather change | Dequant change | Local storage |
|---|---:|---:|---:|---:|---:|
| M256 N128 K256, two CTA | 2010 | 2055 | +43 | +3 | 0 B both |
| M256 N192 K256, two CTA | 2056 | 2101 | +42 | +3 | 0 B both |
| M256 N16 K256, two CTA | 1675 | 1678 | +0 | +3 | 0 B both |

Counts exclude NOP but include terminal/trap instructions. Three paired captures completed; all6 cubins report96 launch registers,640 maxthreads,0 localbytes,0 LDL/STL sites. Gather/dequant CFGs have no indirect/control-flow unknowns and fit their dynamic targets. Control has an indirect warp-dispatch jump and epilogue calls helpers; their whole-role peak is not asserted by this partial CFG walker.

N128/N192 gather32 introduces42–43 additional reachable instructions, chiefly uniform address arithmetic. Dequant adds its allocation handshake but does not reduce packed weight decode, scale decode, LDS or STTM counts. The N128 compiler uses up toR80 for dequant versusR47 retained; its firstSTTM is delayed from after10 to after32 FP4-unpack instructions. There is no convincing reduction of memory/decode work or improved overlap to justify timing this specific allocation.

A single evidence-driven follow-up preserves gather64 and donates only epilogue registers:112/80/112/112/64, same61,440 pool. This is distinct from the previously rejected144/80/112/112/32 design. Its first gate is oneN128 cubin; no broad sweep.

Frozen source/patch inlocal-source.json, allsource binding in evidence/perf-config.json, codegen-analysis.json and dequant excerpts. Review source moved to flashinfer-w4a16-register-review for the follow-up; register128 patch and raw evidence remain here.
