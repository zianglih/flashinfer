# W4 tail cutoff qualification

Candidate `cbef9186731e78806884f7fa2ba5aad18f5ece379664cf8d3181d5cd54548c10` is an unstaged 8+/6− change on retained 2b8. `qualification-summary.json` seals the completed gate; performance is separate.

- Fourteen exact calls ran freshly: ten split calls and four Mega calls. Six existing split control calls were reused only after matching the complete 2b8 source inventory and current release-library/Ninja cohort. This yields eight split cases / 24 native pairs plus two Mega pairs.
- Every paired actual register, maximum-thread, local, static-shared and binary-version field is equal. All local memory is zero. Source allocation/layout and launch geometry are unchanged; no new occupancy measurement was introduced.
- Four partial FC2 K640 kernels remove the per-stage ULEA+USHF before the predicate; each loses 3 non-NOP instructions overall. The short-tail FC2 K320 kernel loses 2. Four partial FC1 H384 kernels move one ULEA to invariant setup UIADD3, with unchanged total instruction counts.
- One-stage FC1 H128 has no instruction-count reduction. Its comparison changes `group != 0` to `group != 1` with the matching branch-polarity inversion; all other SASS instructions match. Both ordinary and two-CTA cases pass exactness.
- Full-K split kernels and the all-live partial FC2 I448 kernel are raw PTX/cubin/SASS identical. All eight finalizers are identical. Both shared Mega padded-K executables are also raw identical (96 registers, LOCAL0).
- Static/CLC, one/two CTA, PDL on/off, both gated layouts, SwiGLU/SiTU/ReLU2, short-tail, multistage tail, and all-live partial cases are covered by existing helpers. No repository tests or compiler options were modified.

The initial pilot and continuation evidence remain separate in `qualification/evidence/1793392766283766000/data` and `qualification-extra/evidence/1793393145401734000/data`. Reused controls remain under the original `w4-raw-peek/qualification` archive. Mega evidence is under `mega-qualification/evidence`. There were no numerical or resource failures; the local summary sealer initially asserted raw equality for the affected one-stage FC1s, then documented their actual two-instruction polarity change instead.

The parent-authorized performance configuration is `performance-screen/perf-config.json` (`62239583`): the existing 39 tail-affected cells (V41F/K3/N3U TP, 13 tokens), 33 retention cells after excluding 1/2, same-GPU CAAC, 100 samples per phase and 10 warmups. The argv-size transport failure occurred before remote Python execution; `launch_staged.py` delivered the exact generated launcher in checked chunks. Native performance calls and all 12 measurement helpers remain unchanged.
