# Prepared ownership-port helper (CPU only)

`prepare_owned_trace_port.py` prepares a new worktree or audits an existing port. It never edits its selected source, an existing output worktree, a retention/source manifest, a GPU queue, or the primary checkout. Writing requires an explicit source digest. Output must be under this effort's `optimization/`; both source Git directories must belong to this effort. No CUDA libraries are imported.

**This is port preparation, not retention or device validation.** R1/Store16 is still the retained parent. Store32's rejection is unchanged. No-peek and communication decisions remain separate; the helper selects no optimization itself.

## What it preserves and moves

- It copies the selected implementation of `_transform_tile` into `_MegaMixedInput` and the four reachable marker-bearing transport methods plus `dispatch_barrier` into `W4A16TokenComm`. If an owned override already exists, that implementation takes precedence over the shared fallback. Already-subdivided publishers are rejected rather than receiving duplicate ranges.
- Current transform probes/direct waits, TMEM repetition, count-ready polling/publication, payload staging, NB11 participants, and all other owned kernel members stay unchanged. Source copying preserves tracked files plus untracked package Python modules. It adds no documentation-guide changes.
- `_iket` name tokens are normalized to the owned `iket` import without changing strings/comments. Required helper imports are explicit and limited to referenced globals. Existing helpers/layout/finish/return primitives remain inherited.
- Three flat, warp-uniform dispatch subsections bracket existing statements: `dispatch_wait_local_route_counts`, `dispatch_publish_expert_counts`, and `dispatch_wait_input_publication`. Their predicate is CTA0 and dispatch-relative warp0; no lane/expert predicate surrounds markers. The last range includes post-publication NB10 and complete NVLink/global publication of input payload plus route/count metadata. The existing outer range remains unchanged.
- The shared grouped helper, vendor `token_comm.py`, and vendor `iket_compat.py` are restored byte-for-byte to PR base406bc0d, with fixed SHA256 checks. The owned `hashinfer._compat` import remains. Full restoration does not delegate back to the old divergent pull markers: the owned `dispatch_pull` is selected by the owned dispatch orchestration.

The audit rejects unported algorithm changes elsewhere in either restored shared file, unexpected compatibility-adapter changes, and a selected pull implementation containing legacy nested markers. It checks the copied methods against the selected source AST, allowing only the explicit IKET alias normalization and new publisher ranges. The publisher's marker-stripped AST must match exactly; the other copied methods match full ASTs. Existing owned members and the kernel class containing the chosen store width match exactly. Native code equivalence is **not** inferred from this CPU check.

## Completed preparation checks

`test_owned_trace_port.py` passes seven fixtures: six source-fingerprinted frozen candidates (Store16/32 with and without no-peek, counts_fence, parallel_payload) and an in-memory count-fence/payload/no-peek composition. Rejected cases include store-width drift, NB11 participant drift, lane-divergent markers, removed blocking wait, wrong rank completion, missing helper import, changed protected bytes and an unported vendor algorithm change. Store32 fixtures are structural coverage only; they do not reopen its retention decision.

The actual CPU-only example worktree is `optimization/ownership-port-test-r1-v2`, from frozen Store16 source SHA256 `7a48709ed07bc8496908625b921927b04dbcca495d7a3b1ced9a7bd28d072234`. Its five-file ownership delta passes the read-only audit and `git diff --check`; all three protected files have zero diff against406bc0d. Primary remains untouched. The earlier `ownership-port-test-r1` is a preserved helper-development fixture, superseded by v2; neither is retained or GPU tested.

Evidence lives under `optimization/ownership-port-evidence/`: `.plan.json`, `.write.json`, `.audit.json` and `fixtures.json`. Repeated modes append numbered reports instead of overwriting prior evidence. Reports include the selected package digest, Git head, method AST hashes, source/output file hashes, helper hashes, import inventory, protected-file hashes and output Git metadata. Git HEAD alone is not the source identity because selected experiment changes may be uncommitted.

Re-run the CPU fixtures:

```bash
cd /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace
python3 optimization/test_owned_trace_port.py
```

## Apply after the final parent is chosen and authorized

Select an explicit frozen parent; do not substitute the current primary merely because it is convenient. The output path must not exist. Plan mode performs all in-memory port/AST checks and writes only its evidence report:

```bash
python3 optimization/prepare_owned_trace_port.py \
  --source /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/SELECTED_PARENT \
  --output /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/owned-trace-final-port \
  --expected-source-sha256 SELECTED_PARENT_SHA256
```

After authorization to prepare the concrete final port, add `--write-port-test` to the same command. This creates a detached worktree from the selected source HEAD, copies its selected working bytes, applies only the owned port and protected restoration, verifies source bytes stayed unchanged, and audits the result. The flag/report intentionally continues calling it a port test; promotion and GPU qualification are separate decisions. If creation fails midway, the incomplete output is left for inspection and is not reused automatically.

After formatting, run a read-only audit against the same frozen parent:

```bash
python3 optimization/prepare_owned_trace_port.py \
  --source /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/SELECTED_PARENT \
  --output /Users/ziangli/playground/projects/hashinfer-w4a16-device-trace/optimization/owned-trace-final-port \
  --expected-source-sha256 SELECTED_PARENT_SHA256 \
  --audit-existing
```

This tolerates formatting and later guide changes while requiring exact protected bytes, unchanged nonported package Python, exact preserved owned member ASTs, selected method equivalence, full import closure and correct new marker guards. It writes a new audit report but no output source.

Before promotion, update the final marker validators/guide separately, export the uninstrumented final kernel and compare synchronization/decoder code and resources, then run the final retained-stack numerical/lifecycle/synccheck coverage and matched performance. Capture a fresh-autotuned final-winner trace with a new PMTRIG/instrument-point binding audit. See `dispatch-composition-and-ownership.md` and `final-validation.md` for the required boundaries and coverage. No existing trace or native timing is evidence for this newly owned source.
