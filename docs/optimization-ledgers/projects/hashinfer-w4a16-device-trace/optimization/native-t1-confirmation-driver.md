# Native T1 confirmation driver

Prepared and CPU-checked only; no GPU command was executed during preparation. The caller owns the exclusive GPU slot.

```bash
cd /workspace/hashinfer-trace/optimization
bash run-native-t1-confirmation.sh --plan native-t1-confirmation-1
bash run-native-t1-confirmation.sh --run native-t1-confirmation-1
```

Omitting `--run` produces only a CPU plan. A unique label is mandatory; existing files/directories/symlinks are refused. Transfer the current `native_t1_confirmation.py` and `run-native-t1-confirmation.sh` plus the existing current dependencies `analyze_native_codegen.py`, `summarize_benchmarks.py`, `export_codegen.py`, `benchmark_checked_v2.py`, `benchmark_checked_final.py`, and `source-manifest.json` beside the three frozen source snapshots. The driver records and rechecks helper fingerprints. In particular, the analyzer must include the `hidden_contiguous` argument added for the all-four-ABI audit.

The exact sequence is two native EP4 H7168/globalT1/capacity1 codegen processes (prototype R2, then owned R2), followed only on success by original002 / ownedR2 / ownedR2 / original002 timing. All six processes use fixed N64/G512/epi, 3 warmups, 100 untrimmed cold-L2 CUDA-graph CUPTI rank-MAX samples, loopback port29894 and GPUs0–3. Codegen durations are excluded from the four timing runs.

The gate checks four ABI keys (Int32/Int64 IDs × vector/strided hidden staging), source/fixture/helper hashes, PTX/cubin fingerprints, H7168/cap1 specialization, absence of profiling instructions, resource equality, and exact CUBIN bytes plus disassembled native instructions. It preserves `codegen-comparison.json` and stops before A1 if identity fails. Every process needs exit0 plus clean benchmark/source closure, finite/repeated outputs and exact fixture/output parity. Native T1 has no independent reference in these existing wrappers; the report explicitly says so.

Frozen source identities:

- Original002: `c366a5e7d7c7aa82034f339a959a058945948381157618bee9139d9005f77eff`.
- Prototype R2: `85f18dc5b772155571b21434184b1cef869cc2b0814039c6292943ab344171ff`.
- Owned R2: `a7001bd59e04b03b372ba4315b3cad8cdcfd7e2db40a96006a5a987c08939e29`, explicitly attested commit `55cd345d57ccc56327966201bd0725767a11593a`.

The legacy wrapper's002 commit field is only a shared base; the prototype's frozen source SHA identifies its actual contents. The owned wrapper uses explicit final commit/hash attestation. No `.git` directory is needed in remote snapshots.

Each process has a20-minute TERM timeout with30-second KILL grace. Any process, validation, or codegen-gate failure preserves logs/artifacts and writes `FAILED.json`; there is no retry or subsequent timing launch. Success writes per-stage receipts, `CODEGEN_GATE.COMPLETE`, ABBA `comparison.json`/`.md`, and final `COMPLETE`. Compiler caches stay inside the unique output; later evidence copies should omit them.

Validation: `bash -n`, Python syntax, and the actual CPU plan pass. `check_native_t1_driver_cpu.py` intercepts every would-be GPU subprocess and verifies five orchestration cases: plan, success, worker failure, codegen identity-gate failure, and missing log closure. The two failures after codegen stop before A1. These synthetic tests validate control flow only; actual native-cap1 CUBIN equality is deliberately left to the real gate. Peer review found no blocker, and its pre-launch gate assertion suggestion is incorporated.
