# Epilogue scale hoist on retained b85

Revisit the prior neutral epilogue alpha/norm candidate under the user criterion to remove redundant instructions even at neutral full-chain performance. Both arms use b85eff41 plus identical six-field all-CLC enumeration. Candidate only moves invariant norm_const[0] outside the per-tile loop and each alpha[expert] before the accumulator wait; active arithmetic and global inputs are unchanged.

The kernel-wide PDL wait already precedes both loads. Alpha remains within live-tile handling after expert metadata is known, so no invalid terminal expert access is introduced. Inline epilogue loads are compiled out when dedicated epilogue warps are used. Norm lifetime extends over the loop; alpha lifetime extends through the load/MMA interval, so inspect register and local-memory costs before timing.

Use existing 64-replay source-paired graph gate and PTX/SASS observer (four formats, one/two CTA, N16/N128, inline/overlap, PDL on/off, changing and empty routing). Then same-native-tactic all-CLC CAAC 10/100 cold-L2 public chain across V3/V41/K3, NV initial quantization included. No new upstream tests, no source mutations during measurement.
