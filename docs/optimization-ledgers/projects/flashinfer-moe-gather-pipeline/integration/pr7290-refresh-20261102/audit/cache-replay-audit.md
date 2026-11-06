# Cache/replay adaptation audit

Source-only review of `payload/harness/import_role_cache.py`, `run_perf.py`, and `observe_benchmark.py`; exact reviewed hashes are in `harness-audit-source-hashes.json`. Runtime import receipts and live pilot execution remain pending.

- 1,424 original stored entries comprise only 968 `CuteDslFusedMoERunner` and 456 `CuteDslFusedMoEW4A16Runner` entries. Candidate translation removes index 8 / index 3 of the respective extras tuple after checking the removed value is zero. Control keys remain unchanged. Key decoding is checked against the original repr, and translated-key collisions are rejected.
- All entry fields other than `key` and `key_fields` are compared exactly, preserving runner, tactic, policy, and recorded evidence. Each measured row is looked up through the current `ManagedAutotuneCache`, validating its runner/tactic/policy against the frozen observer receipt. The importer requires 468 measured rows and all 10 existing `-1` W4 defaults.
- Each role has its own cache copy and key map. `run_perf.py` matches live cache identities against translated original identities, requires every measured lookup to hit, and compares route identities exactly. W4 defaults are resolved to the original default FC1/FC2 tuple and validated against actual launch resolution.
- Fresh profiling is prohibited by both the observer guard and the final zero-count assertion. Cache files are hashed before and after each phase. Missing cache choices cannot silently become accepted defaults: active-measurement lookups assert hits and final selected choices must equal the original choices.
- Strict public timing requires exactly 100 positive finite CUPTI samples after 10 warmups, CUDA graphs and cold L2. Event fallback is explicitly rejected. `flashinfer/testing/utils.py` is byte-identical in both source arms.
- Current config uses CAAC on the same assigned GPU, separate control/candidate native and CuTe caches, source manifests for each exact commit, and the same artifact-download root. Shared downloaded artifacts are compatible because their pinned manifest is unchanged. The inspected source preparation exports exact Git/submodule bytes; no experimental header/ELF copying is present. Actual normal-load native provenance must still be checked in setup/pilot receipts.

Importer hardening is now applied: only control/candidate roles and the two exact known runner names are accepted before migration.

## Pre-timing source-link finding

The setup initially accepted existing `flashinfer/data` symlinks without asserting their targets. Independent review requested exact resolved-target checks. Runtime validation found that the candidate inherited a `data` link into the earlier b17 source copy. The agent reports matching native header bytes, but the path did not satisfy the claimed current-source provenance. No benchmark timing had started. The runtime agent is restoring candidate-local links and repeating normal native warm/load from the corrected paths; final receipts must demonstrate that correction.

## Corrected import/link receipts verified

Both hardened cache imports are now fetched and independently checked. `cache-import-independent.json` reconstructs all 1,424 keys per role using Python AST comparison, checks exact removal of the audited zero-valued offset field only for the candidate, and records hashes. Both imports preserve all 468 measured choices and 10 W4 defaults. Their runtime metadata matches. The corrected symlink receipt resolves all five data directories into each source arm's own root. Native normal-load and pilot receipts remain pending.
