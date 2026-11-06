# Derived-padding R5: rejected

Four fixed-winner CAAC cells /12 phases /1,600 strict-CUPTI samples compare retained22ffe with aligned SF word clearing plus geometry-derived device row bounds. Original quantizer widths/grid and frozen374 route/tactic contracts remain unchanged. The source pair and all gate receipts were checked before deployment and before/after every phase.

Overall geometric speedup−0.057%; prefill−0.118%. V3 EP/TP16K lose−0.333/−0.164% with tight repeats; initial quantization grows by about2.248µs in each topology. N3U TP32+0.124% falls within repeat spreads0.324/0.260%; N3U TP4096+0.145% has tight0.017/0.058% spreads. All sampled clocks are2032MHz/reason0; all64 quartile windows have samples. No clock changes or sanitizer.

The geometry cleanup does remove the impossible initial-linear zero-store branch (48→45 branches), but V3 K7168/128threads uses40B stack and9LDL/5STL versus control0B; R4 used32B and8/4. Total initial instructions are1832 control /1856 R4 /1840 R5. The dead-branch removal does not offset the added local traffic and small stable end-to-end losses in this bounded screen.

Parent rejected R5. Do not launch the broad24-cell screen or refresh TRT baselines for this unretained source. Both R4/R5 raw evidence stay frozen; compare each only against its own source-paired controls, not as a cross-campaign causal delta.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|V3 EP8|16384|PER-TOKEN|622.340|624.149|624.547|622.197|-0.333%|0.023%|0.064%|
|V3 TP8|16384|PER-TOKEN|1351.785|1354.729|1353.578|1352.073|-0.164%|0.021%|0.085%|
|N3U TP8|32|PER-TOKEN|123.520|123.329|123.008|123.121|+0.124%|0.324%|0.260%|
|N3U TP8|4096|PER-TOKEN|552.227|551.220|551.540|552.131|+0.145%|0.017%|0.058%|

All 12 runtime receipts /32 loaded MoE kernels passed unchanged compile/resource guards. This excludes quantizer resource guarantees. All8 initial-linear ABI output hashes match control;18 exact hole-layout cases/90 changed-routing graph replays and80existing/64direct/256graph/4routed gates passed.
