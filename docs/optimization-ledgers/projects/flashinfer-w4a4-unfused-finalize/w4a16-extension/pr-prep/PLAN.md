# PR body extension plan

This preparation does not change `PR_BODY.md` or GitHub. The existing body is
saved as `PR_BODY.previous.md`; `../PR_BODY.profile-normalized.md` preserves every
old row but formats the 80 Nsight interval rows to three decimal microseconds,
matching their underlying integer-nanosecond precision (3,407 characters saved).

## Publication evidence boundaries

- Historical W4A4 performance, 44 MoE phase comparisons, 96 standalone cases,
  and 80 Nsight samples remain scoped to commit
  `fff0070cbeefda46e8f3c987a2bdc8e20584f062` and its `combined-v2` overlay.
- The original 30 W4A16 rows remain unchanged **nightly controls** in the old
  120-row CSV. They are not the baseline for the new W4A16 optimization.
- The new W4A16 baseline uses the same pinned nightly package runtime and the
  original PR source at `fff0070c`; its W4A16 host and GEMM files are byte-identical
  to PR base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`. The candidate overlays only
  the final five changed CuTe source files. Do not compare these new rows to
  nightly-control W4A16 latencies from the historical table.
- Both runs use the same image and software versions. The current GPU is the
  same physical GPU 0, UUID `GPU-dc049cc5-49eb-1d1a-96af-89b3807f7972` (root verified).
- Replace the old 22-case native pytest stdout with the new 30-case stdout,
  explicitly saying that it supersedes the original native result and validates
  both W4A4 modes plus W4A16 on the current candidate. Only do this after that
  command completes successfully. Preserve all output from the successful run;
  exclude earlier setup/path failures from the claimed passing run.
- The new expected W4A16 external matrix is 52 pipeline phases (40 small,
  4 production, 8 partial-tile) and 200 standalone cases (192 nonempty plus 8
  zero-token). These are planned counts, **not passed claims yet**. Publish only
  reports whose actual complete/result fields pass.

## Text changes required after final evidence

1. Title and lead describe W4A4 **and W4A16** unfused finalize.
2. The shared `moe_finalize.py` has two compile-time layouts: W4A4 expanded row
   `token * top_k + slot`; W4A16 permuted row read from the nonnegative route map.
   Negative map entries remain masked, index zero is valid, ascending top-k FTZ
   FMA reduction and one BF16 conversion remain the numerical contract.
3. Describe early FC2 dependent launch after the producer's activation wait in
   both kernels. W4A16 moves its old tail hint to the unfused early location;
   its existing tail path remains for fused finalize. All dependent output
   reads remain after the consumer wait.
4. Scope now covers five CuTe files, no C++/benchmark/test upstream changes.
5. Change old "final head" labels to "original W4A4 commit" wherever they refer
   to `fff0070c`; distinguish final shared-helper correctness from historical
   W4A4 timing unless root performs a fresh W4A4 sweep.
6. Keep all original 120 raw benchmark and 80 raw profile rows. New ratio-only
   W4A16 table has 15 rows and two ratios: baseline-unfused/candidate-unfused,
   baseline-fused/candidate-unfused. Include all 45 new native CSV rows.
7. Shared methodology remains simulated EP8, H7168/I2048, top8, 32/256 experts,
   TP1, native wrapper, PDL, graph, cold L2, CUPTI, 10 warmups/100 samples, median,
   one forward sweep, independent tactic cache for each arm/finalize setting.
   Keep `--include-activation-quant`; it is a no-op for BF16 W4A16 inputs.
8. Do not claim the W4A4 Nsight result directly measures W4A16 overlap. The new
   W4A16 end-to-end MoE sweep measures the combined scheduling/finalizer patch.
9. Keep the complete template and draft status, and keep old historical hashes
   labeled with their matching commit. Add new final source/log SHA256 evidence.

## Result helper

`../scripts/summarize_benchmarks.py ARTIFACT_ROOT --output-dir OUTPUT` requires
exactly 15 native W4A16 rows from each of baseline unfused, candidate unfused,
baseline fused; it rejects warnings/errors/fallbacks for review. It emits a JSON
manifest, ratio-only 15-row table, and lossless 45-row native CSV. It imports the
original effort's CSV parser and retains native metric strings unchanged.

## Reproduction design

Keep the existing pinned-nightly package setup. Use `git show COMMIT:path` when
constructing historical/current source overlays so the currently checked-out
source does not change historical reproduction:

- `combined-v2`: three files from `fff0070c` (historical W4A4 candidate).
- `w4a16-baseline`: those three files plus `moe_w4a16.py` and
  `moe_w4a16_kernel.py` from `fff0070c`.
- `w4a16-candidate`: all five final CuTe files from the new pinned head, including
  `moe_finalize.py` instead of `expanded_finalize.py`.
- All overlays share the same unchanged `shared-nightly/flashinfer/jit` path.

Extend the existing external benchmark-only selector patch with
`cutedsl-w4a16`; do not alter workload or timing. Run in order baseline unfused,
candidate unfused, baseline fused, selecting only `--backends cutedsl-w4a16` and
using independent cache files. No candidate-fused sweep is planned or claimed.

The normalized draft leaves about 5,300 characters below GitHub's 65,536-character
body limit. Superseding old native stdout and sharing setup should avoid duplicate
output/code. If still too long, compact repeated prose or losslessly present
hash JSON as CSV; do not remove token-count rows or relabel incomplete evidence.
