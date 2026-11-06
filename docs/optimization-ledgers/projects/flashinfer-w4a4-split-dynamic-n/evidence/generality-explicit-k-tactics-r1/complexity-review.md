# Read-only complexity review of the remaining generalized-backend diff

The frozen remaining diff has 686 additions /187 deletions across seven files. The core accounts for370/78; this includes the earlier planner and narrow-two-CTA synchronization work, not only K-tactic plumbing. Compared with retained dea2, the new static planning methods occupy198 lines: accumulator10, operand-byte formula20, metadata17, epilogue scratch8, stage capacity25, K capacity57, automatic K selection61. Device kernel length grows20 lines, and its launch-side `__call__` grows4; the K-tactic patch itself does not change device methods.

## Small worthwhile follow-ups, after candidate performance finishes

1. **Unify initial epilogue reservation with stage fitting.** `_k_stage_capacity` and `_configure_pipeline_storage` both compute the one-operand-stage slack, reserve `_epilogue_storage(...)`, then call `_operand_stage_capacity`. Change the latter's `scratch_bytes` input to `bulk_output_bytes` and do this identical reservation inside it. This retains the SDK-derived stage-byte input in `_configure_pipeline_storage`, the estimated-size assertion, final scratch allocation after the stage count is chosen, and explicit stage-count behavior. It removes roughly10–15 lines and one duplicated resource-policy operation. No new DTO or module is needed.

2. **Use the same minimum-fit admission for default and explicit K.** `can_implement` currently computes base-K scale/TMEM feasibility, then repeats it inside `_k_stage_capacity` for explicit K. Resolve its effective capacity-check depth to4 when the override is None and call the shared helper once. This removes about8–10 lines and makes the minimum-storage rule common. It would add the SMEM minimum-fit check to legacy None admission, so prove all supported default geometries unchanged in the CPU census before adopting it. No selection-policy change is required.

3. **Remove the duplicate outer-shape check in MX canonicalization.** `_canonicalize_mxfp_tactic` repeats the outer tuple/list-length validation done by `_split_moe_tactic`. Recursive list-to-tuple normalization already leaves other values unchanged, so the parser can remain the sole error authority. This is a three-line cleanup with existing malformed-input fixtures.

## Keep as-is

- The two public adapters are intentional signature duplication: public signatures/defaults and docs stay intact, while preparation/validation has exactly one private implementation. Replacing them with `**kwargs`, context variables, partials, or synthetic signatures would weaken the explicitly requested API boundary. Deprecated convenience wrapper bodies are AST-identical to their prior versions.
- The final `_epilogue_storage` call after choosing/requesting the actual stage count is necessary. Its result can differ from the initial reservation when an explicit stage override consumes more storage.
- The actual-SDK operand-size assertion is useful protection against estimator/layout drift; it is not redundant admission.
- Automatic K selection remains needed for legacy/default tactics and standalone FC calls. Removing it just because new autotuning entries carry K would change those paths.
- Repeated two-line geometry arithmetic is simple and currently exact; introducing a geometry object or constructor-driven planning framework would add more structure than it removes.
- Cluster scale publication/arrival/wait is a correctness requirement for narrow two-CTA S2T ownership, not planner scaffolding.

No source edits were made for this review. Current frozen CPU/storage and public-signature evidence remains valid; proposed simplifications need their own equivalence check before any source change.
