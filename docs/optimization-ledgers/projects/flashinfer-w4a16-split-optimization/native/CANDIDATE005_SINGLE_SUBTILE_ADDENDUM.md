# Candidate005 N16 single-subtile identity addendum

**PASS: the captured ordinary N16 GPU kernel is unchanged.** This supplements `CANDIDATE005_TMA_PREFIX_REVIEW.md` (original SHA256 `c9ed61e78958a38c572bee6d9a716ccaf10b83e036a8186736a4b9c1e3c69dd6`); the original note and pins are unchanged.

| Capture | Result SHA256 |
|---|---|
|`baseline005-single-subtile-ordinary0-m256-tile-n16`|`ad9eb87972152f14b122ee4002e1b55a56311b0e06c92fe0bc8420ca5900b217`|
|`candidate005-single-subtile-ordinary0-m256-tile-n16`|`18d95c65a28df8a39089a150ab12f9a3f510afe488102ef2bdac72f1a16743de`|

Directories are relative to `native/`. Baseline kernel is b90's `22fefac2a21e2efb5f9b5e0f2b402202dddf8f7136c1c50585105466ae2794a0`; candidate is `1fe29f6f802508034c2fc5daaf7a24271e35bf98a0ca1b052548bfc955f5f97b`; wrapper remains `aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`. Both are compile-only captures of logical M256/N256/K512, ordinary finalize, MMA128/N16/K256, cluster(1,1), static scheduler and PDL disabled. Retained test-file changes do not enter this compilation.

- Raw SASS is byte-exact, including all1640 instruction PCs, opcodes, encodings and scheduling. Shared SHA256: `7ff0bbc86b16c047d0ff7e21baf38015423434f3e38d45ffe2d511a0bd04455a`.
- PTX matches after removing only `.file`/`.loc` source metadata. All23 kernel parameter declarations are identical.
- Resources match: REG128, STACK0, LOCAL0, static SHARED1024, CONSTANT[0]1856 and CONSTANT[2]12. Static SHARED is not a measured total dynamic allocation.
- This directly establishes the one-subtile equivalence for the captured N16 tactic: `(subtile_idx+1)*epiN` is16 when its only subtile is0, matching the previous route-tile threshold16. N8/N32 are source-equivalent by the same one-subtile proof but were not separately native-captured here.

No runtime launch, numerical validation, performance calculation or remote operation was performed by this review. Latency variation on a workload selecting this exact compiled tactic cannot be attributed to changed instructions in its N16 kernel. This does not identify the cause of any measured variation elsewhere in the MoE sequence.
