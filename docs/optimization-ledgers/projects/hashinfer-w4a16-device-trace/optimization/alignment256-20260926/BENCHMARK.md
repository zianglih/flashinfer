# Alignment256 controlled benchmark

This directory adapts the preserved `optimization/arch-target-20260925` harness for source A versus source B. Both arms compile the normal native `sm_103a` target. No GPU work is launched by generating a plan, and historical architecture-study artifacts remain unchanged.

## Frozen worker and methodology

`alignment_benchmark.py` reuses the exact public-forward worker, tuner wrapper, CUPTI wrapper, winner PTX/CUBIN/SASS export, and untimed output checks. CPU AST checks show the four nested functions `checked_benchmark`, `sample`, `export_winner`, and `checked_timer` are identical to the proven architecture-study worker.

- Full public forward with precomputed routing, runtime FC1/FC2 scales, deterministic top-k combine, and O3.
- Native eight-candidate AUTO selection per rank/shape, with all 10 raw hot selection samples retained separately from final timing.
- Three warmups and 100 cold-L2 CUDA-graph CUPTI samples. Each sample is the first-to-last forward activity span, aggregated by rank MAX before summarization. No trimming.
- Source package digest, individual package-file hashes, benchmark/numerical fixture hashes, and helper hashes bound before and after every sweep.
- Fresh rank-specific CuTe, CUDA-driver and Triton caches, compiler dump directory, and run-specific knob cache. Fresh process per sweep and exclusive GPU use.
- Every selected main-kernel PTX/CUBIN/SASS and resource record retained per rank/shape. Instrumentation remains disabled. Source arms use the same native target.
- Every shape checks finite output and repeated BF16 integer-bit equality; global T128 also checks the independent FP32 reference. Full comparison requires fixture and output hashes to match across A1/B1/B2/A2 at every rank/shape.
- Raw samples, selected knobs, pooled medians, per-run median/MAD/quarter medians, order-specific ratios and same-arm drift remain available. AUTO choices may differ; results compare the full selected policy.

Baseline is clean `cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7`; exact package digest from committed relative paths plus file bytes is `79ab6119a9019177beedaef1b396f9e601f56e2fe5aaad723709e6a98c713ddf`.

## Matrix and resumable ABBA

`matrix.json` proposes three scope/topology groups: native H7168 EP4 and EP8, each with global tokens `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; and uniform H6144 EP4 at `128,4096,8192,16384`. I2048/E256/top-k8 throughout. Root can finalize the matrix before launching; it becomes immutable for that campaign.

Uniform routing extends only the external fixture adapter. It calls the existing routing helper with T/4 tokens/rank, preserving eight distinct experts/token and exactly equal counts across all experts. The original T128 fixture bytes are preserved. The 4K/8K/16K cases add 128/256/512 routes per expert.

The driver orders all scope groups in A1, then all in B1, B2, A2. Thus each group has serial ABBA, while every initial control can be collected before the candidate exists. `--max-trials 1` runs only native EP4 A1; omit it to run all available A1 groups. No B arm means a clean pause before B1. Subsequent `--resume` accepts an added B manifest but rejects changes to an existing arm, matrix, helpers, image, output path or completed receipt.

Remote `arms.json` schema (paths must point to remote clean checkouts or verified source archives):

```json
{
  "A": {
    "source": "/absolute/remote/before",
    "commit": "cd7cc07c02300553ef9b8e6af0a4044f0b5dc8a7",
    "package_sha256": "79ab6119a9019177beedaef1b396f9e601f56e2fe5aaad723709e6a98c713ddf"
  }
}
```

Add B with the same schema after its source is committed and pinned. The driver checks clean tracked status when `.git` exists. Archive-only sources bind every package/fixture byte to the explicit full commit attestation.

Run from the supplied remote helper directory, preserving siblings `../export_codegen.py` and `../arch-target-20260925/{arch_benchmark.py,run_arch_study.py}`:

```bash
/path/to/venv/bin/python -B run_alignment_study.py \
  --arms arms.json --matrix matrix.json --output /absolute/remote/results \
  --max-trials 1 --run

# Add the candidate B entry, then resume. Already completed controls are audited.
/path/to/venv/bin/python -B run_alignment_study.py \
  --arms arms.json --matrix matrix.json --output /absolute/remote/results \
  --resume --run
```

`matrix-smoke.json` is a separate T128 native EP4 compile/provenance smoke plan. If used, keep its output separate and exclude it from final performance evidence.

## Offline audit

`audit_alignment_sweeps.py` reuses the prior native codegen/tuning/source audit with source-arm and matrix support. Local `arms` paths may differ from the remote receipts but their identities must match byte for byte.

```bash
python3 -B audit_alignment_sweeps.py \
  --arms arms-local.json --campaign /absolute/local/downloaded-results \
  --output-prefix audit-1
```

Use `--partial` to audit a completed A1 prefix; the report explicitly does not claim an ABBA comparison or retention decision. Output names are exclusive-create to keep prior evidence immutable. A full report rejects failed, active, overlapping or reordered sweeps, wrong native targets, altered cache paths, missing hot/cold samples, mismatched winner bindings, or unequal cross-arm outputs.

Partial failure is retained rather than resumed into a failed trial directory. Diagnose first and start a separately named campaign; clean completed-prefix pauses are the supported continuation mechanism.

## Current status

CPU plan generation, source identity, syntax, serial ordering, unchanged timed wrapper ASTs and uniform route balance pass (`harness-cpu-checks.json`). GPU execution, transfers and publication belong to the parent task. No numerical or performance result is asserted by this preparation note.

## Native 256-bit codegen audit

After the source/timing/output audit passes for an immutable downloaded campaign snapshot:

```bash
python3 -B compare_alignment_codegen.py \
  --campaign /absolute/local/downloaded-results --audit audit-1.json \
  --output-prefix codegen-1
```

This separately identifies the reducer's eight BF16 route loads by their exact hidden-row stride in PTX and SASS, verifies its output-store width, and normalizes memory-instruction counts to 16 output BF16 values per lane. Thus existing FC1 `STG.256` and routing-score vector loads cannot be mistaken for the combine change. Per-export register/stack/local metadata and LDL/STL counts remain visible. Whole-kernel/resource deltas are produced only when topology, rank, shape, selected tactic, resolved config and staging ABI match; changed AUTO winners are explicit unmatched pairs.

The normalization is an equal-output-work static estimate, not a measurement of dynamic instruction count or occupancy. The arithmetic span excludes addressing before the first route load and loop progression after the store. Parser qualification in `codegen-parser-cpu-checks.json` uses historical SM103a examples only and is not current-candidate evidence.
