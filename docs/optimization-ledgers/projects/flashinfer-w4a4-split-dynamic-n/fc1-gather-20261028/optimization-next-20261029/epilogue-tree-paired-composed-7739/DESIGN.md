# Paired TMEM completion plus ternary absmax

Unstaged review: `flashinfer-swap-absmax-tree-review`, base77391e28. Frozen combined kernel413c92b951fd426540f07446869b3e055733e126ae254ed7a2295f262d72ccd0.

The combined source copies the qualified paired-six-wait3326ba09 module, replacing only `_absmax` with the isolated ternary helper. AST equality covers all four modified functions: the transpose, scale-pack transpose, token-group caller and absmax. The other513 manifest files exactly match7739. Both component snapshots, their original measured evidence and old source copies remain untouched. Scoped precommit passed.

GPU qualification uses the existing39-case exact suite and executable resource guard. Both arms are fresh: retained7739 control onGPU0, then combined candidate onGPU3 against the captured matching control signatures. Existing wideM512/K8 local storage is an explicit baseline bound, not silently classified as zero-local. The helper checks before returning each compiled callable, so resource growth blocks its first owned-kernel launch. Same persistent native/DSL caches and stable complete data symlink are retained. No timings or sanitizer.

The first deployment exceeded the remote shell argument limit before it executed. Its failure receipt is preserved. The unchanged payload was then transferred in individually hash-verified chunks and assembled before execution. Full514-file source verification passed remotely before launching the gate; actual remote Git parent1b0 plus source patch is recorded separately from logical7739.

No performance or retention claim follows from this qualification. The isolated tree screen remains b139/abd55, and the standalone paired-six-wait screen is independently owned. Combined-source performance requires separate authorization after this gate passes.
