# Scheduler replay input-hash boundary

The frozen replay field `input_sha256` hashes the common **base** activation tensor `x0` and base routing weights `w0` for each configuration. These hashes are intentionally identical across that configuration's replay iterations and scheduler/PDL selections. They are not per-replay hashes of the mutated inputs, and `weights` here means routing weights, not expert weight tensors.

The hash-bound helper deterministically mutates the actual inputs before every graph replay: it rolls the activation bytes by `iteration + 1` rows, multiplies the base routing weights by `0.5 + iteration / 8`, and reassigns expert IDs. Iterations 0 and 1 use different local expert patterns; iteration 2 assigns only non-local experts and asserts zero live tiles and zero output. Each of the six scheduler/PDL choices sees the same mutation for its configuration and iteration. Exact output comparisons and output hashes are per replay.

No frozen helper, raw result, GPU gate or source receipt changed to make this clarification. The validator received a comment only; its full program AST is unchanged.

The parent independently reviewed the original 416-line validator and frozen R5 helper, finding no blocker in source/promotion binding, the 68-case JUnit checks, 72 grouped replay cases, compiled scheduler/K coverage, or saved-versus-forwarded native observer checks. This records that review, without attributing a second review of the comment-only version.
