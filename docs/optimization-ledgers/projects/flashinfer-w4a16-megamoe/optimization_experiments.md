# W4A16 fused MegaMoE optimization experiments

All experiments use the project-local checkout and the dedicated C2 B300 devbox.
Source candidates remain durable in `candidates/`; rejected experiments are
reverted from active source, not deleted from the ledger.

Environment: 8 B300 GPUs, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA toolkit13.2.78,
PyTorch2.12.0a0 nv26.05, CuTe DSL4.7.1. Benchmark provenance logs record exact
source hashes, software/hardware context, commands, clocks, and temperatures.

The primary timing recipe is unchanged `run_benchmark_ep8.sh`: 100 iterations,
CUDA graphs, three warmups, cold L2, distributed split W4A16 plus fused W4A16,
no fused finalize, with the same routing, packed weights, and precision
boundaries. CUDA-event graph timing is the synchronization control. SASS captures
use lineinfo in separate per-shape/per-rank directories; measured A/B runs leave
lineinfo unset.

## Baseline correctness extension

- `logs/baseline_ring_ep1.log`: six tests passed, 22.75s.
- `logs/baseline_ring_ep2.log`: six tests passed per rank, 27.43s /28.04s.
- Added geometries include H1024/I512/M257, exercising B-pipeline wraparound
  and skewed routing across the 128-row CTA /256-row cluster boundaries.
- Baseline timing artifacts are `logs/baseline-cupti-001.*` and
  `logs/baseline-events-001.*`; baseline SASS is retained under
  `profiles/baseline-dsl/`. These are separate evidence scopes.

## Candidate01: vectorized decoded shared stores

Status: retained after full correctness, SASS inspection, primary CUPTI sweep,
and an adjacent restored-baseline control.

Provenance: existing BF16 epilogue aligned register-to-shared CuTe copy pattern,
applied to the exact MMA B tensor view. One x16 decoded NVFP4 block is written
through two eight-BF16 views with 128-bit copy atoms. No lane ownership,
arithmetic, warp count, stage count, or pipeline-arrival change.

- Source artifact: `candidates/01_vector_shared_store.patch`.
- `logs/vector01_ep1.log`: six tests passed, 20.16s.
- `logs/vector01_ep2.log`: six tests passed per rank, 27.79s /27.80s.
- `logs/vector01-cupti-001.*`: primary 100-iteration sweep with lineinfo unset.
- `logs/baseline-restored-after-vector01-cupti-001.*`: adjacent control after
  restoring the baseline kernel only; split control varies by at most 1.4%.
- `profiles/vector01-t4096/rank0/dsl/`: instrumented SASS capture; timing from
  this capture is excluded from the A/B comparison.
- Whole-kernel static instruction count 5305→4581; producer stores 32 STS.U16→
  four STS.128. Whole STS.128 count 8→12. REG 115/LOCAL 0 unchanged, no LDL/STL.
  See `logs/vector01-sass-producer-static.json` and
  `logs/vector01-resources-t4096.log`. Source-correlated line ranges can include
  different inline-assembly locations; whole counts and explicit store opcodes
  provide the comparison, not equivalent selected-range totals.

| Global tokens | Restored baseline Mega ms | Vector01 Mega ms | Speedup | Adjacent baseline split ms | Vector01 split ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.471698 | 0.328674 | 1.435x | 0.083280 | 0.082128 |
| 8 | 2.542316 | 1.657264 | 1.534x | 0.160593 | 0.161393 |
| 32 | 3.620528 | 2.315403 | 1.564x | 0.201761 | 0.199138 |
| 128 | 4.321249 | 2.743250 | 1.575x | 0.231745 | 0.234401 |
| 4096 | 4.364761 | 2.783182 | 1.568x | 0.550886 | 0.551508 |

Despite this improvement, fused MegaMoE remains substantially slower than the
prior split W4A16 path. These rows establish one mechanism, not a competitive
final implementation.

## Existing reference scheduling probe

Prepared profile is exactly the existing MegaMoE `_SWEEP_BASE` plus flag 4 and
`epi_warps`: group_hint 512, epi_flag_batch(2,4), atomic_counter. Geometry stays
BF16 MegaMoE(256,256,64)/(2,1,1)/2CTA. Provenance is retained in
`candidates/reference_schedule_profiles.json`.

`run_reference_schedule_tests.sh` applies that config through a pytest plugin
without changing the original 12 test cases or numerical oracle. It runs only
after syncing the optional-knob constructor fix from eeb25500.

- `logs/vector01-reference-flag4-epi-ep1.log`: six cases passed, 21.90s.
- `logs/vector01-reference-flag4-epi-ep2.log`: six cases passed per rank,
  31.40s /32.57s. Exact per-rank summaries and source hashes are in the log.
- `logs/vector01-reference-flag4-epi-cupti-001.*`: completed 100-iteration
  CUPTI sweep with lineinfo unset, exact source hashes, unchanged split control.

| Global tokens | Vector01 default Mega ms | Vector01 reference schedule Mega ms | Default/reference ratio | Reference schedule split ms |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.328674 | 0.377122 | 0.872x | 0.077936 |
| 8 | 1.657264 | 1.030822 | 1.608x | 0.163441 |
| 32 | 2.315403 | 1.613339 | 1.435x | 0.203297 |
| 128 | 2.743250 | 1.960874 | 1.399x | 0.236546 |
| 4096 | 2.783182 | 2.054267 | 1.355x | 0.553347 |

This is a compound existing schedule profile, not an isolated flag-batching
experiment: group_hint, epi flags, and atomic scheduling all change together.
It improves the 8–4096 token cases here but regresses the 1-token Mega case by
14.7%. No global default has been changed. Fused MegaMoE still trails split
W4A16 by approximately 3.7–8.3x in this profile. The split control is within
2.1% of the earlier vector sweep for 8–4096 tokens; its 1-token row varies by
5.1%, so a final one-token selection merits an adjacent repeat.

After this probe all eight GPU benchmark processes exited. GPU ownership was
returned to the parent for coordinated NCU; no additional candidate was
applied to active source.
