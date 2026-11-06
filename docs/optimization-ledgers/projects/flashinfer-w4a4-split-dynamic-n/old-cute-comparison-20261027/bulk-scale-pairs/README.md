# Pair per-token FC2 bulk scaling

Retained and pushed as `7ae6244de4ad60d92b6341f8f04dc73d2b1b0549`, parent
`d02c487a15d0636e902c3f7a5e0bf7cf4a03156d`. The clean canonical commit's
parent-to-head full-index binary diff has SHA256
`7587b61069fcfcc30ed31e204fa963fb52b651500646e1a04b07fd34e0cc9775`, exactly
matching the tested candidate. Commit hooks passed. `retention.json` binds
source, gate, timing and publication evidence.

The +9/−5 change pairs the existing per-token FP32 multiply in the bulk epilogue
using the same packed operation already used for uniform scales. The lane and
register mapping and both scale shuffles are preserved; 8,192 mapping cases
match. No new branch, policy, tactic, synchronization, layout or buffer.

The bounded gate passes 18 paired exact-output comparisons (36 source
executions), including PDL off/on, changing/empty routes and N128/N256/M512.
All six FC1 executable sections are identical. Six FC2 specializations remove
64/128/256 non-NOP instructions each, totaling 896 fewer instructions; each
128/256/512 scalar multiply set becomes 64/128/256 packed multiplies. Shuffle
counts and geometry/storage are unchanged; registers change by −11 to +3,
with no stack/local spills. See `independent-review.md`.

The four-model native per-token screen has eight cells (128/16384 tokens),
3,200 raw samples, input quantization included, unfused finalize, and fixed
native winners with no AUTO. Each C-A-A-C leg uses 100 cold-L2 CUDAgraph CUPTI
samples after ten warmups. Overall 1.000217× and prefill 0.999863× are neutral.
V41 prefill −0.688% and V3 −0.251% are explicit small losses; Nemo prefill
+0.302% is observed, while K3 drift prevents a gain claim. Decode uses the
unchanged narrow path. This is retained for instruction efficiency and a small
source delta, not an end-to-end speedup claim. Full rows, source/cache/route/
tactic checks and process-boundary clock telemetry are in
`independent-timing-review.md`, `timing-summary.json` and
`timing-raw-samples.csv`.

Completed local and dedicated remote candidate source copies are removed only
after exact-source verification. All evidence, scripts, source/cache manifests,
native and DSL caches, and external symlink targets are preserved; no recovery
archive is created. `cleanup.json` records the source-only cleanup.
