# Separate AUTO36 static-scheduler experiment preparation

This experiment uses unpublished source commit `f14e4bae9379703fd5693d8ee993faae23e130d5`, whose parent is the public primary candidate `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`. Only the AUTO catalog and its host test change. The kernel bytes remain identical. Product catalog52 contains original16 uniform candidates, 18 atomic mixed candidates and 18 static mixed candidates; policy `mixed-only` selects the latter36. The fresh baseline uses original16/all. The three-point grid is T64/T128/T4096, with 100 untrimmed cold-L2 CUPTI rank-MAX samples after 3 warmups per arm/point.

This is a separate experiment, not confirmation of the original candidate3r AUTO18 policy. It does not alter or pool into the primary full13 table, raw samples or aggregate results. The paired capture completed and passed native timing/source and scheduler-mode coverage audits. The experiment was rejected; selected source is `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`. All three selected tactics used atomic scheduling; no retained benefit warrants doubling the mixed AUTO catalog.

The [exact two-file patch](recipe/auto36-static-on-3d.patch) reproduces the attempted code without requiring access to the unpublished commit. [Source and helper hashes](source-recipe.json) record its identity. After following the primary bundle's Docker/setup instructions to create clean baseline and candidate3r checkouts, run:

```sh
bash /path/to/static-experiment/recipe/reproduce-static.sh \
  /path/to/primary-bundle /work/baseline /work/candidate3r \
  /work/static-results /work/static-cache
```

The script applies the patch to the 3d checkout, verifies both changed files and the unchanged kernel, then invokes the primary bundle's exact native driver/wrapper/run helper with the same controls and separate FlashInfer workspace bases. It also uses the captured AUTO-ranking and scheduler-mode audit helpers. The reproduction source receipt will identify HEAD3d plus the patch, rather than pretending to have the original unpublished commit; the attempted source bytes match. Internal AUTO ranking scores document mode coverage and selection only; they are not cold-L2 latency samples.

For a completed pair, each arm includes its full `auto-rankings.json`: only its top-level absolute capture path is parameterized; all tested tactics, rounded internal scores and original log hashes remain. The scheduler-mode receipt records both the original ranking-file hash and the normalized public-file hash. Re-run the exact captured coverage auditor from the published files without GPU access:

```sh
EXPERIMENT=/path/to/bundle/experiments/auto36-static
bash "$EXPERIMENT/recipe/audit-published-modes.sh" "$EXPERIMENT" baseline /tmp/new-baseline-modes.json
bash "$EXPERIMENT/recipe/audit-published-modes.sh" "$EXPERIMENT" candidate4s /tmp/new-candidate-modes.json
```

Each new capture also has its own safe `hardware.json`, extracted from that capture's GPU inventory and topology receipts. GPU model/count, host driver and GPU-only interconnect matrix must match the corresponding primary arm; original inventory hashes remain available while private host/process/NIC fields are omitted. This verifies recorded controls and does not prove identical clocks, thermals or absence of other environmental variation.

Local publication preparation uses `publication/add_static_experiment.py`. It accepts either a completed paired screen, which must pass the frozen comparison and scheduler-mode audits, or a failed attempt backed by nonzero exit receipts. It never fabricates missing samples or uses incomplete outputs in a comparison table. Complete/partial capture files, source identity, normalization rules and exact hashes remain explicit. A new versioned extension is created only when those receipts exist. Final branch selection/restoration stays pending unless separately documented; no publication or new GPU work is performed by packaging.

Optional final-decision arguments are applied before validation and checksum generation. The default is `--decision pending`. To reject the trial, supply `--decision rejected --decision-rationale '...'` and two `--restoration-receipt` JSON paths, one local and one remote. Each original receipt must contain `scope` (`local` or `remote`), restored `commit`, empty `status` from full porcelain status including normal untracked files, and `files` mapping all 14 original candidate-freeze paths to their SHA256 values. An optional `recorded_at` timestamp is preserved. The builder requires exact equality to the original 3d freeze, publishes only those allowlisted fields and original receipt hashes, and omits private source/host metadata. Until both receipts exist, rejection cannot be finalized in a bundle. `--decision retained` requires a complete screen and rationale; restoration is then explicitly not applicable. Never amend an already checksummed bundle to update the decision: build a fresh version after the actual receipts arrive.

## Verified source restoration

[restoration.json](restoration.json) records both local and remote clean 3d047d3 receipts, with all 14 recorded file hashes equal to the original candidate freeze. The published summary omits private machine paths. Restoration does not create new timing or correctness evidence.

## Separate observed results

| Tokens | Baseline median us | Candidate median us | Baseline/candidate |
|---:|---:|---:|---:|
| 64 | 159.601000 | 162.705500 | 0.980920 |
| 128 | 171.025500 | 171.233500 | 0.998785 |
| 4096 | 403.332500 | 400.499500 | 1.007074 |

[Baseline raw records](baseline/raw-records.json), [candidate raw records](candidate4s/raw-records.json), [sample 0 and comparison](comparison.json), and [native audit](audit.json). All 100 samples per arm/point are retained. Ratios above 1 favor candidate; no significance claim is made.
