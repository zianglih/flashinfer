# R1 shared-prepare integration on retained33b7

The active review checkout is `flashinfer-prepare-index-review`, fast-forwarded to
`33b7e5260132eb4ba2fdfdd97bd71a892f04a481`. Only
`moe_swap_ab_prepare.py` is unstaged. Its bytes match frozen R1
`603dcdf240e23e958a35bee5f3666f83c51a078a1ab317ad48bdb15671d211e5`:
unsigned arithmetic for known nonnegative routing indices, preserving the original
loop policy. The R2 explicit `unroll=1` variant is not included.

`source-local.json`, `integration.json`, `candidate.patch`, and `base.bundle`
bind all348 source files and the one-file delta. `config.json` binds the clean
remote33b7 base plus patch, the immutable retained control bytes, and nine native
compilation-cache symlinks. Per-pass compiler artifacts use private working
directories. No caches are deleted.

`full/` runs15 supported EP/TP jobs with13 token counts and two fresh candidate
passes. Source, routes, managed tuning caches, winner identities and actual GPU
UUIDs match the retained33b7 `composed/full` candidate passes1/2. Those saved
baseline timings are reused; no external baseline or autotuning is rerun.
Both native NVFP4 and MX families are included, including W4A16 because prepare
is shared. Timing is the unchanged public API chain, cold-L2 CUDA graphs,
10 warmups and100 strict CUPTI samples per measurement.

GPU7 is held for the independent targeted prepare exact/codegen gate before its
benchmark lane launches. All other lanes launch independently. No sanitizer,
broad pytest, production commit, or PR publication is part of this campaign.

The comparison is fresh AA versus saved AA, not a fresh CAAC experiment. The time
gap remains a limitation when interpreting small changes. Tokens1 and2 are
collected but excluded from displayed/retention aggregates. Existing unsupported
MX cases stay absent rather than being filled or emulated.

Collection: `full/fetch_evidence.py` verifies each raw archive member.
Analysis: `analyze_full.py` consumes fresh `full/evidence/raw` plus retained
`../../composed/full/evidence/raw`, writing `full/analysis`.
`full/independent_audit.py` rechecks all samples, source/cache/routes, UUIDs,
receipt hashes and published primary ratios after collection.
