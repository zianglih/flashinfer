# SF32 two-slot scratch: rejected

The exact/codegen gate passed, but the added planner/admission plumbing and address instructions did not produce a useful gain. This source is not retained or pushed; canonical remains unaffected. No rerun or PR-body update is warranted.

- Frozen source: `c6a8b50e9c51ad1eccf9fb10edc093288ded0ca6f48b78b6ccaecafe41a498a3` on `f175faea1bd97a038fcbf3b51c84c22fd41843ed`; five files, +78/−13.
- CPU proof: 2,004 lifetime/address sequences, 13,500 constructors, 12,600 admission/allocation checks; no stage/K changes in the admitted matrix.
- Exact/codegen gate: 64 comparisons/source, 32 GEMM + 10 Prepare pairs, 362 verified artifact hashes. No spills, registers −1…0, stage/K/UMMA counts unchanged. Eight gated SF32 FC1 cores add 512 bytes; N16 retains two joins, M512/N128 static BAR6 sites fall 32→18. Total static SASS grows 64 instructions. Thirty-three unaffected pairs are strictly identical; one has only the documented descriptor-register permutation.
- Timing: three models × two MX formats × tokens 128/4096/16384, identical saved five-field winners, fresh same-GPU C–A–A–C, 100 cold-L2 samples/run and 10 warmups. No AUTO, TRT, NV or W4A16 rerun. All 79 collected artifact hashes and 7,200 samples independently verified.
- Aggregate: 0.995903× overall, 1.000101× decode, 0.993811× prefill. Several large-prefill controls drift; treat loss magnitudes as observations, not isolated causal estimates. The absence of a useful gain plus implementation cost is sufficient to reject.

| Model | Backend | Tokens | Control C0 / C3 (µs) | Candidate A1 / A2 (µs) | Speedup | C0/C3 |
|---|---|---:|---:|---:|---:|---:|
| v3 | CuteDSL MXFP8 | 128 | 226.7685 / 226.7370 | 226.6580 / 226.7370 | 1.000244× | 1.000139 |
| v3 | CuteDSL MXFP4x8 | 128 | 135.6810 / 135.6645 | 135.5850 / 135.5360 | 1.000828× | 1.000122 |
| v3 | CuteDSL MXFP8 | 4096 | 304.7700 / 304.6890 | 304.9300 / 304.8340 | 0.999500× | 1.000266 |
| v3 | CuteDSL MXFP4x8 | 4096 | 226.0500 / 225.9370 | 225.7930 / 225.7920 | 1.000890× | 1.000500 |
| v3 | CuteDSL MXFP8 | 16384 | 739.2835 / 747.9240 | 779.9080 / 766.1635 | 0.961949× | 0.988447 |
| v3 | CuteDSL MXFP4x8 | 16384 | 735.2350 / 691.2030 | 706.2280 / 717.3470 | 1.001564× | 1.063703 |
| v41-flash | CuteDSL MXFP8 | 128 | 462.6745 / 462.9150 | 462.8355 / 462.4990 | 1.000276× | 0.999480 |
| v41-flash | CuteDSL MXFP4x8 | 128 | 254.6580 / 254.5290 | 254.6100 / 254.5295 | 1.000093× | 1.000507 |
| v41-flash | CuteDSL MXFP8 | 4096 | 585.4750 / 585.4280 | 585.4760 / 585.4595 | 0.999972× | 1.000080 |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 356.6260 / 356.7870 | 356.8990 / 357.0425 | 0.999260× | 0.999549 |
| v41-flash | CuteDSL MXFP8 | 16384 | 993.7020 / 965.7825 | 1010.2800 / 999.9425 | 0.974674× | 1.028909 |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 882.8710 / 899.8945 | 901.4785 / 897.6380 | 0.990869× | 0.981083 |
| kimi-k3 | CuteDSL MXFP8 | 128 | 520.2760 / 520.2600 | 520.5960 / 520.5480 | 0.999416× | 1.000031 |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 289.8900 / 289.9385 | 290.0180 / 289.9540 | 0.999753× | 0.999833 |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 647.8290 / 647.8930 | 647.1250 / 648.2610 | 1.000260× | 0.999901 |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 395.2190 / 395.5550 | 395.3795 / 396.3705 | 0.998768× | 0.999151 |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1380.9380 / 1324.6500 | 1326.4430 / 1355.4665 | 1.008670× | 1.042493 |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1071.3355 / 1121.0005 | 1140.4740 / 1073.7210 | 0.990324× | 0.955696 |

Per-cell speedup is `sqrt(C0*C3/(A1*A2))`; aggregates are geometric means. All raw samples remain under `../sf32-scratch-gate/bounded-screen-evidence/`. Source/codegen proof is `../sf32-scratch-gate/gate-review.json`; CPU proof is `cpu-proof.json`. Remote sources and persistent native/DSL caches are untouched.
