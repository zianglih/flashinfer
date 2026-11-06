# Reproducible payload composition — preparation only

`prepare_payload_composition.py` applies the frozen `parallel_payload` feature relative to frozen Store16 onto an explicit parent. It handles the transport import/method insertion conflict by a verified union, and requires a clean three-way kernel merge. It does not select a parent, retain an experiment, modify the main manifest, edit primary/frozen inputs, or run GPU workloads. Apply this before final ownership-port preparation.

The helper requires all three input package SHA256 values. The payload feature and its Store16 parent must match their original frozen fingerprints. The selected parent is unrestricted by retention policy but must exactly match the supplied hash and pass the structural checks. The caller is responsible for selecting the retained parent first.

The resulting transport has the exact frozen `stage_payload`, `stage_routes`, `dispatch_prep`, and NB11=11 attribute. It replaces the original `stage_inputs`. Every other parent method, including count-ready `sched_warp_pre_init_wait`, remains byte-identical. Import bindings are the exact union of the parent and payload feature, preserving the parent's import origins. The kernel merge adds only the epilogue payload staging/arrival and dispatch route-staging delta; reversing it reproduces the exact parent kernel text. Every other package Python file remains byte-identical, including the vendor publisher, shared transform/probe selection, compatibility shim, and TMEM width outside the payload delta. Unexpected existing payload overrides or changed input staging are rejected for explicit review.

After the parent is selected, replace the parent path/hash and output name below. Omit `--write-source` first to prepare a plan; add it to create the new worktree. The output must not exist and must be inside this effort's `optimization/` directory. Planning and writing produce separate, numbered evidence directories rather than overwriting previous reports.

```sh
python3 optimization/prepare_payload_composition.py \
  --parent optimization/SELECTED_PARENT \
  --parent-sha256 SELECTED_PARENT_SOURCE_SHA256 \
  --feature-sha256 94a939ede3ca316d23cd6aa640a1b0a17035c18aaa54d521b100fdb858d8a49c \
  --feature-parent-sha256 7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234 \
  --output optimization/NEW_CUMULATIVE_CANDIDATE \
  --write-source
```

Each evidence directory contains `audit.json`, `payload-increment.patch`, and **a separate** `manifest-addition.json`. The latter is returned for the parent task to review/merge later; the script never modifies `source-manifest.json`. It records source creation and `prepared_not_retained`/`plan_only`/`cpu_fixture_only` status explicitly. It imports only standard-library AST/Git helpers, whose hashes are included in the audit. The frozen ownership helper is consumed read-only and unchanged.

CPU coverage:

```sh
python3 optimization/test_payload_composition.py
```

Eight source fixtures passed: Store16; count-fence; no probes; count-fence with no probes; either isolated probe removal; and synthetic count-fence with either isolated removal. Their method union matches the earlier `test_owned_trace_port.py` composition fixture. Nine mutations are rejected: participant count, scheduler, publisher, shared-transform, TMEM-width, import-origin, barrier-ID drift, an already composed parent, and unreviewed parent staging.

`payload-composition-cpu-fixture/` exercises the real worktree write path using the frozen `store16_no_peek_counts` parent. It is explicitly **a CPU fixture, not a selected or retained candidate**. Its source hash is `f0082ff0be4709001712f9637bfbf36ba02bc6c068b4d34f867ecf66386772eb`; evidence is in `payload-composition-cpu-fixture-composition-evidence/`. Git metadata, the primary checkout, frozen input snapshots and main manifest were checked unchanged except for registration of this new project-local fixture worktree. No compile, correctness or performance result is implied. The cumulative candidate still needs its own GPU validation and incremental performance comparison against its selected parent.
