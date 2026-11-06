# Kernel and shared pipeline cleanup

Reviewed the six assigned files against PR base `002529e1` and retained head
`33b7e5260132eb4ba2fdfdd97bd71a892f04a481`. Repository AGENTS.md delegates to
CLAUDE.md; its linting, comments, and existing-pattern guidance was followed.
Only `blackwell/moe_swap_ab_kernel.py` is changed by this audit, with two
host-planner expressions simplified. Changes remain unstaged.

- `_accumulator_storage`: remove the redundant overflow disjunct. For positive
  accumulator width, `stages <= floor((capacity - scale_cols) / acc_cols)` already
  guarantees `stages * acc_cols + scale_cols <= capacity`. A nonpositive stage
  count still raises the same error. Constructor and planner geometry give
  positive accumulator widths; no admission rule is relaxed.
- `_configure_pipeline_storage`: compare the available bytes directly with
  `scratch_bytes`. Every `_epilogue_storage` result is divisible by four, so the
  prior byte → Float32-count → byte expression was identical. The Float32 count
  remains stored for the unchanged shared-storage declaration.

Source hashes:

- Before: `b668b2736ea9770e0ca2d45a91f461601953bfaa20f8f807731a641fa20d93d8`.
- After: `14044c6c674ede904f32b29f9d4223b313adfa39798034aecd3a42defea9ae8c`.

`kernel_proof.py` extracts the original/current host functions without importing
CUDA dependencies. It verifies 1,517,440 accumulator cases, including matching
errors, and 262,152 epilogue-storage cases. It also proves the source consists
of exactly the two substitutions and all 28 decorated device-function ASTs are
unchanged. Results are in `kernel-proof.json`. Scoped pre-commit, mypy, Ruff,
formatting, and diff-whitespace checks passed; `kernel-precommit.log` preserves
hook output. Final bytes were rechecked after hooks.

No GPU compilation or timing was run. The source and host-equivalence proof
support unchanged generated device inputs; they are not a new PTX/SASS capture
or performance claim.

## Retained intentionally

- The regular-TMA producer roles, single transaction announcer, shared operand
  lifetime, SF-prefix extents/strides, K96 descriptor handling, terminal CLC
  publication, accumulator-release points and final CTA join are unchanged.
  Their guards encode ownership or hardware legality, not stale versioning.
- `custom_pipeline.py` adds only the useful `defer_sync` behavior. The unused
  `pipeline_init_wait` layout argument and generic pipeline method signatures
  predate this PR; removing them would create unrelated compatibility churn.
- W4A16's empty transform trace hooks are existing caller/subclass extension
  points. Its K-tail, native geometry handoff, scaling order and old/new weight
  layout paths remain unchanged.
- Shared prepare's BF16 versus scaled alignment/validation differs intentionally.
  The recently rejected unsigned-index variant is not reintroduced. Row mapping,
  invalid padding, SF ownership, PDL publication and allocations stay unchanged.
- Finalizer packed multiply/FMA and first-slot signed-zero behavior remain
  intact. Its expanded-layout vector geometry policy is retained; removing its
  guard was an earlier rejected performance experiment.
- Descriptor iterator `hasattr(..., "value")` handles real CuTe/MLIR object
  representations. Optional IKET import compatibility is dependency handling,
  not unpublished kernel-contract versioning.
- No write-only instance fields or truly unused new function arguments were
  found. Apparent unused shared-storage annotations are CuTe struct fields.
  Helpful comments, docs, licenses and inherited behavior were preserved.

## Not applied without codegen evidence

Hoisting repeated descriptor conversions, combining epilogue branches, changing
loop/guard placement, or deleting synchronization can change CuTe lowering,
register liveness and issue order. Existing local experiments demonstrate that
source-level simplification alone does not establish neutrality. None is needed
for this cleanup; they remain possible separately qualified optimization work,
not pending edits in this review.
