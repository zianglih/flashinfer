Source-private persistent CuTe workspaces

Run `prepare_workspace_cache.py` before a benchmark child imports FlashInfer. It verifies the frozen source receipt and exact native source bytes against a known clean reference, then creates a workspace keyed by HEAD, patch SHA, and all pinned source hashes.

```bash
python3 scripts/generality_audit/prepare_workspace_cache.py \
  --repo /workspace/flashinfer-w4a4-split-dynamic-n/generality-quantizer-ancestor-r1 \
  --native-reference-repo /workspace/flashinfer-w4a4-split-dynamic-n/mx-table-retained-final \
  --source /workspace/flashinfer-w4a4-split-dynamic-n/scripts/generality_audit/generality-quantizer-ancestor-gate-r1/source.json \
  --shared-base /workspace/flashinfer-w4a4-split-dynamic-n/cache/gap-c2-native \
  --namespace-root /workspace/flashinfer-w4a4-split-dynamic-n/cache/source-private \
  --output /workspace/flashinfer-w4a4-split-dynamic-n/logs/cache-namespace-ancestor-r1.json
```

Set `FLASHINFER_WORKSPACE_BASE` to the returned `workspace_base`. Keep the existing per-source `CUTE_DSL_CACHE_DIR` and fresh AUTO behavior. Do not set `FLASHINFER_CUTE_DSL_DISABLE_CACHE=1` for normal benchmark campaigns that should retain compilation artifacts. That flag was used equally in the diagnostic four-arm trace solely to ensure fresh compile-bound PTX/SASS and prevent shared module invalidation.

The helper shares only existing non-`*_cute_dsl` cached modules, the whole generated native-source directory, cubins, and the complete lock directory. Every CuTe object module remains private. Build locks are shared, so compilation of the same operation can serialize across sources without sharing or invalidating its CuTe objects. It never copies or loads AUTO timing caches. A newly needed native module absent from the shared workspace is compiled privately; a later helper invocation can expose a subsequently populated shared module only if no private artifact would be replaced. Existing conflicting files are rejected, not overwritten.

The initial helper incorrectly symlinked individual lock files. The installed FileLock3.29 uses `O_NOFOLLOW` and unlinks each final lock file on release: individual symlinks fail with errno40, and hardlinks would not preserve exclusion across reacquisitions. The corrected helper symlinks only the `tmp` directory, leaving final lock components regular.

The corrected live proof is `evidence/generality-cache-namespace-repair-r2/receipt.json`. It reproduces the original error and verifies three real cross-process contention/reacquisition cycles, private CuTe preservation, and idempotence. Both affected stopped namespaces were repaired; their source identities stayed unchanged. Old bad-link directories were preserved as `tmp-lock-symlinks-before-r2` for inspection. The prior r1 fixture did not exercise FileLock and is insufficient runtime validation.

For an existing legacy namespace, stop its owned jobs and pass `--repair-lock-directory`. The helper admits only the exact previous native-lock symlink pattern; it refuses to move any unrelated regular lock or unknown entry. Newly created namespaces need no repair flag. The helper does not import Torch/FlashInfer or invoke a GPU.

R3 also shares the entire `generated` directory. Sharing only its children left a namespace-specific `-I.../generated` root in native Ninja commands and triggered unnecessary recompilation. The native builder already resolves other source/include/output paths. `JitSpecCuteDsl` does not use `FLASHINFER_GEN_SRC_DIR`; CuTe exports remain private under `cached_ops/*_cute_dsl`. The live inventory found only a native `.h` file plus native export-header symlinks there.

Existing R2 namespaces require stopped owned jobs before `--repair-generated-directory`. The helper checks all legacy generated files against the common tree before preserving the old directory as `generated-before-canonical-r3` and replacing its path with a directory symlink. The migration is explicit; active namespaces must not be rewritten. New namespaces use the canonical root automatically.
