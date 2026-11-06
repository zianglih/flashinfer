# Split W4A16 Gather4 optimization experiments

Scope: FC1 gathers BF16 rows directly from the original input and removes the standalone activation permutation. FC2, MegaMoE production, dense GEMM, and fused-finalize performance are outside this experiment. The Gather4 source/diff based on PR head `36740c36a32a6c6d1c7d8162823fe823912de741` is preserved in `workspace-before-regular-tma/`. The user subsequently requested the combined regular-TMA candidate in the main workspace, which now replaces Gather4 as the unstaged diff. All Gather4 measurements and source snapshots remain unchanged.

## Environment and measurement

C2/infra devbox `w4a16-gather4-1025`, host `hu-pdx-7`, B300 GPU0, explicit image `nvcr.io/nvidia/pytorch:26.05-py3` (latest CUDA13.2 NGC PyTorch release when checked October25). Torch2.12.0a0+5aff3928d8.nv26.05/CUDA13.2; CuTeDSL4.7.1; CUPTIpython13.4.0/lib13.4.58. CuTe emits PTX9.3 using bundled compiler13.3.27/NVVM23; this is distinct from the image runtime/systemCUDA13.2. Full environment manifests are stored with each campaign.

The benchmark and timing behavior in `scripts/run_split_benchmark.py` is unchanged; its runtime source-hash metadata now also records the tuner and mixed-cluster helper when present. It invokes native `benchmarks/bench_moe_deepseek.py`: H7168/I2048, simulated EP8 on one GPU, 256 experts/32 local/top-k8, seed42, SwiGLU, unfused combine, PDL enabled. Independent AUTO per fresh process, 10 warmups and 100 native cold-L2 CUDA-graph CUPTI samples. Tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384; only 1/2 excluded from retention. Distributed benchmarks are deferred at the user's request.

Native C++ sources are unchanged. Generated editable data links use identical native source paths to reuse unrelated JIT builds; Python candidate sources and AUTO selections remain independent. Full source hashes, patches, timing output and tactic caches are archived per run.

## Experiment ledger

| Variant | Candidate patch | Measurement | Overall | Decode | Prefill | Interpretation |
|---|---|---|---:|---:|---:|---|
| Per-lane Gather4 issuers | candidate-v3.patch | [split-v1](results/split-v1/RESULTS.md), complete ABBA |0.830854x|0.986206x|0.526031x|Rejected: major repeat-consistent prefill regression, including identical tactics. SASS has a serialization loop around each Gather4 instruction.|
| Elected issuer with shuffles | candidate-v4.patch | [split-v2](results/split-v2/RESULTS.md), two candidate sweeps reusing split-v1 baselines |1.005023x|1.030385x|0.940402x|All retained decode points improve both repeats; prefill still regresses. Prompted the follow-up experiments below.|
| Final uniform V9 with cache48 | [candidate-final-uniform.patch](candidate-final-uniform.patch) | [split-v3](results/split-v3/RESULTS.md), two candidate sweeps reusing split-v1 baselines |1.007745x|1.030856x|0.948616x|Do not retain as a solid optimization: T512/T4096/T8192 regress in both repeats; T16384 has mixed repeat direction. Candidate is archived for review.|

Primary ratios are geometric paired baseline/candidate ratios, not ratios of pooled samples or selected minima. Reused baselines do not provide a fresh bracketing drift control. Probe subsets are diagnostic only and cannot substitute for the complete retention grid.

**Final retention conclusion:** the uniform candidate preserves the small-token benefit, but the 1.0077449215681926× overall ratio does not justify the prefill regression (0.9486158867320897×); decode is 1.0308564733943713×. T1/T2 remain excluded from retention. Both fresh candidate sweeps completed the full 13-token grid, reusing the original before sweeps byte-for-byte. T4096 is 0.913521× and T8192 is 0.927955×, with complete active-token cache records identical across all four runs: FC1/FC2 `(256,192,256), cluster(2,1)` at T4096 and `(256,128,256), cluster(2,1)` at T8192, raster-M true and cold-L2 policy. These regressions therefore persist with matching tactics. T16384 is 1.006991× with mixed repeat direction, and its earlier single-probe gain did not hold consistently. The full raw medians, repeat ratios, and complete tactic records are preserved in [RESULTS.md](results/split-v3/RESULTS.md) and [RESULTS.json](results/split-v3/RESULTS.json). Two repeats and a reused baseline do not establish statistical significance or control temporal drift.

The final campaign changes only the launcher and kernel production sources; mixed-cluster tactics and their helper are absent. All 80 report input hashes, runtime/source manifests, identical candidate patches across repeats, and unchanged reused baseline files were verified. The archived candidate production hashes match `workspace-before-regular-tma/source/`:

| Source | Candidate SHA256 |
| --- | --- |
| `blackwell/moe_w4a16.py` | `fca68892d60062a62fab57eb9de9939ed90b0e3a1e704a4c056179352786772a` |
| `blackwell/moe_w4a16_kernel.py` | `58ea3844071ce9cb91980ac7f6a2ccd6eb89f45a6de678cfc303074ea6d29dee` |

Iteration stops with this evidence. The candidate was left unstaged at the end of the Gather4 experiment and later archived when the user selected regular TMA for the main workspace; no additional GPU work or rigorous sanitizer campaign is scheduled for this unretained optimization.

The devbox was released after evidence capture; [devbox-delete.log](logs/devbox-delete.log) records successful deletion. Source changes and all experiment artifacts remain local for review.

## Candidate-only probes

The six completed probes reuse the same completed split-v1 before medians. Each is one fresh AUTO sweep over T16/T512/T4096/T16384 using the same native timing. No baseline was rerun. The tables below preserve all measured points; no subset aggregate is used for retention. The interrupted V10 probe is recorded separately below. Complete active-token cache records, cumulative-cache comparisons and source-report hashes are in `PROBE_COMPARISON.json`. Original probe reports and caches are unchanged.

| Tokens | Before R1 (µs) | Before R2 (µs) | V4 R1 (µs) | V4 R2 (µs) | V5 hoisted issuer (µs) | V5a distinct OOB (µs) | V6 mixed option (µs) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 76.9610 | 76.9605 | 73.7285 | 72.4325 | 72.4005 | 72.4965 | 73.4565 |
| 512 | 159.7130 | 159.7135 | 155.7770 | 155.6490 | 160.7855 | 159.8730 | 160.2735 |
| 4096 | 301.7310 | 300.4825 | 331.3625 | 331.3950 | 331.2830 | 330.9145 | 330.6905 |
| 16384 | 1235.8340 | 1202.2180 | 1279.8020 | 1269.7705 | 1243.1295 | 1260.0265 | 1268.5380 |

| Tokens | V7 cache48 (µs) | V8 full96 (µs) | V9 branch hoist (µs) |
| ---: | ---: | ---: | ---: |
| 16 | 73.2805 | 72.2730 | 73.3440 |
| 512 | 160.5290 | 158.9770 | 160.0975 |
| 4096 | 329.6505 | 330.1465 | 328.2270 |
| 16384 | 1233.5945 | 1269.8340 | 1183.9775 |

| Tokens | Baseline / V5 | Baseline / V5a | Baseline / V6 | Baseline / V7 | Baseline / V8 | Baseline / V9 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 1.062986× | 1.061579× | 1.047705× | 1.050221× | 1.064862× | 1.049312× |
| 512 | 0.993331× | 0.999001× | 0.996504× | 0.994918× | 1.004631× | 0.997600× |
| 4096 | 0.908909× | 0.909921× | 0.910538× | 0.913410× | 0.912038× | 0.917372× |
| 16384 | 0.980517× | 0.967369× | 0.960878× | 0.988096× | 0.959897× | 1.029504× |

These descriptive ratios are `sqrt(BeforeR1 * BeforeR2) / Probe`; they are not paired-repeat retention ratios.

Actual-workload tactic summary follows. `M/N/C` means tile `(M,N,256)`, cluster `(C,1)`, raster-M true; each cell lists FC1 then FC2. Full cache-entry equality compares the entire key and value, not these abbreviated fields.

| Tokens | Before R1/R2 | V4 R1 | V4 R2 | V5 | V5a | V6 |
| ---: | --- | --- | --- | --- | --- | --- |
| 16 | 128/8/1 + 128/8/1 | 256/16/2 + 256/16/2 | 128/8/1 + 128/8/1 | 128/8/2 + 128/8/2 | 128/8/2 + 128/8/2 | 256/16/2 + 256/16/2 |
| 512 | 256/32/2 + 256/32/2 | same | same | same | 128/32/2 + 256/32/2 | 256/32/2 + 256/32/2 |
| 4096 | 256/192/2 + 256/192/2 | 256/128/2 + 256/128/2 | same as V4 R1 | same as V4 R1 | same as V4 R1 | same as V4 R1 |
| 16384 | 256/128/2 + 256/128/2 | same | same | same | same | same |

| Tokens | V7 | V8 | V9 |
| ---: | --- | --- | --- |
| 16 | 256/16/2 + 256/16/2 | 128/8/2 + 128/8/2 | same as V7 |
| 512 | 128/32/2 + 256/32/2 | 256/32/2 + 256/32/2 | same as V7 |
| 4096 | 256/192/2 + 256/192/2 | 256/128/2 + 256/128/2 | same as V7 |
| 16384 | 256/192/2 + 256/192/2 | 256/128/2 + 256/128/2 | same as V7 |

- **V5:** hoists the issuer election and caches uniform indices for small row partitions. T4096 remains near 331 µs; T512 is slower than both v4 repeats despite identical complete active-token tactic records. One probe cannot separate source effects from temporal drift. [Probe](probes/v5-hoisted-election/PROBE_RESULTS.md).
- **V5a:** adds distinct OOB row coordinates inspired by FlashMLA. AST comparison against the saved v5 source confirms this is its only semantic change. It shows no consistent benefit; T512 also changes its FC1 tactic. This variant was left unapplied. [Probe](probes/v5a-distinct-oob/PROBE_RESULTS.md).
- **V6:** adds FC1 preferred-cluster4/fallback2 options at route N128/N192, with FC2 cluster2. AUTO selects no mixed tactic at any of the four measured token counts, nor in any of the final cumulative cache's 22 non-metadata entries. Complete active-token records equal v5 at T512/T4096/T16384; T16 chooses a different ordinary cluster2 pair. The slight T4096 difference is not evidence of a mixed-cluster benefit, and T16384 remains slower than baseline. [Probe](probes/v6-mixed4-2/PROBE_RESULTS.md).
- **V7:** caches up to 48 row indices. AUTO switches both prefill workloads to ordinary N192/cluster2. T16384 improves to 1233.5945 µs, close to the reused baseline's 1218.9101 µs geometric mean, but T4096 remains 9.48% slower than baseline. The tactic changes prevent attributing the end-to-end improvement solely to index caching. No mixed tactic is selected. [Probe](probes/v7-cache48/PROBE_RESULTS.md).
- **V8:** caches up to 96 row indices. AUTO selects ordinary N128/cluster2 for both prefill workloads, and their timings remain near v6. V7 and V8 have different complete active-token tactic records at all four measured shapes. No mixed tactic is selected. The mixed N192 specialization also incurs local-memory spills, described below; full96 is not an established improvement. [Probe](probes/v8-full96/PROBE_RESULTS.md).

- **V9:** moves physical cluster-width dispatch outside the activation K loop and specializes each loop's row count. All four complete active-token records match V7; AUTO still selects ordinary cluster2, and none of the final 22 cumulative entries selects mixed. T16384 reaches 1183.9775 µs (1.029504× the reused baseline), while T4096 remains 328.2270 µs (0.917372×). This probe led to the bounded V10 follow-up and the final uniform-only full campaign; it did not establish full-grid retention or a mixed-cluster speedup. [Probe](probes/v9-branch-hoist/PROBE_RESULTS.md).

All cumulative-cache documents differ between these probes even where the active-token record matches; entries for other AUTO profiling shapes must not be mistaken for the timed workload's selected tactic. No mixed variant is retained on this evidence.

The [offered-tactics receipt](../../evidence/gather4/offered-tactics.json) records all 25 registered tactics, including both mixed FC1 N128/N192 options, surviving runner filtering at T64/T128/T4096/T16384 on the B300. Occupancy reports 33 preferred cluster4 and 8 fallback cluster2 capacity slots. This directly covers both timed prefill shapes; the receipt does not contain T16/T512. V6/V7/V8/V9 select no mixed option anywhere in their final 22-entry cumulative caches, and their completed benchmark logs contain no skipped-tactic messages. Together these observations establish that mixed options were offered to AUTO and lost its prefill selection, rather than being removed by runner filtering. The receipt itself is shape-only and contains no timing or source hashes; individual losing-tactic timings were not retained. Full receipt contents and hash are included in `PROBE_COMPARISON.json`.

The original v6 probe predates complete untracked patch capture: its source manifest records the helper hash, but `working-tree.diff` omits the untracked helper. The saved `transfer/runtime/w4a16_mixed_cluster.py` matches that hash (`4e0cdde6899a6feea0fbc60f11ec21821a53547a46e4c7756dc745274377eb89`). This provenance boundary is recorded in `PROBE_COMPARISON.json`; historical artifacts were not rewritten.

### Interrupted V10 probe

V10 skips activation groups strictly outside runtime N and manually completes their transaction bytes. Only T16 completed: **73.2810 µs**, selecting ordinary `256/16/2 + 256/16/2`. T512 AUTO remained at profile 8/10 from about 11:45:30 UTC through 11:47:32 UTC without producing a timing row. The identified benchmark process received SIGTERM and returned 143. The cause is unconfirmed because no GPU activity snapshot was taken before termination; this is not established as a kernel deadlock. T4096/T16384 did not run. V10 is rejected/incomplete, with no ratio or aggregate. The partial native output, complete T16 cache, and [interruption receipt](probes/v10-skip-unused-b/INTERRUPTION.json) are preserved and recorded separately in `PROBE_COMPARISON.json`.

V10 had passed 32 normal exact cases in 28.44s and 8 forced-fallback2 cases in 12.76s before the probe. Those tests do not establish reliability across all AUTO shapes. Logs are `../../logs/smoke-v10-skip-unused-b.log` and `../../logs/smoke-v10-forced-fallback2.log`. The final candidate returned to V9's uniform-only implementation and completed the two full candidate sweeps recorded above using the existing baseline.

## Validation and code generation

Both candidates passed the same six existing exact boundary cases: top-k2/3, routeN8/N16/N128, tail1, covering oneCTA, oneCTAcluster2 multicast and twoCTA. V4:6passed/18deselected in105.69s including native build setup. Logs: `../../logs/smoke-v4.log` and experiment launch logs. Changed-file pre-commit passes. Rigorous full matrix and Compute Sanitizer remain deferred until performance retention, as requested.

V7 and V8 each passed the expanded 32 exact cases: V7 `32 passed, 730 warnings in 27.27s`; V8 `32 passed, 730 warnings in 26.80s`. Raw logs are `../../logs/smoke-v7-cache48.log` and `../../logs/smoke-v8-full96.log`. V9 passed the same 32 exact cases in 27.76s and 8 forced-fallback2 cases (24 deselected) in 12.30s; raw logs are `../../logs/smoke-v9-branch-hoist.log` and `../../logs/smoke-v9-forced-fallback2.log`. All three new probe snapshots include and verify the complete untracked mixed-cluster helper bytes and its addition patch.

The final uniform-only candidate passed all 24 focused exact cases: `24 passed, 598 warnings in 22.08s`, exit 0. Raw evidence is in [smoke-final-uniform.log](../../logs/smoke-final-uniform.log) and its exit-code receipt. Mixed-cluster cases are outside this final candidate. Rigorous full correctness and Compute Sanitizer were not run, following the user's performance-first iteration scope.

`top_k` is a compile-time wrapper parameter, part of the compilation key, absent from runtime kernel arguments. Code-generation probes for3 and8 verify constant multiply and shift lowering. Unfused FC2 passes0 to avoid unnecessary top-k specializations. The final code-generation helper uses valid zero packed weights/unit scales to avoid unrelated native quantization compilation.

V3 SASS:4 static Gather4 sites, each followed by a lane-serialization backedge. V4:64 static Gather4 sites, no such backedges; dynamic transfer count is unchanged. `codegen-v4/` contains PTX, cubins, SASS and reports. The larger static count is unrolling, not extra data copies.

The [index-cache code-generation comparison](CODEGEN_INDEX_COMPARISON.md) covers all 24 H7168 specializations for v6/cache48/full96, N128/N192, cluster2/mixed4+2, and top-k3/8. Counts isolate the hot Gather4 K loop. For ordinary N192/top-k8, cache48 reduces static loop instructions from 966 to 682 and SHFL from 96 to 48, with no local spills; ordinary N128 instead grows from 454 to 480 instructions. Mixed row-count guards remain inside the K loop. Full96 mixed N192 has a 216-byte stack plus 220-byte spill stores/loads in ptxas, with 50 LDL and one STL in the hot loop; the other specializations have no local spills. Uniform-register transfer instructions are counted separately from local-memory spills. [V9 code generation](CODEGEN_BRANCH_HOIST.md) has separate preferred4/fallback2 K loops: N128 262/485 sites and N192 358/714, versus cache48's modeled 312/575 and 446/823. All four mixed specializations have zero local spills.

The later [uniform N192 capture](CODEGEN_V9_UNIFORM.md) shows byte-identical PTX, cubins, and SASS between V9 and V7/cache48 for top-k3/8. The top-k8 K loop is unchanged at 682 sites, 96 Gather4, 48 SHFL, and zero local spills. These synthetic captures use `num_tokens=256`; the actual timed T16384 cubin was not separately captured. They provide no instruction-level explanation for the single-probe T16384 difference. Mixed-loop savings therefore do not explain the AUTO-selected ordinary path by themselves. The final repeated campaign above supplies the retention evidence and does not support retaining the optimization.

## Reproduction

- `run_campaign.sh`: fresh ABBA, overwrite-protected.
- `run_followup_campaign.sh`: candidate repeats with verified reused baseline artifacts.
- `run_probe.sh`: candidate-only AUTO subset screens; defaults16,512,4096,16384.
- `summarize_results.py`: provenance checks, complete raw medians and full tactic comparison.
- `snapshot_sources.py`: records all scoped source hashes, preserves untracked source bytes, and appends their complete addition patches without staging files. The campaign allowlist is exactly `moe_w4a16.py`, `moe_w4a16_kernel.py`, `tuner.py`, and `blackwell/w4a16_mixed_cluster.py`; any other production difference is rejected.
- `capture_fc1_ptx.py` / `inspect_codegen.sh`: source and generated-code constexpr checks.
- `candidate-v*.patch`: preserved implementation stages; v2 failed at a DSL compile-time guard before any timing and was corrected in v3. The failed run remains under split-v1/after-r1-compile-error.

No PR body, commit, branch ref, or Git staging update is part of this experiment.
