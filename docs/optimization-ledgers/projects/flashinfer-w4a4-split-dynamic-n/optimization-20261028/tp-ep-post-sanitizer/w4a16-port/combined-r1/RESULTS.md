# Combined W4A16 tail + FC2 scaling qualification

**PASS.** Source is `fd72759b15b8d417d6c791c0382f90d14262a8e4` plus the two frozen, independent patches. One unstaged kernel in `flashinfer-w4a16-combined-review`; no production test/API/tactic changes.

- Kernel SHA256: `2caee0b467e9017bd53847a6401680810653eb4fdaff4573bc788cacb1a60126`.
- Combined patch SHA256: `65b06adc797db8de3e78763eec3df6761da8019418cea40588c95d1d07de250a`.
- Components: packed `9befca580574f6cff261c7b5aaf5a2d4ce55e491cbed5470a6730c81b2646e69`; tail `4b894db654ac693a9b80c5f8cc60a85da70c43da69a28721b05bc81b5393a1e2`.
- Scoped pre-commit passed before deployment; measured bytes were unchanged by formatting.

Validation on primary GPU3 (B300), `nvcr.io/nvidia/pytorch:26.05-py3`, existing CUDA13.2 runtime with persistent native caches:

- **16 exact cases /112 graph replays:** direct K256 aligned control and K384/K576/K640 tails, one/two CTA, ordinary/CLC and PDL selections, zero/negative-zero/cancellation inputs, adjacent inactive storage poison, and old64/new16 public MoE layout endpoints with changing routes. Uses the existing shared bit-exact oracle and unchanged helperv3 from the independent tail gate.
- **4 existing API tests:** functional/wrapper × old64/new16 weight layouts passed with zero failures/skips.
- **24 owned codegen pairs against tail-only:**8 FC1 instruction streams identical; all MMA instruction-site counts and register declarations unchanged. Both local and uniform spill/fill counts remain zero. FC2 retains the hoisted paired alpha multiply.
- The larger packed gate separately covers route tiles8/16/32/64/128/192 and PDL/CLC combinations; see `../packed-fc2-r1/RESULTS.md`. This combined subset is an interaction gate, not a repeated full tactic matrix.
- The independent tail gate preserves its initial helper failures and unsupported forced-static control IR failures under `../../w4a16-tail/`. Combined validation uses supported native dynamic-N configurations only; it does not qualify the forced-static path. No sanitizer was repeated.

Raw API result:
```text
4 passed, 220 warnings in 10.69s
```

Raw exact outputs: `evidence/exact.log`; codegen and per-case receipts: `evidence/exact/`; command/env/source checks: `evidence/status.json`. All349 pinned source hashes (including the existing W4A16 oracle) were verified before and after both phases.

Source-bound `evidence/GATE.json` SHA256 `7386502be3b2284d5413c11351b6c990205d2d9b668eebc1d8f0be44070f580b`. Archive `evidence.tar.gz` SHA256 `a19227b9189639c9bf925d9989dda1ec250b57286bc4a6e0a7a61575ce67924f`:118 files verified by `evidence-verification.json`.

GPU3 was explicitly released after completion. Independent/combined performance measurements are owned by the shared `w4a16-recent-ports` runner; no timing claim is made by this exact/codegen gate.

Report correction: the frozen gate receipt classified FC1 alignment using FC2 K. the independent `../../w4a16-tail/combined-independent-audit.json` supplies actual reduction dimensions (FC1 H, FC2 K): FC1 cases27/29/31/33 are aligned at K256/512. The original receipt remains immutable; exact, SASS-identity, MMA-count and resource proofs are unaffected.
