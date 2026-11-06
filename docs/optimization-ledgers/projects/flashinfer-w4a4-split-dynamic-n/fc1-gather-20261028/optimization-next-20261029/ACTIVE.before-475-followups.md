# Active handoff — 2026-10-29

User requests continuous optimization on forkPR8, including W4A16, until told to stop. UpstreamPR7290 stays untouched. No sanitizer. Latest retained/pushed fork head is `475cae6b28a536e24aa8da2ed488d0f00fb5305b`; canonical fork checkout `flashinfer-fc1-gather-review` is clean. Prior retained follow-up7106faf3 removes observed spills and moves independent weight-SF copies before gather wait. c0c0 uses lane-owned route decode/shuffles,11added/35removed lines. Full468-cell validation passed; current PRbody/heatmaps published and read-back verified in `composed-metadata/publication/receipt.json`.

| GPU | Owner | Active work |
|---|---|---|
|0,1,2,3,4,5|free|Full364 refresh completed and published; CPU-only gap ledger in progress.|
|6|external_gap_audit|W4 K3EP4K/8K paired timing, CUPTI timelines and read-only clock telemetry.|

|7|full_bench_audit|Live-group Gather4 candidate23exact passed; SASS audit before bounded perf.|

## Source copies

- `flashinfer-fc1-gather-cpasync-review`: rejected and retired.36 affected cells, overall−4.67%, prefill−9.92% versus c0c0; evidence in `cpasync-payload/`.
- `flashinfer-w4a16-tma-gather-review`: frozen b361 cleanup control; new shared Blackwell inline_ptx helper (includes unused issue knob to remove only after experiments). Original prototype TMA outperformed W4 cp.async on all EP prefill shapes.
- `flashinfer-w4a16-single-arrival-review`: rejected and removed.33 exact cases passed;32-cell screen EPprefill−0.69%, TPprefill−0.50%, decode neutral. Evidence in `w4a16-single-arrival/`.
- `flashinfer-fc1-gather-control120-review`: retained as1b0f1f69 and retired.17 exact tests,60 cells/24000 samples: performance neutral+0.053%; wide2CTA MX stack accesses removed, no new role/tactic/shape rule. Canonical checkout is clean.
- Other W4 active copy paths and exact hashes are in `../full-20261029/w4a16-gather-ledger.md` maintained by external_gap_audit.

## Findings guiding next work

- W4 Gather4 five-WG screen improved all16 prefill points (TP roughly13–35%), but decode regressions remain. Gather is the last WG; FC2 retains four WGs.
- Native W4 decode retune: V3 EP8 token8 +4.52%, V41F EP4 token8 +10.70% on b361; token256 slightly negative. No added tactics.
- W4 gather quota32 fits after compiler reallocation; linear SASS highest-register scans had included unreachable other-role tails.37 case CFG/codegen audit and40 exact cases pass. Giving freed registers to either decoders or epilogue worsens perf; retain144/80/96/96/64 allocation for now.
- N3U EP16K swap gap is FC1: CUPTI prepare saves19.51us, FC1 completion adds222.97us, FC2 tail and combine neutral. NCU stalls on trivial allocation independently of MoE; no hardware counters available. See `ncu-n3u-prefill/RESULTS.md`.
- Prior swap cp.async R5 predates corrected donation and cluster publication, so transport revisit is justified. New experiment changes only payload transport, preserving scale path, phase capacity, PDL and current roles.

Use `/usr/local/bin/h`; remote wrapper at `optimization-20261028/swap-ab-hybrid-output/remote_box.py`, cwd `/Users/ziangli/rl/hai`. Replacement devboxC3 fi-gather-opt-1029 namespaceziangli (old1028 box disappeared), explicitimage nvcr.io/nvidia/pytorch:26.05-py3. Persistent native caches remain intact. See `experiment-handoff.md` for preparing correct source/runtime copies.

The final84-cell native existing-tactic sweep completed before reclamation: +1.877% mean,+2.918%EP,+0.688%TP. All outcomes preserved; stableK3 selection regressions remain. Public graph-only MeasurementPolicy selects the same slower K3 tactics, so execution mode alone does not fix them. Native inputs_pre_hook simulates balanced max-load routes; actual routes have different tile counts. Controlled route/scope investigation ongoing.

Persistent C++ caches survived. Installed CuTeDSL4.8 default diskcache was /tmp/root/cutlass_python_cache; future campaigns use explicit CUTE_DSL_CACHE_DIR under compile/cute-dsl-4.8.0-cuda13.2-sm103. Do not alter active campaign environments.

Final W4 full104 completed with40 exact cases plus6 alignment-offset cases. Excluding1/2: EPdecode+0.318%, EPprefill+0.540%, TPdecode+2.843%, TPprefill+17.299% (prefill includes512). Keep all gaps visible, including K3EP4K/8K. See ../full-20261029/w4a16-full. Composed active source flashinfer-fc1-gather-composed-review preserves latest1b0 swap changes; frozen W4 files/common helper only.

Actual-route default tuning was previously rejected after a dummy-warmup holdout. Preserve that decision; route distributions are absent from cache keys. Current controlled route proof is diagnostic, not justification to train production tactics on first-call routes. NCU replacement-host smoke again hangs on native allocation, so no hardware counters or further routine retries.

W4 five-WG Gather4 retained/pushed475cae6b; canonicalclean. Composed source copy retired after all514 hashes verified against commit,17swapexact and4byte-identicalSASS gates. Full364swapAA runs on0–4. W4summary uses standardbands now: decode4–64,middle128–512,prefill4096–16384. W4TPprefill+20.79%,EPprefill+0.53%; overallTP+7.88%,EP+0.40%. Previous17.3%TPprefill included512, not a changed cell result.

Final475 full468 publication verified at composed-w4/publication/receipt.json (body21fcd12b,396displayedcells,468raw,EP+0.65%,TP+5.25% vs saved d35; cross-GPU-instance boundary explicit). Includes5dtype heatmaps,9column external comparisons,8rawA2 panels, new W4scope/title and separateddiffcounts. No stale W4unchanged claim. Native prefill winner-selection changes included explicitly; largestAA spread7.45/7.03%.

Current source experiment: flashinfer-fc1-gather-live-groups-review at475, one unstaged kernel change. Live rowgroups via loop and lane-heldIDs/shuffles; scale path and barrier counts unchanged, transaction bytes adjusted. Ownership proof2976combinations. Paired23exact cases passed both arms; SASS gate before GPU7perf. W4staticbounds/modulo copies retired after bad instruction results; W4agent profiles K3gap on6. Root canonicalclean and source-bound publication current.

Publication assets commit 378e59a3a9b614c23619f23b12433bfc747b17d3; exact body readback SHA21fcd12b91ffa15a9e2e7eca0dc3ae403d7185cfda6e2b18e3fad37fd9744a27. Primary PR title now includes swap-AB and W4A16.
