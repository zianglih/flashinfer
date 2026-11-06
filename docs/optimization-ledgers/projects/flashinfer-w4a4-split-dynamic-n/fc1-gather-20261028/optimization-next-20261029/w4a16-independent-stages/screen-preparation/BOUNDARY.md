# Predeclared independent W4 operand-stage screen

- Candidate: frozen `cf78403f1572bb8fe62f9ab5c3056d6d671bb82224631f572d127322887f44e2`, retained `ce4a7d8c2836c0f8a871ebf5cfe87633172360d8` control; no kernel changes after declaration.
- Eight model/topology arms, tokens 8, 256, 4096, 16384: 32 cells. Five N192 cells keep identical stage counts and remain controls; all rows, including losses and repeat spread, are retained.
- Preserve frozen native tactic caches and routing identities. No tuning or new axis; raw `-1` is explicitly expanded to the existing N128 default only for reporting.
- Same GPU C–A–A–C, 10 warmups, 100 strict CUPTI samples, unchanged cold-L2 CUDA graph methodology and all seven observers. Stock clocks and persistent native/CuTe caches remain unchanged.
- Established W4 estimator: arithmetic mean of each arm's two phase medians; percentage is `100 * (mean(C1,C2) / mean(A1,A2) - 1)`. Preserve all four phase medians and raw samples.
- Include per-FC durations and whole-chain end-to-end latency. Kernel durations can overlap through PDL; their sum is not the critical path.
- Stage inventory is not an additive latency claim. A4/B4/D2→A2/B5/D2 does not increase `min(B, A+D)`; it reallocates storage toward direct activation lookahead. Narrow cases can increase matched inventory but add terminal-drain instructions.
- No timing launch until the complete resource and existing exact/graph gate is reviewed.
