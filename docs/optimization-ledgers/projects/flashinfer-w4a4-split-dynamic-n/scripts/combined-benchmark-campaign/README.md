# Primary candidate campaign readiness

The next candidate is not yet selected or deployed. Do not execute these commands
until the root agent confirms its full commit SHA, GPU0/GPU1 availability, and
readiness of the candidate native-JIT epoch. Candidate source stays frozen for
all primary measurements. No source deployment or reset is performed here.

For the next post-13ca candidate, use [NEXT_CANDIDATE.md](NEXT_CANDIDATE.md) and
the generic prepare/launch/archive/finish scripts. Historical commands and
completed checkpoints below remain as evidence.

Existing valid B1 evidence is reused:

- NVFP4 W4A4, per-tensor activations, GPU0: `results/baseline-r1.json`.
- Homogeneous MXFP8 E4M3, GPU1: `results/mxfp8-unfused-baseline-r1.json`.
- MXFP4 weights × MXFP8 E4M3 activations, GPU1:
  `results/mxfp4-unfused-baseline-r1.json`.

All runs use deterministic unfused finalize, native AUTO, EP8/TP1, H7168/I2048,
256 global/32 local experts, top-k8, seed42, and native 10-warmup/100-sample
cold-L2 CUDA-graph CUPTI medians. Initial activation/weight quantization and
inter-GPU communication are excluded. The exact token grid is
`1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only 1 and 2 are excluded from
retention. Decode is 4–512 and prefill is 4096/8192/16384. Failed checkpoint
screens are diagnostic evidence and do not replace retained A1.

## Candidate screening commands

Execute on `fi-w4a4-dyn-n-1024` in c1, namespace ziangli, pinned image
`nvcr.io/nvidia/pytorch:26.05-py3`. First complete candidate native-JIT loading
serially before starting a concurrent mode. Use fresh processes per mode. The
shell refuses existing JSON/log/cache evidence rather than truncating it.

```bash
set -euo pipefail
project=/workspace/flashinfer-w4a4-split-dynamic-n
candidate_sha=REPLACE_WITH_ROOT_CONFIRMED_40_CHARACTER_SHA
label=${candidate_sha:0:8}
cd "$project/candidate"
test ${#candidate_sha} -eq 40
test "$(git rev-parse HEAD)" = "$candidate_sha"
git diff --exit-code HEAD -- flashinfer include csrc benchmarks tests
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
export TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0
export FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0
for task_recipe_name in ${!FLASHINFER_NVFP4_4OVER6@}; do unset "$task_recipe_name"; done
```

GPU0, original frozen NVFP4 helper SHA
`c9678f2386ac4a843f12b33ee17bbbf4a5cafdc827ab1df40d3d0f9d9285a4d1`:

```bash
nvfp4_out="$project/results/nvfp4-candidate-screen-$label"
! compgen -G "$nvfp4_out.*" >/dev/null
set -o noclobber
CUDA_VISIBLE_DEVICES=0 "$project/.venv/bin/python" "$project/scripts/run_split_benchmark.py" \
  --repo "$project/candidate" --expected-head "$candidate_sha" \
  --image nvcr.io/nvidia/pytorch:26.05-py3 \
  --tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
  --output "$nvfp4_out.json" > "$nvfp4_out.log" 2>&1
```

GPU1, sequential modes, original v2 frozen helper SHA
`989076c16165a2a6370e6246975aac80dcd80032c156ff55b5b44ff115c36a08`:

```bash
frozen_tools="$project/results/unfused-baseline-epoch-v2-tools"
for weight_format in mxfp8 mxfp4; do
  mode_out="$project/results/$weight_format-unfused-candidate-screen-$label"
  ! compgen -G "$mode_out.*" >/dev/null
  set -o noclobber
  CUDA_VISIBLE_DEVICES=1 "$project/.venv/bin/python" "$frozen_tools/run_split_benchmark.py" \
    --repo "$project/candidate" --expected-head "$candidate_sha" \
    --image nvcr.io/nvidia/pytorch:26.05-py3 \
    --weight-format "$weight_format" --gated-group-size 16 \
    --tokens 1,2,4,8,16,32,64,128,256,512,4096,8192,16384 \
    --output "$mode_out.json" > "$mode_out.log" 2>&1
done
```

The command manifest, complete raw logs/JSONs, all 13 AUTO caches and SHA hashes,
GPU UUID/process snapshots, exact tested commit, source hashes, and environment
must be archived before any source changes. Native in-memory bucket reuse is
preserved, caches are saved as evidence only, and CUPTI fallback is fatal.

## Optional bounded large-token diagnostic

After root deploys the committed candidate and releases GPU0, a first T16384
NVFP4 probe can use the same frozen native measurement helper without repeating
B1. This is diagnostic only: an isolated T16384 process has a different AUTO
bucket history from the full 13-token sweep and must not be retained as A1.
The source/env setup above still applies. Keep this distinct prefix:

```bash
diagnostic_out="$project/results/nvfp4-candidate-diagnostic-t16384-$label"
! compgen -G "$diagnostic_out.*" >/dev/null
set -o noclobber
CUDA_VISIBLE_DEVICES=0 "$project/.venv/bin/python" "$project/scripts/run_split_benchmark.py" \
  --repo "$project/candidate" --expected-head "$candidate_sha" \
  --image nvcr.io/nvidia/pytorch:26.05-py3 --tokens 16384 \
  --output "$diagnostic_out.json" > "$diagnostic_out.log" 2>&1
```

Do not start other candidate native imports until the first import/JIT build
completes. That was the original pre-d907 epoch transition. For subsequent checkpoints,
root must confirm the current native epoch; do not infer it from this historical
example or rerun the baseline diagnostic.

## Retained candidate follow-up

If root retains a complete full-grid A1, reuse that exact data and its B1; run
fresh candidate A2, then fresh baseline B2 per mode. Use source epochs to avoid
concurrent native-JIT rebuilds: candidate A2 for all modes completes before the
baseline B2 epoch begins. No B1 or A1 rerun is needed. Existing campaign tools in
`scripts/post-layout/w4a4` and `scripts/unfused-blockscaled` support both
`--reuse-baseline-r1` and `--reuse-candidate-r1` and strict provenance validation;
root must coordinate their epoch boundaries if used concurrently.

Per-token paired ratio is `sqrt(B1 * B2 / (A1 * A2))`. Report the full 13-row table;
compute decode/prefill/overall geometric means from retention tokens only.
Phase diagnostics and fixed-tactic minima are not primary retention results.

## Static readiness checks

`python3 scripts/unfused-blockscaled/check_saved_protocol.py` and
`python3 scripts/post-layout/check_saved_protocol.py` passed before the pending
integration was committed. They check all 7 saved modes, exact retention groups,
changed-timing rejection, preparation-only source normalization, and invalid
layout rejection. Re-run the preparation audit after the final candidate commit.

## Completed d9074cb6 checkpoint

Root authorized and deployed `d9074cb6e9e934d387e358a069e90ddf084f5ef7`.
All three full-grid screens completed on 2026-10-25 UTC; baseline B1 was reused.
NVFP4 and MXFP8 ran concurrently on GPUs 0 and 1, followed by mixed W4A8 on GPU1.
The shared candidate fp4 quantization native build ran once before timing.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 |
| :--- | ---: | ---: | ---: |
| NVFP4 W4A4 | 0.930884x | 0.814472x | 0.897578x |
| MXFP8 | 0.965664x | 0.993616x | 0.973208x |
| MXFP4 × MXFP8 | 0.930436x | 0.973750x | 0.942054x |

The checkpoint still regresses over the retention grid; no A2/B2 repetitions
were launched. Full raw evidence, 39-row tables, and selected tactics are under
`evidence/combined-screen-d9074cb6/`. The raw archive contains 78 files,
1,537,984 bytes, SHA256
`c50a783a371618573554901177c5641d46d7c8cafe1814224bd1d725557f61dc`.
All 39 routing histograms, 78 B1/A1 per-token cache hashes, source/preparation
contracts, timing/software/environment fields, frozen helpers, and driver hash
were verified. GPU0/GPU1 were released after completion.

## Completed 94be9a71 checkpoint

Root authorized and deployed `94be9a712a46ab34b902605c4a34d26a4c570692`.
All three full-grid screens completed on 2026-10-25 UTC with the same frozen
helpers and retained B1. GPU0 ran NVFP4; GPU1 ran MXFP8 followed by mixed W4A8.
The candidate native-JIT epoch was already built and unchanged from d9074cb6.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 |
| :--- | ---: | ---: | ---: |
| NVFP4 W4A4 | 0.968371x | 0.817936x | 0.924794x |
| MXFP8 | 0.995249x | 0.999680x | 0.996456x |
| MXFP4 × MXFP8 | 0.976493x | 0.963775x | 0.973007x |

Decode improves over d9074cb6 by 1.040271x / 1.030637x / 1.049500x respectively,
but every mode still regresses overall against B1. No A2/B2 was launched.
All 39 rows and 78 baseline/candidate cache hashes passed strict verification;
frozen helper/driver hashes and the exact kernel source hash were also verified.
The raw archive has 81 files, 1,542,263 bytes, SHA256
`fac140b23d53b99932fe050c651ad7f4bf167d687ed5108ec0cdc3f1a65658b1`.

Evidence is in `evidence/combined-screen-94be9a71/`, including full raw logs,
summary tables, selected tactics, comparison to d9074cb6, and verification receipt.
The archive explicitly reuses d9074cb6 capability/tactic checks because those
contracts are unchanged. New small-N overlap behavior has 306 paired exact cases
and focused pre-commit validation in `scripts/decode_geometry_experiment/RESULTS.md`.
Core source SHA256:
`581395ff44b3598ff3d0d497b12e4f5326e0ee5d83f525d2bf79e501b317dd0d`.
GPU0/GPU1 were released after archive verification.

## Completed 7829fc00 checkpoint

Root authorized and deployed `7829fc00dc7121341cc40cd4190660507e006490`.
All three full-grid screens completed on 2026-10-25 UTC with the same frozen
helpers and retained B1. GPU0 ran NVFP4; GPU1 ran MXFP8 followed by mixed W4A8.
The candidate native-JIT epoch was already built and unchanged from d9074cb6.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 |
| :--- | ---: | ---: | ---: |
| NVFP4 W4A4 | 0.968347x | 0.845621x | 0.933210x |
| MXFP8 | 0.996139x | 1.018482x | 1.002184x |
| MXFP4 × MXFP8 | 0.972155x | 0.982986x | 0.975097x |

NVFP4 and mixed still regress overall against B1; MXFP8 is approximately at
parity in this single screen. Tokens 1 and 2 were measured and excluded from
the aggregates. No A2/B2 was launched, so this is not an ABBA retention result.
All 39 rows and 78 baseline/candidate cache hashes passed strict verification,
including routing histograms, timing/software/environment fields, frozen helper
hashes, driver hash, preparation contracts, and both changed source hashes.

Evidence is in `evidence/combined-screen-7829fc00/`, including full raw logs,
`raw-medians.md`, summary tables, selected tactics, comparison to 94be9a71, and
`verification.json`. The raw archive has 82 files, 1,543,316 bytes, SHA256
`c1be0474ee40d6c1abc52651bf4b1092644fd892d4069b20c3dcdb8c28430843`.
The archive explicitly reuses d9074cb6 capability/tactic checks because those
contracts are unchanged. Root separately reports 24 paired exact FC1 producer
reorder cases, 98 paired exact FC2 bulk-store checks, and focused pre-commit
validation for the two changed production files.

Core source SHA256:
`abb740d378d104cd7c2d3b26937328716b72a93b9d3c8910f8a37cb306421009`.
Epilogue utility source SHA256:
`c005604ae1385fccfd60b3adbb314e305cc0d8337b4642e5d10586106d7555b2`.
GPU0/GPU1 were released after archive verification.

## Completed 13ca1475 checkpoint

Root authorized and deployed `13ca1475d96839f3bf3c46699cc63204b4d3b409`.
All three full-grid A1 screens completed with the frozen helpers and existing
B1, GPU0 for NVFP4 and GPU1 for sequential MXFP8/mixed. No A2/B2 was launched.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 |
| :--- | ---: | ---: | ---: |
| NVFP4 W4A4 | 0.994551x | 0.918510x | 0.973209x |
| MXFP8 | 1.062953x | 1.035364x | 1.055357x |
| MXFP4 × MXFP8 | 1.074825x | 1.002396x | 1.054568x |

NVFP4 still regresses overall/prefill; MXFP8 and mixed improve in this single
screen. The full 39 rows, 78 cache hashes, routing, frozen helpers, driver,
preparation/timing contracts, and seven changed Git-source hashes were verified.
All five changed production-source hashes match all three run manifests.
The current capability/validation log reports 56 passed and four deprecation
warnings and is archived instead of reusing old capability evidence.

`evidence/combined-screen-13ca1475/` contains full raw evidence, summary, tactics,
comparison against 7829fc00, and verification receipts. Archive: 83 files,
1,556,844 bytes, SHA256
`7ec0f63fbb8ca368d6167e6b843235cb3f702cea1bd4be749ca7727493a549a4`.
The new M512/N128 FC1 tactic is selected at T8192 and T16384 for all three
modes. All 39 measured sizes have exact AUTO buckets; earlier bucket profiles
are preserved unchanged throughout each full sweep. GPUs0/1 were released.

## Completed 442d2aa5 checkpoint

Root authorized, pushed and deployed
`442d2aa53f68b4640c3ab5118a76f1599ff60d34`. Current host capability/tactic/
architecture checks passed (56 passed, four warnings, 0.27s), followed by serial
candidate native readiness for MoE utils, FP4 and MXFP8 quantization. No native
cache reset or baseline rerun occurred. The three A1 sweeps completed on
2026-10-25 UTC using GPU0 for NVFP4 and GPU1 for sequential MXFP8/mixed.

| Mode | Decode B1/A1 | Prefill B1/A1 | Overall B1/A1 |
| :--- | ---: | ---: | ---: |
| NVFP4 W4A4 | 1.057669x | 0.956047x | 1.028928x |
| MXFP8 | 1.094339x | 1.092435x | 1.093820x |
| MXFP4 × MXFP8 | 1.149295x | 1.039251x | 1.118177x |

All modes improve overall in this one screen. NVFP4 prefill still regresses;
T16384 B1→A1 is 472.464→532.351us. Mixed T16384 also regresses,
776.002→816.481us, despite its positive prefill aggregate. Tokens 1 and 2 were
measured but excluded from all aggregates. No A2/B2 was authorized or launched.

All 39 rows, 78 B1/A1 cache hashes, routing histograms, timing/software/runtime
environment, frozen helpers, preparation contracts, log receipts, and four
changed production-source hashes were verified. All measured token sizes have
exact AUTO buckets, and earlier profiles remain unchanged in the final cache.
The finalizer is explicitly recorded as measured production, with old/new
hashes and a full diff; the other original protected setup invariants remain.

Evidence: `evidence/combined-screen-442d2aa5/`, including complete raw medians,
selected tactics, comparison with 13ca, and verification receipts. Raw archive:
96 files, 1,565,238 bytes, SHA256
`6f4ffcf8bfd00449008b9e2d8cf133ec02d66f726f0825ceb1f447f6c95d48b4`.
The root separately archives 72 paired phase cases and 15 native exact
configurations for the composed overlay. Broad numerical/sanitizer validation
remains deferred. GPU0/GPU1 were verified idle and released after completion.
