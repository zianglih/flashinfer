# W4A16 mixed-cluster performance evidence — current draft

This local bundle contains a **partial token grid and no established speedup** for preferred4/fallback2 W4A16 MegaMoE. It is performance iteration evidence, not numerical, deadlock, sanitizer, graph-lifecycle, or release qualification. Nothing in this bundle has been published.

The completed pairs cover global T32/T128/T512/T4096/T16384. The broader token grid remains incomplete. The middle pair is a single ordered screen and is not pooled into a later full-grid result. One serial process sweep per arm/point provides descriptive measurements; it is not a statistical significance or independent-repeat claim. Earlier candidate experiments, fixed-tactic measurements, profiler samples, and incomplete captures are excluded.

| Global tokens | Baseline median (us) | Candidate3r median (us) | Baseline/candidate |
|---:|---:|---:|---:|
| 32 | 144.193 | 144.817 | 0.99569 |
| 128 | 168.370 | 165.7295 | 1.01593 |
| 512 | 175.954 | 177.010 | 0.99403 |
| 4096 | 401.843 | 405.6205 | 0.99069 |
| 16384 | 1228.877 | 1244.425 | 0.98751 |

**Policies and fixture.** Baseline runs the original 16 native AUTO candidates with the wrapper's `all` policy. Candidate3r runs AUTO over only the new 18 preferred4/fallback2 tactics selected from its product catalog of 34; the original 16 product tactics remain available outside this benchmark filter. Both arms use identical captured native-driver and policy-wrapper bytes. This compares tuning policies, not fixed or tactic-matched configurations. All eight rank winners and candidate counts/hashes are preserved in every run's `raw-records.json`. The synthetic GLM5 routed-expert core uses D6144, intermediate 2048, 256 experts, top8, SwiGLU, EP8, BF16 activations, and NVFP4 weights. Fixture details and seeds are in `fixture.json`. Precomputed routing excludes the router from timing; this is not an end-to-end model benchmark.

**Timing.** Each point retains all 100 cold-L2 CUPTI/CUDA-graph samples after 3 warmups. Each sample is the per-iteration maximum rank activity span, **including gaps and overlap**; the reported latency is the median of those 100 rank-MAX samples. Preparation, AUTO tuning, warmup, graph capture, routing preparation, and L2 flushing are untimed. The large sample-zero values are retained without trimming, dropping, winsorizing, or replacement. `raw-records.json` and `summary.json` are exact byte copies of the completed captures, including order, every sample, policy receipts, and tactic receipts. No pooled grid aggregate is claimed.

**Environment.** Eight NVIDIA B300 SXM6 AC GPUs, 148 SMs/GPU, CC10.3, GPU-pair topology NV18; image `nvcr.io/nvidia/pytorch:26.05-py3`. The actual host driver recorded by `nvidia-smi` is 595.91.07. The container's `CUDA_DRIVER_VERSION` environment value is 595.58.03; both are preserved as different fields. Runtime: PyTorch `2.12.0a0+5aff3928d8.nv26.5.50603568`, CuTe DSL 4.7.1, CUDA 13.2, CUDA Python/CUPTI Python 13.2.0, CUPTI package 13.2.86, NVSHMEM 3.6.5, nvshmem4py 0.3.1. Full setup and per-run package receipts are included.

**Files and extraction.** `index.json` lists the six completed arm captures. `sources/` holds exact captured repository-relative source manifests, original source patches, source status, submodule revisions, and manifest-verified untracked implementation additions. `recipe/` contains frozen captured `run.py`, `policy_driver.py`, `compare.py`, the identical native driver, and its manifest-verified sibling import. Every run's `metadata.json` retains captured helper hashes, runtime versions, completion state, source hashes, and controlled flags, with private machine paths replaced by explicit parameters. `extraction-log.json` records each byte copy and metadata extraction. Raw logs, connection metadata, host identifiers, process lists, NIC identities, and private paths are excluded. `validation.json` records byte/hash, sample-preservation, and public-content checks; `SHA256SUMS` covers the resulting files.

**Source identity.** Both checkouts started at `316faec37a4706a2ecc7d46265087f8190b40baa`. Baseline is pristine. Candidate3r is that base plus the exact captured patch and implementation additions in `sources/candidate3r/`; the shared native driver is the captured modified driver for both arms. At capture time, the candidate edits were not committed. They have since been committed as `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`; the original base-plus-patch receipts remain the identity of these iteration captures. The manifests cover `flashinfer/` and `benchmarks/`, not every repository file; untracked test files are outside this captured manifest and are not bundled. Reproduction must use the captured source state, not the current tip of a future PR.

**Legacy common-cache boundary.** These captures share common CUDA-driver, CuTe DSL, and Triton cache roots. Both arms set the same `FLASHINFER_WORKSPACE_BASE`, sharing FlashInfer's version/architecture workspace under that base, as well as the CUDA-driver, CuTe DSL, and Triton cache roots. The captured source reads `FLASHINFER_WORKSPACE_BASE` and derives the Python variable `FLASHINFER_WORKSPACE_DIR` as `<base>/.cache/flashinfer/<version>/<target-architectures>`; it does not read a `FLASHINFER_WORKSPACE_DIR` environment override. The reproduction helper preserves this legacy behavior and uses one explicit common cache path for both arms. A later separate-workspace cache policy is not represented here. Initial cache contents and all preceding compile history were not snapshotted, so the command reproduces the recorded policy and timing method, not an identical starting cache state or guaranteed timings.

To reconstruct the sources in a new Linux workspace, use two independent checkouts, checkout the base above in each, initialize their pinned submodules, apply `sources/candidate3r/source-before.patch` to the candidate, and copy `sources/candidate3r/additions/` into its root. Verify the resulting files against the corresponding source manifest. Use the exact prepared image and preserve its PyTorch. The remaining runtime package pins are in `recipe/runtime-requirements.txt`; install them with `python3 -m pip install --no-deps -r "$BUNDLE/recipe/runtime-requirements.txt"` in that container if needed.

The following parameterized commands run new AUTO measurements; they were not executed while preparing this publication bundle. Choose fresh output paths and reserve the eight GPUs for serial runs:

```sh
BUNDLE=/path/to/current-draft
BASELINE_SOURCE=/path/to/base-checkout
CANDIDATE_SOURCE=/path/to/candidate3r-checkout
OUTPUT_ROOT=/path/to/new-results
COMMON_CACHE=/path/to/common-compile-cache
bash "$BUNDLE/recipe/reproduce.sh" "$BASELINE_SOURCE" "$CANDIDATE_SOURCE" \
  "$OUTPUT_ROOT" "$COMMON_CACHE" 32,4096 short
bash "$BUNDLE/recipe/reproduce.sh" "$BASELINE_SOURCE" "$CANDIDATE_SOURCE" \
  "$OUTPUT_ROOT" "$COMMON_CACHE" 16384 t16384
# Middle pair, kept separate from the short/endpoint captures:
bash "$BUNDLE/recipe/reproduce.sh" "$BASELINE_SOURCE" "$CANDIDATE_SOURCE" \
  "$OUTPUT_ROOT" "$COMMON_CACHE" 128,512 middle
```

The frozen capture helpers write full local provenance and logs for new runs, which may contain machine-specific paths. Apply the same metadata extraction before sharing new outputs publicly; the raw measurement JSON itself must remain unchanged.
