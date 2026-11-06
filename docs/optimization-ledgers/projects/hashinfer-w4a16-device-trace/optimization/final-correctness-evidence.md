# Owned R2 final correctness evidence

Final five-suite audit: **PASS**. The actual immutable evidence is in
`results/owned-r2-correctness-snapshot-1`; the full raw tables and audit are
`results/owned-r2-final-correctness-1.md` and `.json`. Accepted actual totals are
26 outer cases, 58 rank pytest passes, 128 strict combinations, 384 collective
reference comparisons and 1,984 collective pairs. All JUnit ranks report one
test, zero failures/errors/skips, exit 0 and unchanged source.

The helpers use only Python standard-library CPU operations. The collector's
remote action is a read-only `kubectl exec` that packages a strict allowlist;
it launches no GPU work or tests. The completed collection contains 191 files,
with archive SHA256 `42ac11eb818f8bc00ed45ad8c898d879bae4eca0e4085377439f1933ac56251e`.

The target is commit `55cd345d57ccc56327966201bd0725767a11593a`, package SHA256
`a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29`.
This is retained R1 + R2 after ownership refactoring, with only TMEM probes
remaining. The parent-owned serial GPU gate completed before collection.

## Collection and audit

The following exact commands completed the collection and audit. Their output
paths now exist and are immutable; use new numbered paths for any later rerun:

```bash
effort=/Users/ziangli/playground/projects/hashinfer-w4a16-device-trace
python3 "$effort/optimization/final_correctness_evidence.py" collect \
  --pod devbox-hashinfer-trace-final-0925-0 \
  --remote-root /data/ziangli/hashinfer-w4a16-device-trace/recovery-20260925/results \
  --output "$effort/optimization/results/owned-r2-correctness-snapshot-1"

python3 "$effort/optimization/final_correctness_evidence.py" audit \
  --snapshot "$effort/optimization/results/owned-r2-correctness-snapshot-1" \
  --source "$effort/optimization/retained_owned_r2" \
  --repository "$effort/hashinfer" \
  --output-prefix "$effort/optimization/results/owned-r2-final-correctness-1"
```

The collector reads these exact directories beneath the remote results root:

```text
owned-r2-final-ep4-1
owned-r2-final-ep8-1
owned-r2-final-tails-1
owned-r2-final-lifecycle-1
owned-r2-final-prestaged-1
```

`--remote-root` defaults to
`/workspace/hashinfer-trace/optimization/results`; an explicit alternate root
must be absolute and contain no `..`. The original default pod is historical.
The active replacement pod and its real persistent results root are explicit
in the command above; `--pod` selects it without changing the historical defaults.

Each collection requires a new output directory. It preserves the selected
archive and a content-hashed manifest. A suite with a passing summary is a
`completed-candidates` snapshot, pending local audit. Missing, malformed or
nonpassing summaries are saved under `partial-or-failed`. This preserves
partial/failure logs without turning them into passing evidence. An early
snapshot remains immutable; collect into a new numbered directory later.
Transfer failures leave the partial archive and a failure receipt.

The allowlist includes plan/summary/collection log, each case's run log and
command, all rank JUnit/provenance files, and strict numerics JSONL/CSV. It does
not descend into pytest temporary/cache directories or copy tensor payloads,
compiler caches, or knob caches. Symlinks and unsafe archive paths are refused.
Audit reports go outside the immutable snapshot and never overwrite an
existing JSON/Markdown report. An incomplete or failed audit exits nonzero;
its report identifies excluded suites rather than claiming a final pass.

## What is checked

- Exact selected outer nodes: three EP4 strict cases, one EP8 strict case,
  ten tails, six lifecycle, six prestaged. Case ordering matches the unchanged
  final-validation driver's suite ordering, not the order of `--node` arguments.
- The local frozen package hash matches both the recorded source and the
  package at the declared tested commit. Selected test files also match that
  commit. The execution plan's test/helper hashes match local audited files;
  every summary field must agree with the corresponding plan.
- Every expected rank has exactly one JUnit test of the correct node/module,
  with zero failures/errors/skips. Per-rank provenance must name the correct
  rank, node and imported package, report pytest exit 0, and confirm unchanged
  source. Collection and command records must select the exact case/rank count.
- The four strict cases each have one initial/completion record, 32 distinct
  compiler/tactic/execution combinations, 96 expected eager/replay reference
  records, and all 496 unique pair records. Merely duplicating rows to reach a
  desired count cannot pass. Numerics JSONL must equal the records in raw logs.
- Every strict comparison is finite BF16 bit equality with zero mismatch or
  nonfinite counts. Every rank's element count, equality, repeat result and
  error metrics are checked. The eight candidate knob dictionaries are read
  from the exact frozen source's pure catalog function without importing CUDA.
- The expected completed totals are checked only after computing them from
  accepted actual evidence: 26 outer cases, 58 rank pytest passes, 128 strict
  combinations, 384 collective reference comparisons and 1,984 collective
  pair comparisons. Collective comparison counts are not multiplied by EP.

The final Markdown report is 6,855 bytes and contains all exact pytest nodes with their raw
per-rank JUnit counts/times and the four raw strict completion counts. The JSON
also preserves raw pytest summary lines, record hashes and comparison details.
The report is small enough to include its raw tables in the PR alongside the
native performance evidence. No sanitizer
coverage is implied, and the non-strict tail/lifecycle/prestaged assertions are
not relabeled as the strict all-tactics reference matrix.

The final-validation plan's historical `declared_base_commit` field may still
be `002ef145`; it is not used as the final source identity. The actual final
package is independently bound to commit `55cd345` above. Source fingerprints
and successful pytest evidence remain distinct from GPU performance and native
IKET point/cubin validation, which have separate collectors.

## CPU preparation evidence

```bash
python3 optimization/test_final_correctness_evidence.py \
  --output optimization/final-correctness-cpu-v3
```

That output already exists and is intentionally not overwritten. Choose a new
suffix for another run. The generated records are explicitly labeled synthetic
and require `audit --synthetic`; they are never final numerical evidence.

`final-correctness-cpu-v3/summary.json` records one complete synthetic fixture
and 17 negative/selection checks. These reject missing rank/suite/phase records,
source/node/tactic mismatch, JUnit failure/skip, nonzero exit, bad closure,
duplicated pairs, failed replay equality, and synthetic evidence presented as
real. The actual remote selector ran locally against synthetic directories to
verify selective copying, cache/tensor exclusion and separate partial storage.
No remote access, pytest execution, or GPU launch was involved. Ruff syntax,
format and unused-name checks also pass.

Prepared helper SHA256:
`6baf1785fde48ee4a718e291d4f02953d766bad25f6cc59b0dde93b6685885ff`.
Current helper SHA256 after explicit replacement-pod selection support:
`682473bba051872ee0900d32707e3b4540090de18aa6e0bbab80914bc8a1785b`.
Test helper SHA256:
`2f1dfd1ee3e8a3aaccfb821b5211160e2d09d54dfd281194a5331a207f19a5ca`.

Progress-only evidence: `results/owned-r2-ep4-progress-audit.json` validates the
three completed strict EP4 cases (12 rank pytest passes; 96 combinations,
288 collective references and 1,488 collective pairs) against the same source.
This does not stand in for the final five-suite immutable snapshot/audit.
Repository-only reproduction commands for the exact selection are in
`final-correctness-reproduction.md`; their shell syntax and expanded 26-node /
58-rank selection pass the CPU check in `final-correctness-reproduction-cpu-v2.json`.
