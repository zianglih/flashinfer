# B300 W4A16 small-token review

Completed 2026-11-03 on C3 `fi-pr7290-small-w4-1103`, eight B300 SXM6 GPUs. The requested immutable sources were used: baseline `002529e17b22567a071091053c6c4dc2a55e050e` with the recorded benchmark adapter; current `14a338579eb8acddcc5cfd1cc58871fc0788de22`, independently OFF and ON. The separate pending host API/test review changes were not part of these benchmark sources.

## Main fixed-choice matrix

- V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8; tokens 4, 8, 16; unfused functional W4A16 BF16.
- Before → OFF → ON → ON → OFF → before; one GPU per job, eight jobs in parallel. Each phase uses strict CUPTI CUDA-graph cold-L2 timing,10 warmups and100 samples. Cache hits, exact tactic identity, routing identity and source hashes are checked; timing fallback and timed autotuning are forbidden.
- Before and OFF share the previously selected baseline tactic for each cell. ON uses the retained swap-AB tactic. These choices originate from the earlier B300 selection; they are controlled choices, not a fresh best-tactic claim.
- All 8 jobs / 48 phases passed;14,400 raw samples,24 workloads × 3 arms × 2 repeats. Full elapsed 209.6 s after the pilot. Maximum within-arm phase-median spread: 0.466%.
- Across 24 workloads, OFF geomean speedup +2.707%, ON +3.562%. OFF has 6 negative cells; ON 3. No cells were removed or replaced.
- V3 EP8 T4: before 50.41648µs, OFF 52.75250µs (-4.428%), ON 50.23195µs (+0.367%). This reproduces the OFF regression with the frozen two-CTA choice.

Raw data: `perf-evidence/c3/results/`. Configuration and source/native warm receipts: `perf-evidence/c3/qualified/`. Deployed helper scripts and source manifests: `perf-evidence/payload/`. Fetch SHA inventory: `perf-evidence/c3/fetch-perf-manifest.json`; archive receipt: `fetch-perf.json`. Parent-owned `../plots/b300-*` contains the complete table/heatmap and numerical audit. Independent raw-span reconstruction: `full-matrix-independent-audit.json`.

## Separate fresh native V3 EP8 T4 check

All 3 arms publicly autotuned into new per-arm caches, outside the balanced sampling. Each enumerated 23 W4 tactics at the benchmark's 1/2/4-token buckets. Baseline had 69 profile calls; current arms 72. All compilation/profile calls succeeded. Both current arms compiled 30 guarded W4 kernels with no failed resource checks or local memory. No tactic was removed by a guard.

A separate before → OFF → ON → ON → OFF → before replay then collected 600 CUPTI samples on GPU 2, with the same input/routing/clock/timing contract:

| Arm | Geomean of phase medians (µs) | Speedup vs before | Native FC1/FC2 tactic |
|---|---:|---:|---|
| Before | 50.79275 | — | (128,16,256), cluster(1,1), CLC |
| OFF | 50.15275 | +1.276% | (128,8,256), cluster(1,1), CLC |
| ON | 50.32019 | +0.939% | (128,8,256), cluster(1,1), CLC |

Fresh tuning removes the tested B300 V3 T4 loss. It does not prove all shapes are optimal or that the fixed-choice regressions are absent. This dataset never replaces the main fixed-choice heatmap. Evidence: `fresh-native/`, `fresh-native-audit.json`, `fresh-native-qualification.json`; archive `archives/fresh-native.tar.gz`. All 600 replay samples were reconstructed directly from CUPTI launches/activities.

## Runtime and provenance

Image `nvcr.io/nvidia/pytorch:26.05-py3`, selected after live NGC check as latest CUDA 13.2 release. Torch 2.12.0a0+5aff3928d8.nv26.05, CUDA 13.2, PTXAS 13.2.78, nvidia-cutlass-dsl 4.8.0 (embedded DSL compiler 13.4), driver 595.91.07. `runtime-final.json` under qualified records exact package versions, UUIDs and final GPU-process-free state. No power/clock changes.

Baseline native extensions were rebuilt through the ordinary loader in a fresh CUDA 13.2 source-specific namespace. No CUDA 13.0 objects/ELFs or cross-source headers were copied. Current valid normal caches were reused; final loader receipts include no-op checks. The initial historical source inventory had 542 misplaced CUTLASS documentation paths and 3 missing export-ignored CCCL metadata links. Parent regenerated exact Git/pinned-submodule inventories and only the newly owned source copies were reconciled. Kernel bytes were unaffected. Full postflight verified 31,069 baseline files and34,762 current files and every native data link.

Failed setup attempts/logs remain local: initial review launch exceeded Linux argument-size limit; source inventory repair initially mishandled symlink extraction; first postflight helper duplicated a data-link path prefix. All were fixed in harness/setup without production source edits; none supplies accepted timing data.

## Reproduction entry points

The exact resolved commands/environment for every phase are in each `receipt.json`. Remote campaign configuration was `/data/ziangli/flashinfer-moe-gather-pipeline/integration/pr7290-review-small-w4a16-20261103/c3/qualified/config.json`.

```sh
# One fixed-choice job; all eight jobs used this command on distinct GPUs.
python payload/run_job.py --config c3/qualified/config.json --job ep-v3-w4a16 --gpu 2
# Fresh tuning, independently for before/off/on; then replay the fresh winners.
python payload/fresh_native.py --config c3/qualified/config.json --output c3/fresh-native --role off --gpu 1
python payload/fresh_native.py --config c3/qualified/config.json --output c3/fresh-native --make-replay
python payload/run_job.py --config c3/fresh-native/replay-config.json --job ep-v3-w4a16 --gpu 2
```

Output directories must be new; the stored runs are immutable. Persistent native/CuTe/download caches remain on cluster storage. No additional GPU experiments or sanitizer were launched. Separate C3 review validation is documented in `review-validation.md` (28 passed).
