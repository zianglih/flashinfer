# Empty BF16 FC1 bulk-drain removal: strict admission

This isolated sibling admits exactly source **`e9a72505b9a742f6069bd9f395ef5672f6fbc55cb36d0862dd211234481d0a23`** from the completed fresh CUDA 13.2 C1 native owner **`250553779d5278c66794abef19696df40297d0767336e2782836298fc0a9074b`**. It preserves the frozen static-FC2 release adapter. No product source application, native import/compile, remote staging or GPU execution was performed for this preparation.

The candidate package is `profiles/cu132-recovery0908b-empty-bulk-drain-compileonly-001/packages/candidate/manifest.json`, SHA `69c03ac98b3ee5455b67298b8472b0a1e2dcf874a34d29d35cd00abd6d4a0071`. It changes only epilogue `604935b5…` → **`b1d82a1df8334c78ca27636924913464ca2be8df1dad31d50add1f48d34e0e70`** on the safe-FC2 source `28a58c2d…`: remove the `if cur_was_linear1` node containing `cp_async_bulk_commit_group()` and `cp_async_bulk_wait_group(0, read=True)`. The complete remaining module AST is identical. This candidate retains the original FC1 accumulator-release position; it does not include the separate `802634…` FC1 release experiment.

`static-fc2-release-empty-bulk-drain-manifest-001.json` pins exactly four C1 base/proposed paths:

| Source | C1 base | Candidate |
|---|---|---|
| `w4a16/frontend.py` | `e9eb9557…` | `2a47141e…` |
| `w4a16/kernel.py` | `e00942e4…` | `2b85c9e3…` |
| `w4a16/communication.py` | absent | `c4497fac…` |
| `w4a16/epilogue.py` | `33b5967c…` | `b1d82a1d…` |

All other source hashes and all four historical source-identity helpers match the owner. Inventory is 1,573 sources / 338 required paths, with communication as the sole addition. Shared decoder utilities, shared split/transform kernel, vendor epilogue and dynamic mainloop remain unchanged. Old `28a58…`, base 512, standalone static, FC1 release, preload and historical seven-path declarations cannot satisfy this declaration.

The resource gate, numerical driver, compiled capture observer, public observer and resource probe are byte-identical to the frozen static-FC2 release adapter. Other runtime files differ only by the exact path/schema/declaration/source-hash and descriptive substitutions recorded in `adaptation-validation.json` and `literal-substitutions.json`. Native stack admission, source admission and compiled-result validation AST are unchanged. Every new runtime object must pass the actual CUDA-function REG 128 / 512-thread / two-transform-group / register-pool 65,536 gate before invocation. Earlier `e2d88…` or `28a58…` validation cannot attest this new source.

## Owner launch plan

These are dry-plan commands. Use them only after the owner installs the exact candidate source, captures its matching preflight, and confirms all previous native-cache writers have ended. The preflight path below is a proposed fresh name; it is not a supplied preflight. Source guards reject an installed `28a58…` checkout.

```bash
EBD=candidates/w4a16_dispatch_decode_reuse512_scoped/provenance512_c1_static_fc2_release_empty_bulk_drain
EBD_PREFLIGHT=logs/cu132-recovery0908b-empty-bulk-drain-preflight-001.json
EBD_OWNER=logs/cu132-recovery0908b-c1-full13-001/stack-manifest.json
EBD_PREFIX=cu132-recovery0908b-empty-bulk-drain
EBD_PYTHON="$(python3 - "$EBD_PREFLIGHT" <<'PYTHON'
import json
from pathlib import Path
import sys
print(json.loads(Path(sys.argv[1]).read_text())['python_executable'])
PYTHON
)"
EBD_TORCHRUN="$(python3 - "$EBD_PREFLIGHT" <<'PYTHON'
import json
from pathlib import Path
import sys
print(json.loads(Path(sys.argv[1]).read_text())['torchrun_path'])
PYTHON
)"
export PATH="$(dirname "$EBD_TORCHRUN"):$PATH"
export FLASHINFER_CUDA_ARCH_LIST=10.3a
unset MEGA_USE_NCU CUTE_DSL_LINEINFO CUTE_DSL_KEEP CUTE_DSL_DUMP_DIR

# Optional first actual-resource probe. It stops before the Mega invocation.
"$EBD_PYTHON" "$EBD/run_validation512.py" \
  --candidate-manifest "$EBD/static-fc2-release-empty-bulk-drain-manifest-001.json" \
  --native-cache-manifest "$EBD_OWNER" --preflight "$EBD_PREFLIGHT" \
  --mode resource-probe --world-size 2 --tile m256n128 --cluster 2 \
  --name "${EBD_PREFIX}-resource-ep2-001"

# Eight public suites, then lifecycle EP1 and EP2, with fail-stop sequencing.
bash "$EBD/run_validation_sequence.sh" "$EBD_PREFLIGHT" "$EBD_OWNER" "$EBD_PREFIX"

# Full13 only after all ten new-source numerical/lifecycle gates pass.
"$EBD_PYTHON" "$EBD/run_catalog16_512.py" "${EBD_PREFIX}-full13-001" \
  --stack-id cuda132-recovery0908b-empty-bulk-drain \
  --preflight "$EBD_PREFLIGHT" --native-cache-manifest "$EBD_OWNER" \
  --candidate-manifest "$EBD/static-fc2-release-empty-bulk-drain-manifest-001.json"
```

For owner-authorized execution, append `--execute` to each selected command, after the dry plans pass; all names must be fresh. The sequence preserves four geometries (M256/N128/C2, M128/N64/C1, M256/N64/C2, M128/N64/C2) at EP1/EP2, then all 16 lifecycle candidates per rank at EP1/EP2. Expected numerical evidence is 120 rank-tests, 192 `(test, layer)` configuration/compiled pairs, and 48 lifecycle candidate-oracle records. The original fixtures, tolerances, graph checks and empty-rank checks are unchanged. Torchrun retains explicit localhost addresses; Python and torchrun need not reside in the same directory.

Full13 preserves fixed CONTROL then independent 16-candidate auto, all 13 token powers of two, EP8 and 100 CUPTI iterations with the original warmup, graph, L2 and split tuning behavior. Preserve 52 raw values, 208 actual split selections, 208 compiled records, 104 auto winners and 13 complete rankings. Only the completed fresh C1 owner's two native caches are eligible for reuse after exact native/source admission; DSL, driver and knob caches are fresh. Native cache inventories are before-only, while source/helper inventories are captured before and after each run. Source equality does not imply native-cache immutability.

## CPU evidence and upload boundary

All **37 CPU tests**, Ruff and shell syntax checks pass; see `cpu-validation.log`. Tests include the unchanged runtime gates and sequence checks, all 21 frozen compile-handoff hashes, candidate-file identity, whole-module AST preservation after the single exact If removal, and the inherited static-subtile mapping proof. `prospective-source-manifest.json` is a computed fingerprint, not an installed-source observation.

`upload-runtime-files.txt` / `.sha256` lists exactly 28 files: 18 existing shared helpers, 9 sibling runtime helpers and this declaration. For staging, exact hash matches may be skipped; create missing paths exclusively and reject any existing mismatch. Do not overwrite original helpers. Repository overlays, packages, caches and newly captured preflight/owner evidence are outside this helper upload inventory and remain under owner control. Tests, the local analyzer, CPU snapshots, documentation and this adapter's handoff inventory need not be uploaded for execution.

The supplied offline N128/N64 codegen evidence reports eight fewer instructions per geometry, unchanged actual REG 128 / STACK 0 / zero local operations, retained producer/dispatch drains and preserved named-barrier/release-publication order. It used production `28a58…` plus a private candidate package. It makes no new-source numerical, runtime resource or performance claim. The full 21-input source/compile handoff remains unchanged.
