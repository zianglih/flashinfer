# Cleanup native-code gate

The driver is CPU-only unless `--execute` is supplied. It never schedules itself, changes sources, or runs stages concurrently. The parent assigns the exclusive GPU slot.

Frozen inputs:

| Role | Snapshot | Attested commit | Package SHA-256 |
| --- | --- | --- | --- |
| Original x8 baseline | `control` | `002ef1454cbacde09972ed5e2ec7dcfe37e55749` | `c366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff` |
| Measured raw-probe-only x8 | `retained_owned_raw_only` | `5f2094b3b9f7cfbc724d84794632e278331ffd98` | `a0ee8df00da58df7b871ab7a45a93c89df3c5ed221a7cdc3daa0429dba686b8a` |
| Shared-helper cleanup x8 | `retained_shared_raw_only` | `d453eb4f49f0bb38cf828f94c5588ec05d1b5b2c` | `b522ae25090f152c4fda9c364de7fdb256e542eaf1bb4c95c622a4b62670264e` |

Five serial stages run in this order: original N64, measured N64, cleanup N64, measured N128, cleanup N128. Each fixes G512, two-CTA M256/K256, `epi_warps`, atomic scheduling, two scheduler stages and deterministic combine. All use the same EP4 uniform fixture: H6144, I2048, E256, K8, 256 source tokens per rank. The three snapshots' distributed benchmark, trace fixture, numerical tests, and independent reference files must be byte-identical.

Every stage wraps the unchanged `benchmark_checked_final.py` in `export_codegen.py`, with explicit commit/hash attestation for all three sources. It compiles four input ABI variants: Int32/Int64 route IDs × vector/strided hidden inputs. One ABI executes three warmups and 100 cold-L2 CUDA-graph CUPTI samples, followed by finite, repeated-bit-equality, and independent `finite_bf16_bits` reference checks on all four ranks. These timings are diagnostic and excluded from performance comparisons. The other three ABI variants receive generated-code coverage, not an execution claim.

Each stage uses new source-specific output and cache paths. The driver resolves the output root before passing paths to child processes and records both logical and physical paths. A minimal immutable export source manifest is written inside that run; the shared historical `source-manifest.json` is never modified. Successful subprocess exit, source/fixture closure, complete samples and strict output records are required before its `.COMPLETE` receipt is written. Failure logs remain intact and cannot count as successful merely because they contain an earlier completion marker.

The equality gate compares actual CUBIN bytes, complete native SASS instruction text including PCs, and all reported resource fields across all four ABIs at N64 and N128. PTX file equality and full SASS file equality are reported separately; source names/comments are not presumed invariant. No expected instruction deltas are hard-coded. The original N64 → cleaned N64 diagnostic separately reports actual whole/per-K counts, opcode changes, all TRYWAIT sites, the identified TMEM free-slot wait, and out-of-line waits. Static instruction differences do not establish a speedup.

## Run

From the restored optimization directory, first inspect the CPU plan:

```bash
python cleanup-20260925/cleanup_codegen.py \
  --label cleanup-codegen-1 \
  --output /workspace/hashinfer-trace/optimization/results/cleanup-codegen-1
```

In the parent-owned exclusive GPU slot, append `--execute`. The default rendezvous is explicit localhost port 29912. GNU `timeout` limits each stage to 25 minutes. No output overwrite or automatic retry is allowed. Typical runtime depends on cold compilation; allow roughly 15–30 minutes for the five stages, with a hard per-stage bound.

## Collect and audit

Copy only a completed run (logs, receipts, manifests, PTX, CUBIN, SASS, resources, summaries and audit reports). CUDA/CuTe caches and compiler-dump directories are excluded:

```bash
python optimization/cleanup-20260925/collect_cleanup_codegen.py \
  --pod <verified-pod-name> \
  --remote-output /workspace/hashinfer-trace/optimization/results/cleanup-codegen-1 \
  --output optimization/results/cleanup-codegen-1-collected
python optimization/cleanup-20260925/audit_cleanup_codegen.py \
  optimization/results/cleanup-codegen-1-collected \
  --output optimization/results/cleanup-codegen-1-local-audit
```

The collector verifies logical/physical output binding on the remote host and hashes every copied file. The local auditor rechecks those hashes, exact helper identities, source snapshots, exit receipts, and generated artifacts. A failed or partial run is preserved by the parent separately; this collector refuses to package it as completed evidence.

CPU checks: `cpu-codegen-checks-v3/summary.json` records 22 passing plan/protocol checks, including missing ABI, source/commit/cache mismatch, inadequate bit-equality oracle, post-completion failure, failed process receipt, altered PTX, and unsafe collection path rejection. Synthetic test records are explicitly not new GPU results. `codegen-frozen-bundle.json` records the helper/dependency bytes to upload without edits.
