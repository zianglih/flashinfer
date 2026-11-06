# Independent sanitizer evidence audit

Pinned source: `d1767be1f42fdc371f90db4fb06598299ea32845`.
The production sanitizer and GPU controller are unchanged by these helpers.

`contract.py` extracts only pure constants/functions from the tracked script.
`audit_results.py` uses Python's standard library and never initializes CUDA.
`run_remote_audit.py` deploys these CPU helpers under the remote campaign's
`audit/` directory, reads completed raw worker artifacts, and retrieves a hashed
report. Unfinished cases are recorded as pending.

When `transfer-secondary.json` exists, the remote runner includes the sibling
secondary root. The audit validates the mirrored transfer receipt, the locked
pre-transfer pending snapshot, assigned-case ownership, matching preflights and
source, and disjoint GPU UUIDs. Every original case must have at most one
execution receipt across both roots. The original 150-case manifest remains
authoritative; transferred cases are not additional tests.

```sh
python3 api-cleanup-20261028/sanitizer-d1767be1/audit/run_remote_audit.py
# After all 150 cases complete:
python3 api-cleanup-20261028/sanitizer-d1767be1/audit/run_remote_audit.py --complete
```

The auditor checks the 150-node matrix, pinned source/Git hashes, launch receipts,
one clean pytest pass per case, strict sanitizer summaries, owned compiler
options/entries, remaining PTX bytes, native O3 flags/routing symbols, and all
random/skewed eager/graph counts. For each mode/token pair, memcheck and synccheck
must enumerate the same full catalog, and the eight racecheck shards must cover
that catalog exactly once without gaps or duplicates.

## Evidence boundaries

- `--check-tensor-ops no` is the tracked memcheck contract; every owned GEMM
  compilation requests `-g-tmem-access-check`. No cubins are retained, so this
  audit does not independently prove assembled guard instructions.
- The SDK reuses `--keep-ptx` dump filenames across specializations. For example,
  the first completed per-token case records 104 unique GEMM PTX hashes, but its
  final dump directory contains one GEMM PTX file. The initial audit's stronger
  all-dumps-survive assumption was corrected after inspecting the actual files.
  Complete compile hash/options/entry receipts are checked; every remaining
  final PTX dump must match a recorded specialization. Missing overwritten dumps
  are not classified as sanitizer failures and do not trigger reruns.
- This suite checks memory/synchronization behavior on SM103 B300 at one GLM5
  geometry with EP8 emulation. It does not compare numerical outputs, test real
  communication, legacy/non-swap kernels, fused/atomic finalize, 4over6/strict
  quantization, other activation functions, or unfiltered external helpers.

`remote-audit.json` is the latest raw-artifact audit. Its `complete` field remains
false until all 150 cases and all 15 catalog unions pass. The corresponding
`remote-audit-receipt.json` binds the report bytes and helper hashes.

After the complete audit passes, `fetch_core.py` freezes and downloads the exact
raw case logs, JUnit results, worker results, native build flags, and symbol
receipts already checked by the audit. The archive manifest binds every byte to
the final report. Large final PTX files remain in persistent cluster storage;
the manifest retains their exact paths and hashes. Symlink worker aliases are
deduplicated, so the archive contains exactly one result per case.
