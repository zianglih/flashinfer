# Held task-or-terminal CLC trial

Preparation only: no primary/source install, compilation, GPU work, numerical check, saved-result validator, or timing run. The root chooses the baseline after the tight-row outcome: retained tight-row4cf or restored c267. Both have the reviewed `clc.py` b2b7 bytes. Source/install/preflight/native/capacity receipts and the whole CLC BEFORE proof/result are required inputs, currently unbound.

Only the exact reviewed `clc.py` b2b7→882d patch e8662a2a is admitted. The association checks its exact unified diff, AST equality outside `run`, equal full source inventories except that one file, and equal helper/required-path declarations. No kernel AST restriction or init-cleanup exception is added. The prior closed capacity association is consumed with its actual source and six original capacity receipts. Three new representative native comparisons must show actual dispatch/finish instructions, encodings, resources, configuration, compile flags, and fixed launches unchanged. Compute codegen is reviewed separately. Historical native results retain their real source IDs; do not relabel a 57e2/4cf result as c267 if the baseline is restored. Any required prior association linking a control to the selected baseline must be explicit before launch.

Use `V=candidates/w4a16_central_refactor/task_or_terminal_validation`. `native-controls-template.json` preserves the existing three fixture configurations and leaves observed BEFORE/result/output pins empty. Set the actual SOURCE, SOURCE_SHA, PREFLIGHT, PREFLIGHT_SHA, NATIVE_ENV, NATIVE_ENV_SHA, NATIVE_INVENTORY, NATIVE_SHA and fresh NATIVE_PREFIX (`profiles/...`) variables, then run:

```sh
bash "$V/run_three_native.sh"
```

This calls the unchanged central `validation/native_v2/capture.py` sequentially: small C1 H256/I256/E4/topk2/cap64/EP1/no-lineinfo, then N64/N128 C2 H7168/I2048/E256/topk8/cap512/EP8/lineinfo. All are CLC/bundle1/epi/F4/S2. Compare with the existing ownership `compare_native.py`; use the existing source/native/idle closure. Do not add a default native or timing cohort.

After actual native review and a passed bound `transport-association-template.json`, reuse the same numerical arguments and original cohort:

```sh
/usr/bin/python3 -B "$V/numerical/run_reference_tests.py" \
  --source-manifest "$SOURCE" --source-manifest-sha256 "$SOURCE_SHA" \
  --preflight "$PREFLIGHT" --preflight-sha256 "$PREFLIGHT_SHA" \
  --native-environment "$NATIVE_ENV" --native-environment-sha256 "$NATIVE_ENV_SHA" \
  --native-inventory "$NATIVE_INVENTORY" --native-sha256 "$NATIVE_SHA" \
  --install-receipt "$INSTALL_RECEIPT" --install-receipt-sha256 "$INSTALL_SHA" \
  --native-closure "$NATIVE_CLOSURE" --native-closure-sha256 "$NATIVE_CLOSURE_SHA" \
  --transport-association "$ASSOCIATION" --transport-association-sha256 "$ASSOCIATION_SHA" \
  "${SIX_OCCUPANCY_ARGUMENTS[@]}" --name "$NUMERICAL_NAME"
/usr/bin/python3 -B "$V/numerical/close_numerical.py" --name "$NUMERICAL_NAME"
```

Nine numerical helpers, including the complete runner, original cases/oracles/tolerances and actual three-symbol/storage observers, are byte-exact tight-row copies. Their sibling imports and hash declarations require this same-depth layout. Only transport admission changes. Expected completion remains the observed 11 rank-tests/41 objects across four jobs; no passed-case rerun. Original saved-record validation runs once per job; closure consumes its saved summary. The native cache must already contain its required runtime modules; the historical strict prelaunch/numerical inventory policy is unchanged.

After true numerical closure, bind the selected completed whole BEFORE (all current columns; no baseline validator rerun) and run the existing CLC8/full13/AUTO100 invocation:

```sh
/usr/bin/python3 -B "$V/performance_clc/run_auto_prepared.py" \
  --source-manifest "$SOURCE" --source-manifest-sha256 "$SOURCE_SHA" \
  --preflight "$PREFLIGHT" --preflight-sha256 "$PREFLIGHT_SHA" \
  --native-environment "$NATIVE_ENV" --native-environment-sha256 "$NATIVE_ENV_SHA" \
  --native-inventory "$NATIVE_INVENTORY" --native-sha256 "$NATIVE_SHA" \
  --validation-completion "$NUMERICAL_COMPLETION" --validation-completion-sha256 "$NUMERICAL_COMPLETION_SHA" \
  --experimental-before-reconstruction "$BEFORE_PROOF" --experimental-before-reconstruction-sha256 "$BEFORE_PROOF_SHA" \
  --experimental-before-result "$BEFORE_RESULT" --experimental-before-result-sha256 "$BEFORE_RESULT_SHA" \
  --name "$AUTO_NAME"
/usr/bin/python3 -B "$V/performance_clc/close_auto.py" --name "$AUTO_NAME"
```

The 12 performance observer/catalog/scoring/timing/closure helpers are byte-exact copies; only the direct driver and reader's trial identity/BEFORE bindings change. The eight explicit CLC candidates, distinct F4/F8 transport batches, effective compute epilogue batches `[1,1]`, S2, CUDA13.2, full graph invocation and original result/sample/resource/ranking block are preserved. No public catalog or runtime kernel knob changes.

After true completion, closure and download, run the saved reader exactly once:

```sh
python3 "$V/readers/read_clc.py" --name "$AUTO_NAME" --output "$FRESH_RECONSTRUCTION" \
  --invocation-sha256 "$INVOCATION_SHA" --execution-sha256 "$EXECUTION_SHA" \
  --closure-sha256 "$AUTO_CLOSURE_SHA" \
  --numerical-completion "$NUMERICAL_COMPLETION" --numerical-completion-sha256 "$NUMERICAL_COMPLETION_SHA"
```

It takes BEFORE pins from the actual driver invocation and preserves all 13 whole-run rows, retaining the 8–4096 ten-row comparison. No baseline/default rerun, split run, or row replacement is included. The helper map is intentionally unbound: add the actual source declaration and runtime association/evidence files to a separate stage map before using existing `validation/stage_runtime.py`. Existing packages remain unchanged.
