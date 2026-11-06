# Same-source SM100f versus SM103a benchmark

This external experiment compares the portable `sm_100f` compilation target (A) with native `sm_103a` (B) on the same SM103 B300 GPUs. It uses HashInfer `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`, package SHA256 `df90d2d0aa8f65881624fef55fe7bcd8e1aa91a1227124796947a45e685cd716`. The production class name does not select the compilation target; the normal B300 trace already contains SM103a code. This is a target comparison, not a missing-SM103 dispatch fix. No repository files are modified.

## Reused benchmark and measurement contract

- `hashinfer/benchmarks/bench_cute_dsl_moe_distributed.py`: H7168/I2048/E256/top8, BF16 activations, canonical NVFP4 weights, runtime unit FP32 alphas and precomputed seeded DeepSeek group routing. Its 13 global token counts are `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`: ten decode points and three prefill points. They are not 13 decode counts.
- Each point freshly runs the unchanged eight-candidate native AUTO catalog. Selection uses 10 hot CUDA-event samples per candidate and rank (three candidate preparations plus six untimed graph replays); score is the maximum rank median, winner is the first minimum. These scores are preserved separately from final performance samples.
- Final performance follows PR #11: three public-forward warmups, then 100 native cold-L2 CUDA-graph CUPTI activity spans. Each sample is the maximum across ranks; report the median of those samples. Full public forward includes runtime alpha copies, input staging, communication, expert compute and output handling. Preparation, routing, compilation, tuning, capture and L2 flushing are outside the activity span. No samples are trimmed.
- Each topology runs A1→B1→B2→A2 serially, with fresh processes and separate tactic/compile/driver/Triton caches for every run and rank. Pool all 200 rank-MAX samples per arm and shape; report EP4 and EP8 separately. Decode retention covers 4–512; 1/2 and all prefill points remain visible. ABBA does not eliminate temporal drift or AUTO selection noise.
- Optional `uniform128` is a separate EP4 row: H6144/I2048/E256/top8, 32 tokens/rank, 128 globally, four tokens/expert. It reuses the committed trace routing/weight fixture and is excluded from the native decode geometric mean.

## Checks and artifact boundaries

`arch_benchmark.py` is CPU-only by default; `--run` enables execution. It verifies the exact package hash and full tested commit (and a clean matching Git checkout when present). It records the four fixture-file identities and helper hashes, verifies them after execution, and never inserts a historical “before” commit.

The worker sets `CUTE_DSL_ARCH` and `CUTE_DSL_KEEP=ptx,cubin` before importing CuTe, asserts the full selected target, and requires SM103 hardware. After timing it performs two eager winner calls, requires finite/repeated BF16 bit equality for every row, and applies the existing independent reference at global T128 (native and optional uniform). Other token counts receive finite/repeated-output checks, not independent-oracle coverage. Cross-run output hashes must also match in final analysis; timed graph replays are not each independently checked.

After the actual winner forward, it selects the exact retained frontend staging specialization. Public forward clears `workspace._staging_inputs`; the export uses `frontend._launch_inputs.staging_inputs`, verifying pointers/dtypes/shapes/strides/devices against the timed input closure. It exports each rank's winning PTX, CUBIN, SASS and resource report. PTX `.target` must match the full target; CUBIN ELF flags must encode the corresponding SM field `(e_flags >> 8) & 0xff`. On the installed CUDA13.2 disassembler, the family-target CUBIN displays `sm_100` while retained PTX declares `sm_100f`; the SM103a arm displays `sm_103a` in both. The audit verifies those exact representations and ELF SM fields separately. The older kernel class name or suffix-stripped helper architecture is insufficient proof.

Exports and reference checks happen after the native CUPTI samples. The benchmark's `wall_seconds` includes this post-timing host work through the wrapper; do not interpret it as pure timing overhead or use it as the GPU performance metric.

The unchanged helper `optimization/export_codegen.py` supplies only its artifact reader. `optimization/summarize_benchmarks.py` supplies the established sample parser and ABBA pooling. The architecture-specific auditor checks target/source/cache/selected-winner provenance in addition to that shared analysis. Logs, raw samples and all generated artifacts remain outside the source repository.

## Commands

From this project directory on the prepared node, use its existing Python environment. `run-arch-study.sh` defaults to a plan and accepts `HASHINFER_ARCH_PYTHON` to choose that environment's Python. The caller owns the exclusive GPU slot. `--run` fails if another GPU compute process is present and stops immediately on a failed trial; require clean child exits and all completion receipts.

```bash
set -euo pipefail
export HASHINFER_ARCH_PYTHON=/path/to/prepared/venv/bin/python
study=/path/to/project/optimization/arch-target-20260925
source_repo=/path/to/current/hashinfer

# CPU-only plan: no output directory reservation or CUDA imports.
bash "$study/run-arch-study.sh" --source "$source_repo" \
  --mode fastsmoke --include-uniform --output /path/to/fresh-smoke

# Separate qualification smoke: one native T128 and one uniform128 point,
# each with the real 3-warmup/100-sample protocol and numerical/binary checks.
bash "$study/run-arch-study.sh" --source "$source_repo" \
  --mode fastsmoke --smoke-target sm_100f --include-uniform \
  --output /path/to/fresh-smoke --run

# Eight native sweeps (104 rows); optional four uniform rows are separate.
bash "$study/run-arch-study.sh" --source "$source_repo" \
  --mode abba --include-uniform --output /path/to/fresh-abba --run
```

Every run directory contains `run.json`, `benchmark.log`, a new `knobs/`, and `rankR/` caches, per-shape winner binaries and `complete.json`. `campaign.json` preserves the order, exact source/helper identity, timestamps and completion state. The architecture auditor is `audit_arch_sweeps.py`; run it on the complete campaign, not a mixture of partial runs. Fastsmoke results are excluded from ABBA comparisons.

The historical PR #11 runtime/dependency installation command is preserved in `optimization/cleanup-20260925/reproduction-final.md`. Current execution must use the newly recorded node/environment instead of claiming that historical node identity. The selected image is explicit `nvcr.io/nvidia/pytorch:26.05-py3`; keep that image's PyTorch 2.12/CUDA13.2 build and CUTLASS DSL4.8.0, with installed CUPTI and `cuobjdump`.

## Preparation state

CPU plans for the two-row smoke and 108-row full campaign passed without CUDA imports or reserving outputs. Ruff, Python syntax and shell syntax checks passed. `arch_benchmark.v1.py` preserves the first checked worker (`c352ddb...`), which failed after timing because it used the cleared workspace staging field. The current worker uses retained frontend launch inputs. The coordinating task owns all GPU launches and their actual results; preparation checks are not benchmark evidence.

## Completed execution

Both checked SM100f smoke rows passed on all four ranks with exact finite BF16 reference equality and source-bound winner exports. Independent audit: `smoke-v2-audit-2.json`. The full12-trial ABBA campaign completed successfully at `/workspace/w4a16-trace-sync-0925/arch-target-20260925/abba-v2`. Independent timing/numerical and generated-code audits passed. [Decision](DECISION.md): keep automatic native targeting; both decode aggregate advantages and the uniform128 advantage reverse by run order, and matching winners show no static instruction reduction. [All27 pooled rows](PERFORMANCE.md), [order/tactic qualifications](final-summary-1.md), [codegen findings](codegen-final-findings.md).

Compiler provenance: the image/Torch runtime uses CUDA13.2 and system cuobjdump/ptxas13.2.78. Retained PTX identifies the DSL bundled NVIDIA NVVM compiler as NVVM23.0.0, CUDA13.4 V13.4.59, PTX9.4. Do not describe this as exclusively CUDA13.2-generated code.

The emitted W4A16 PTX uses `tcgen05.mma.cta_group::2.kind::f16`: packed FP4 weights are decoded to BF16 before MMA. Selecting an architecture target does not change that W4A16 arithmetic contract into a native FP4 MMA path. This is directly observed in the exported uniform128 winner PTX; no performance inference is made from the instruction kind.
