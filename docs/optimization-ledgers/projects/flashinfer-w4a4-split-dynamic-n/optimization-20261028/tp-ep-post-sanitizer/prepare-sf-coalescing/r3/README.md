# R3: complete unified prepare ownership

Frozen source: `acc93cabb4cbc1703d32225449cea876814493010aae9db465f0cb87c96eaf1a`.
Frozen comparison base: pushed d1767be1. The sole active local review copy is
`flashinfer-prepare-sf-review`; it has advanced to retained 2cfb06afd while
preserving these exact prepare bytes. All source changes remain unstaged.
The frozen remote comparison source remains d1767; see `review-base-update.json`.

R2's 32 rows x 4 lanes ownership, atom-row permutation, SF register preload,
byte copies and padding contracts are unchanged. The host grid now has the
matching work bound `ceil(capacity / rows_per_cta)` as well as the original
hardware thread-capacity bound. Every group is assigned once via grid stride;
the last group masks rows before metadata reads. Unscaled W4A16 still has one
row per CTA and the same grid.

The scaled payload loop uses `unroll=1` explicitly. R2's `unroll_full=False`
was insufficient to prevent compiler expansion; generated-code qualification
will verify this policy rather than assume it. The unscaled full-unroll hint
and default unroll=0 remain unchanged.

The isolated exact gate includes SF16/SF32/FP4/FP8 workload widths through
112 SF words, route tiles16/32/64/128/256, PDL on/off, zero/partial/full and
reactivated counts, poison invalid mappings, exact payload and SF bytes,
logical-invalid SF zeros and physical/tail canaries. A separate 80,016-row
case exceeds the hardware grid bound and exercises persistent grid stride
plus partial CTA ownership. W4A16 generated instructions must remain identical.

Same public fixed-winner CAAC screen as R1/R2 follows a passing gate, on the
two reserved GPU7 devices. No external baseline rerun or new tuning is used.

Exact gate passed: 552 byte/canary graph replays per source, 92 compiled
kernels per source, all 30 unscaled W4A16 instruction streams identical.

Generated code has no local-memory loads/stores or stack spills. The long
scaled payload loops now contain one LDG256/STG256 site: K3 FP8 width uses
40 registers (R2:48), the larger FP8 width48 (R2:62), and V3 NVFP4 SF112
uses56. Small one-iteration paths may be cloned by outer-loop compilation;
static site counts alone are not dynamic instruction counts. See
`codegen-comparison.json` for every specialization.

## Decision: reject

All 12 CAAC cells are complete and all 4,800 raw CUPTI samples, public-call
identities, exact routes, frozen winner caches and medians verified. TP
prefill gains are +1.27% K3 MXFP4x8 / +4.48% V3 W4A4, but decode
regressions span 2.66–21.57%. EP V3 prefill is neutral; K3 EP prefill is
inconclusive because its control passes differ by 6.7%. Full medians and
pass values remain in `perf-table.md` / `perf-summary.json`.

The geometry-correct grid and actual rolled code do not solve useful payload
parallelism on sparse expert tiles. Each valid row now receives four lanes
instead of the original 128, so small active prefixes serialize long row
copies. No model/token-specific bypass or further ownership sweep is retained.
A future design must preserve useful row-copy parallelism while coalescing SF
accesses; merely changing lanes per row or repeating the separate SF traversal
has no demonstrated basis.

The inactive local review clone was removed after preserving its exact patch,
source hashes and all gate/timing evidence. Remote immutable campaign sources
and persistent native compilation caches remain untouched.
