# FC2 six-warp experiment — rejected

Baseline442d2aa53f68b4640c3ab5118a76f1599ff60d34, C1GPU5/B200, nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, CuTe DSL4.7.1. The isolated compact kernel maps epilogue/TMA/MMA to physical warps0–3/4/5 and reduces FC2 TMA-only CTA size from288 to192 threads. No production edits were made.

**Decision: reject for retention.** All120 paired phase cases and36 native full-output comparisons are byte-exact. Register/thread counts and static instruction counts improve, but adjacent forward/reverse native measurements show no repeatable full-chain gain. Stable NVFP4/T16384 reverse full times are522.785/523.329/523.329us (compact/baseline/compact), effectively neutral. NVFP4/T8192 is slightly slower. MXFP8/mixedT16384 control and candidate timings drift; they do not establish a gain. No N256 timing, broader screen, or new NCU run was justified after rejection.

The120-case exact screen includes six format combinations, N128/N256, one/twoCTA groups, per-token on/off, sub-stage/partial K, M384 tails, invalid-SF poison, fused top-k1 with PDL, and unchanged N16/N64 controls. Source checks preserve allocatorwarp0, the128-thread deallocation cohort, epilogue barrier6, group2 pipeline counts, and markers. GPU5 was verified idle and released.

## Generated-code evidence

| Mode | Arm | FC2 threads | Registers/thread | Static SASS instructions | Local loads/stores |
| :--- | :--- | ---: | ---: | ---: | :--- |
| nvfp4 | baseline | 288 | 110 | 1696 | 0/0 |
| nvfp4 | compact | 192 | 106 | 1616 | 0/0 |
| mxfp8 | baseline | 288 | 114 | 1240 | 0/0 |
| mxfp8 | compact | 192 | 110 | 1224 | 0/0 |
| mxfp4 | baseline | 288 | 114 | 1240 | 0/0 |
| mxfp4 | compact | 192 | 110 | 1224 | 0/0 |

All inspected native arms have zero stack/local storage and no setmaxnreg. NVFP4 FC1 is unchanged at288 threads,80 registers/thread,6016 static SASS instructions in both arms. `SHARED:1024` in cuobjdump is static storage, not the dynamic operand/epilogue footprint; shared-memory layout and pipeline-stage count are unchanged in source. No occupancy benefit is inferred.

## Complete adjacent medians

Microseconds;10 warmups/100 samples,cold-L2 CUDA graph CUPTI. Each row uses actual native top-k8 routing and fixed N128/FC1logicalM512/FC2M256(twoCTA) tactics. FC1 is an unchanged drift control. Isolated phase medians are not additive full-chain evidence. mxfp4 below means mixed MXFP4weights/MXFP8activations.

| Mode | Order | Tokens | Arm | FC1 | FC2 | Full chain |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: |
| nvfp4 | forward | 8192 | baseline | 150.8805 | 91.1690 | 300.1610 |
| nvfp4 | forward | 8192 | compact | 150.5760 | 91.4240 | 300.5450 |
| nvfp4 | forward | 8192 | baseline | 154.1765 | 91.1045 | 300.5290 |
| nvfp4 | forward | 16384 | baseline | 254.7845 | 150.2245 | 524.0970 |
| nvfp4 | forward | 16384 | compact | 264.3045 | 153.7450 | 532.4660 |
| nvfp4 | forward | 16384 | baseline | 262.6250 | 153.7610 | 535.8410 |
| nvfp4 | reverse | 16384 | compact | 256.1290 | 150.8160 | 522.7850 |
| nvfp4 | reverse | 16384 | baseline | 256.8965 | 150.5770 | 523.3290 |
| nvfp4 | reverse | 16384 | compact | 258.5610 | 149.5845 | 523.3290 |
| nvfp4 | reverse | 8192 | compact | 150.9120 | 92.1600 | 300.0650 |
| nvfp4 | reverse | 8192 | baseline | 152.4480 | 91.3125 | 298.9130 |
| nvfp4 | reverse | 8192 | compact | 150.7360 | 91.6165 | 299.5850 |
| mxfp8 | forward | 8192 | baseline | 239.7285 | 149.5040 | 466.2735 |
| mxfp8 | forward | 8192 | compact | 239.2480 | 150.7200 | 465.2810 |
| mxfp8 | forward | 8192 | baseline | 250.2090 | 152.7840 | 452.2575 |
| mxfp8 | forward | 16384 | baseline | 411.1050 | 282.4970 | 797.8585 |
| mxfp8 | forward | 16384 | compact | 412.4815 | 264.1925 | 836.4180 |
| mxfp8 | forward | 16384 | baseline | 407.0885 | 255.8890 | 791.8585 |
| mxfp8 | reverse | 16384 | compact | 410.2900 | 270.1610 | 838.7225 |
| mxfp8 | reverse | 16384 | baseline | 410.8810 | 271.8410 | 809.3300 |
| mxfp8 | reverse | 16384 | compact | 438.6090 | 287.3450 | 804.9625 |
| mxfp8 | reverse | 8192 | compact | 239.4560 | 149.2160 | 461.7935 |
| mxfp8 | reverse | 8192 | baseline | 254.9610 | 153.2005 | 457.1050 |
| mxfp8 | reverse | 8192 | compact | 251.1525 | 152.6880 | 455.0735 |
| mxfp4 | forward | 8192 | baseline | 229.3610 | 131.2320 | 415.8575 |
| mxfp4 | forward | 8192 | compact | 229.2490 | 134.4490 | 416.8010 |
| mxfp4 | forward | 8192 | baseline | 232.1610 | 131.7760 | 416.1290 |
| mxfp4 | forward | 16384 | baseline | 407.6170 | 236.1290 | 761.8265 |
| mxfp4 | forward | 16384 | compact | 420.3690 | 226.1290 | 804.2260 |
| mxfp4 | forward | 16384 | baseline | 415.8090 | 247.3930 | 793.1060 |
| mxfp4 | reverse | 16384 | compact | 406.9290 | 225.5360 | 787.9865 |
| mxfp4 | reverse | 16384 | baseline | 407.0730 | 221.5365 | 793.0425 |
| mxfp4 | reverse | 16384 | compact | 413.0420 | 238.0485 | 821.6185 |
| mxfp4 | reverse | 8192 | compact | 229.6490 | 130.3685 | 416.4970 |
| mxfp4 | reverse | 8192 | baseline | 235.7770 | 134.7525 | 418.1770 |
| mxfp4 | reverse | 8192 | compact | 235.6800 | 136.1445 | 421.5215 |

Every100-sample array, command/source receipt, exact log, source snapshot, PTX/CUBIN, and resource report is preserved under `raw/`. Reproduction and layout rationale: `../../scripts/fc2_roles_experiment/README.md`. No failed numerical case or CUDA error was observed in this experiment.

Archive: `1831695` bytes, SHA256 `2cd5a99209e90187b86d316aca2fae7763feb937560c6b31fe099acbc7b77fe3`.
