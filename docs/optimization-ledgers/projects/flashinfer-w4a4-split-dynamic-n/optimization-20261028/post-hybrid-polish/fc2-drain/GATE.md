# FC2 terminal drain qualification

Retained base `61c2c367009340ca0ed218511ed9382512860f1b`; candidate kernel SHA256 `9e369972a734de766fd9d8005b83425e64705a1b0cae4e03f49b7b0ce00ca632`. Source remains unstaged and frozen in `flashinfer-fc2-drain-review`.

**Passed:** 256 paired byte-exact changing-route CUDA graph replays. Four input formats (NVFP4, per-token NVFP4, MXFP4x8, MXFP8), static/CLC, PDL off/on, one/two CTA, actual N256 overlapping accumulator windows, N128/N256 route tiles. Routing includes empty/reactivated/skewed/full and below/at/above 16/32/64-row boundaries. Valid FC1 payload/scales, per-token quantized intermediate/scales, FC2 payload and final output match control. Owned padding is recorded, not asserted as a public contract.

All 16 FC1 instruction streams and resources are identical. All 16 FC2 cases preserve registers, local/uniform spill counts, operand stages and output staging. These gates realize 64-token/two-stage bulk storage; the 32-token case is covered by the source predicate proof, not a fresh runtime gate.

| Config | Format | CTA | Overlap | Non-NOP delta | Branch delta |
|---:|---|---:|---|---:|---:|
| 3 | MXFP4x8 | 1 | False | -1…+1 | +1…+1 |
| 4 | NVFP4 | 2 | False | +1…+3 | +1…+1 |
| 5 | PER-TOKEN | 2 | True | +9…+9 | +2…+2 |
| 6 | MXFP8 | 2 | False | +1…+3 | +1…+1 |

Static checks: full-module AST comparison proves only the terminal two statements gained the guard; 1,544 forward/reverse routed-count cases establish that `valid_tokens >= tokens` is exactly equivalent to issuing at least one TMA group. Scoped pre-commit and `git diff --check` pass.

Evidence: `evidence/gate/{quick-gpu6,formats-gpu6}/` preserves source-bound commands, GPU UUID, logs, replay hashes, PTX, cubins, SASS and resources. All 289 downloaded files match `evidence-verification.json`. Archive SHA256: `0e2578adbace2326b8945a12457d810616cd6108d2587148b9a23534089408bc`. Existing CUDA 13.2 B300 environment and persistent native compilation caches are reused. No sanitizer, autotuning or external-baseline rerun.

GPU 6 is released. Runtime performance is a separate root-owned screen; these correctness/codegen results do not establish a speedup.

## Screen interpretation

The frozen four-token screen has 112 scaled cells. All 56 decode cells at 4/64 tokens have routed N below 128 and do not instantiate this bulk path. TP V41F NVFP4/per-token at 4096 also use N64. Those 58 cells are unchanged controls. The remaining 54 prefill cells are bulk eligible. For a 64-row slab, 47 include a sub-slab routed tail; 7 have no skipped terminal drain and only incur its predicate. The exact affected predicate is compiled `bulk_tokens > 0`; realized screen compilation metadata should confirm output-storage geometry. `affected-cells.json` binds the frozen winner files, selected tactics, and routing histograms.
