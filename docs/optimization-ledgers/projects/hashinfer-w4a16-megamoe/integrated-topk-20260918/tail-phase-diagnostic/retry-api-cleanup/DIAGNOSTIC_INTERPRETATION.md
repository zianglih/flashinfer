# Retained 7dc tail-phase diagnostic

All four fresh same-node cases passed. The archive contains 16 rankwise bit-exact control/instrumented outputs, 96 independent eager/graph snapshots, and all four fused ABI artifacts per rank. The two failed harness attempts remain preserved separately.

| Global tokens | Fresh control median / MAD (µs) | Instrumented median / MAD (µs) | Instrumented/control |
| ---: | ---: | ---: | ---: |
| 128 | 190.7045 / 0.7205 | 192.6570 / 0.8480 | 1.010238× |
| 8192 | 807.6690 / 22.1920 | 777.1445 / 15.8085 | 0.962207× |

At 128 tokens, the latest cleanup leader observation occurs about 6.2 µs after the latest reduction leader observation in graph snapshots. At 8192 tokens, the latest reduction leader occurs about 18.5 µs after cleanup. Every snapshot at each shape has the same ordering; eager snapshots agree. These observations favor testing cleanup lifetime at small shapes and reduction work distribution at large shapes. They do not establish an end-to-end speedup or that either marker equals kernel completion.

All 64 control/instrumented ABI pairs retain REG96/STACK0/LOCAL0/SHARED1024 and zero LDL/STL. The PTX synchronization opcode sequence is unchanged; instrumented entries have 20 static globaltimer sites. Representative vector lowering places lane-zero timestamps around the existing barriers, drain, active reduction and reset boundaries. The diagnostic uses fixed per-CTA/per-warp records without new hardware barriers or atomics; source AST reversal was independently checked before execution.

`role_work_end` precedes producer-tail handling for producer/decode roles and follows epilogue cleanup; `bar8_first_enter` is the retirement boundary. `reduce_last` is a warp-leader issue observation, not proof that every lane's output is globally visible. The cleanup gap includes marker overhead, scheduling and waiting; inactive reset leaders show comparable gaps, so it cannot be interpreted as the cost of clear instructions alone. Clocks are compared only within one GPU snapshot.

Instrumented timing changes are mixed: about +1.02% at 128 and −3.78% at 8192. The 8192 quarter medians drift in both arms; all 100 samples are retained. This is a perturbation report, not an instrumentation performance benefit. No production source is promoted by this diagnostic.
