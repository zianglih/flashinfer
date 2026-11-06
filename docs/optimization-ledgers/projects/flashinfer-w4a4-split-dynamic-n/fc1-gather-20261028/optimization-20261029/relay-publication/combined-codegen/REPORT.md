# R14 combined candidate code generation and prelaunch register guard

Source `6605aeacc09dfe16232312d17bcf00d320f4e5065e8a5ed34514b9542f6cf372`.
GPU4 K3 EP8 T4096 and N3U TP8 T16384 diagnostics completed; source/patch,
route, frozen winners and persistent cache links verified before and after.
Zero autotuning; CUPTI required. All six FC1/FC2 cubins are retained.

The guard reads executable CUBIN SASS and ELF. It does not trust artifact PTX,
which can be stale on CuTe cache hits. Every callable was guarded synchronously
before its first launch. FC1 guards verified 384 threads, C80/G128/E256 and
initial REG168: required59392 registers fit the reserved64512-register CTA
pool. FC2 guards verified256 threads and no register-reconfiguration instruction.

| FC1 case | R6 → R14 instructions | R6 → R14 STACK | R6 → R14 LDL/STL | R6 → R14 GPU membars |
| --- | ---: | ---: | ---: | ---: |
| K3 EP8 MXFP4x8 T4096 | 2984 → 2680 | 0 → 0 | 0/0 → 0/0 | 29 → 1 |
| N3U TP8 MXFP8 T16384 | 7472 → 6640 | 208 → 0 | 26/46 → 0/0 | 1 → 1 |
| N3U TP8 MXFP4x8 T16384 | 7472 → 6640 | 208 → 0 | 26/46 → 0/0 | 1 → 1 |

FC1 REG168 in all three variants; spills are eliminated in N3U. R12's relay
fence improvement is retained. FC2 resource counts remain REG108 (K3) /110
(N3U), zero stack/spills, with unchanged instruction counts. Dispatch structure
changes affect machine-code register choices, so FC2 binary identity is not
claimed. See `summary.json` and the emitted diffs.

These three guarded variants do not prove legal register reservation for every
possible tactic. The broader test campaign should retain per-compilation
physical-pool guards. Dump flags and diagnostic samples are excluded from
retention timing claims.

Archive SHA256:
`3350b4c0d32bb298510241c52a5c9d584fd191f2d1a2a9732161745913cc3ffb`.
52 manifest entries verified after download. GPU4 was released.
