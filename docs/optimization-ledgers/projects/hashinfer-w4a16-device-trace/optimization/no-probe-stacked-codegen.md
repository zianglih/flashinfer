# Probe removal on the retained Store16 parent

The completed native export confirms an instruction reduction on the actual stacked parent, not just the earlier isolated experiment against `002ef145`.

| Matched uninstrumented artifact | Store16 | Store16 + remove both probes | Delta |
|---|---:|---:|---:|
| Whole static native instruction count | 5,112 | 5,072 | −40 |
| FC1 repeated K-loop body | 225 | 215 | −10 |
| FC2 repeated K-loop body | 231 | 217 | −14 |
| TMEM weight stores per K-step | 4 x16 | 4 x16 | unchanged |
| Convert/scale instructions per K-step | 136 | 136 | unchanged |
| REG / STACK / SHARED / LOCAL | 96 / 0 / 1024 / 0 | 96 / 0 / 1024 / 0 | unchanged |
| Whole-function LDL / STL | 0 / 0 | 0 / 0 | unchanged |

This is the Int32-routing, contiguous-vector BF16 input ABI for EP4 H6144/I2048/E256/K8, capacity256/rank, N64/G512/epi, two CTAs per cluster. Manifest configuration, stage metadata, and input ABI match. The analyzer verifies the frozen source file map plus PTX and cubin fingerprints before selecting the timed ABI. PMTRIG instrumentation is disabled. The two decoder loops reverse their native order in the no-probe artifact; phases are identified by their K bounds, not code order.

The complete FC1 opcode delta is two fewer `TRYWAIT`, two fewer branches, one fewer comparison, two fewer `LEA`, one fewer `S2R`, and two fewer `SHF.L.U32`. FC2 has the same reductions plus one fewer `IADD3`, one additional comparison removed, and two fewer `LOP3.LUT`. Conversion, scale arithmetic, shared loads, TMEM stores, and the required fences/arrivals have unchanged per-K opcode counts. Each phase retains two outlined blocking wait helpers, each the same five-opcode retry sequence (`TRYWAIT`, conditional sleep, conditional phase check, retry branch, return branch); there are no hidden spills or added local memory operations.

These are native static counts of repeated loop bodies and their separately inspected wait helpers. They do not imply a fixed dynamic instruction saving on every readiness path or establish a timing benefit. The next-stage probes could alter when readiness is observed and where waiting happens. This specialization also does not establish counts for every AUTO-selected N/group/shape combination.

Source SHA256:

- Store16: `7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234`.
- Store16 + no probes: `2cb93b9d3b679898341b103a5ccb9b19f8cdf7ddd1f0f245f922fab6c9137b64`.

The source difference is confined to the shared `_transform_tile` helper: remove both initial/next readiness probes and their cached-status arguments, while retaining the blocking waits at their existing points. If retained, the separately prepared ownership port must restore the shared file to PR base and move this implementation and its markers into the owned W4A16 subclass, followed by validation of that actual port.

Reproduce the CPU analysis:

```bash
python3 optimization/analyze_native_codegen.py \
  --arms control store16 store16_no_peek-uniform-n64-codegen \
  --output optimization/native-codegen-no-probe-r1-analysis
```

`native-codegen-no-probe-r1-analysis/comparison.json` records all fingerprints, stage metadata, whole opcode histograms, and phase boundaries. `delta-vs-store16.json` records the direct stacked delta and all four wait-helper extracts. Full phase SASS extracts are beside those files. Only the completed rank0 manifest/PTX/cubin/SASS/resource summaries and export log were copied; compiler caches were excluded.
