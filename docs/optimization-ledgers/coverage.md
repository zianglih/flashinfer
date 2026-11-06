# Archive coverage

[Archive overview](README.md)

## Collection

This snapshot collects the surviving local optimization journals and their supporting narrative evidence through 2026-11-06. It covers split and dense W4A16, W4A16 MegaMoE, K3 and mixed-cluster experiments, W4A4/swap-AB dynamic-N, no-standalone-permutation pipelines, finalizers, quantization, routing/top-k, and related instruction/codegen audits.

- Searched project workspaces for ledger and optimization-journal filenames, then inspected the related experiment, candidate, profiling, retention and results directories. Project indexes preserve the original project-relative document names.
- Reconciled the broad ledger-name inventory against the final source selection. The unmatched records were application or training-optimizer ledgers, vendor/test files, dependency requirements, or small receipts whose substantive Markdown notes are included.
- Checked ledger/deletion names in reachable local Git history for the split/dense W4A16 and swap-AB projects, and checked tracked filenames across 14 W4A16-related repositories. No additional deleted authored optimization journal was found by these bounded searches.
- A read-only shared-repository filename search and a bounded search of the retired local `rl` wrapper found no additional authored ledger outside source/vendor clones.

This is a text archive of the located ledgers, not a complete backup of every experiment directory. It does not claim to recover deleted untracked files, unreachable Git objects, retired remote devboxes, or GPU persistent storage. The source-copy ledger records experiments that were deliberately discarded; their surviving decisions remain preserved here.

## Selection and transformations

- Included primary journals, per-experiment READMEs, retained/rejected decisions, benchmark protocols and narrative results, plus small profiling and source audits. Several summaries may describe the same underlying run; document counts are not experiment counts.
- Excluded source checkouts and vendored documentation, raw CSV/JSON measurements, logs, plots, profiler traces, binaries, caches, generated publication copies, and unrelated training/deployment records. The original documents can still refer to these dependencies.
- Excluded the correctness-only C1 authentication/setup record at `flashinfer-moe-gather-pipeline/integration/nvfp4-bitexact-review-20261103/c1/README.md`.
- Deduplicated only byte-identical originals. Every source alias and original SHA-256 remains in the manifest. Differing historical revisions are kept independently.
- Normalized line endings, tabs and trailing whitespace in the copies. Private repository references and a few deployment/account-operation details were omitted where embedded in otherwise relevant notes. The manifest lists the transformations per document; measurements and retention decisions were not rewritten.

The dense W4A16 journal also refers to two companion benchmark helpers removed from its working tree. Their last local source revision is `100e95275d55280c110c66e9a4693b07b86ff4d4`, with paths `benchmarks/bench_dense_w4a16_sm100.py` and `benchmarks/bench_dense_w4a16_sm100_worker.py`; removal was recorded by `c74bdec1d2a959340c8c072a8b67d0b10df07210`. These are source-history pointers, not additional ledger documents.

## Integrity checks

The archival validation checks every copied document and original source alias against its recorded hash, verifies that all generated index links resolve, checks for case-conflicting paths and unexpected files, and scans for credential signatures and private repository URLs. Original source files remain unchanged. Historical GPU tests and benchmarks were not rerun.

To verify the copied documents after checkout, run from this directory:

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path("manifest.json").read_text())
for document in manifest["documents"]:
    payload = Path(document["archive_path"]).read_bytes()
    assert len(payload) == document["archive_bytes"]
    assert hashlib.sha256(payload).hexdigest() == document["archive_sha256"]
print(f"Verified {len(manifest['documents'])} archived documents")
PY
```

The manifest and the original append-only MegaMoE journal exceed the repository's default 500 KiB pre-commit file-size threshold. They are intentional text archival payloads; neither approaches GitHub's 100 MiB file limit. The remaining scoped pre-commit checks apply normally.
