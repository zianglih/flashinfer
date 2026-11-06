# Direct FC1 SF publication: initial NV tradeoff

Frozen442d2aa53f68b4640c3ab5118a76f1599ff60d34, C1GPU5, B200, nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2/CuTe DSL4.7.1. Replacementdevboxfi-w4a4-pipeline-1025 uses the candidate442 cache environment from scripts/recovery442/env_candidate.sh. No production edits.

One short-K smoke plus8 paired NVFP4 checks pass (K64/384/512/7168, quantized and per-token output, logicalM512/N128,twoCTA, poisoned SF guard row, route/channel/Ktails). All12 native arms are paired byte-exact on final output. No SF32/all-format matrix has run yet.

**Result: tradeoff, no retention.** NV8K full chain regresses in both orders (about2.3–2.6%), while16K improves about1.3–2.1% with some control drift. FC1 at8K regresses about5%; reverse16K FC1 improves about2.6%. This does not justify a uniform loader replacement or shape-threshold branch. Further work requires a concrete overlap mechanism or profiling, not all-format validation of this initial candidate.

Codegen confirms intended publication removal. NativeNVFP4FC1 remains80 registers/thread with no local spills. SF LDGSTS sites fall4→0, LDG.E.128sites increase4→5, STSsites2→6, and barrier try-waitsites50→38. K384 lowers SF reads toLDG.E.64 (legal8-byte vectors); K64 uses4-byte loads. Per-tokenK7168 stays111 registers in both arms, without spills. FC2 generated resources/instructions are unchanged. Complete CUBIN/PTX and raw resource/instruction reports are archived.

## Adjacent native medians

Microseconds; actualnative top-k8routing,32localexperts, hidden7168/intermediate2048, fixedN128/FC1logicalM512/FC2M256(twoCTA).10warmups/100samples,cold-L2 graphCUPTI. FC2 is an unchanged driftcontrol. Isolated phases are not additive full-chain evidence.

| Order | Tokens | Arm | FC1 | FC2 | Full |
| :--- | ---: | :--- | ---: | ---: | ---: |
| forward | 8192 | baseline | 150.7525 | 91.0405 | 300.0330 |
| forward | 8192 | direct | 158.4165 | 91.2315 | 307.0725 |
| forward | 8192 | baseline | 150.3845 | 91.1040 | 300.2885 |
| forward | 16384 | baseline | 256.5125 | 153.5360 | 523.5370 |
| forward | 16384 | direct | 256.2730 | 154.8480 | 516.8980 |
| forward | 16384 | baseline | 259.6165 | 163.3445 | 525.0095 |
| reverse | 16384 | direct | 247.6165 | 152.9445 | 518.7690 |
| reverse | 16384 | baseline | 256.2410 | 154.0965 | 530.2415 |
| reverse | 16384 | direct | 251.4730 | 151.7440 | 519.1530 |
| reverse | 8192 | direct | 158.7520 | 91.9200 | 306.3850 |
| reverse | 8192 | baseline | 150.6890 | 91.3930 | 298.6725 |
| reverse | 8192 | direct | 158.0485 | 91.5360 | 306.4970 |

Archive: 2205036 bytes, SHA256 `b61c32403cbbe1dff06bb6e5795c7c6c4a7b23c1ab4f437fa372a13e8a1555dd`. All36 arrays contain100samples. Sources, hashes, commands, exact logs, and generated code are in`raw/`. Prototype rationale and synchronization proof: `../../scripts/fc1_sf_register_experiment/README.md`.
