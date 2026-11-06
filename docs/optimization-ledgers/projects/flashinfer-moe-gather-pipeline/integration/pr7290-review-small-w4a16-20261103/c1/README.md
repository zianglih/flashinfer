# B200 W4A16 small-token review

Completed on C1 `fi-pr7290-small-w4-b200-1103`, NVIDIA B200 / SM100, using `nvcr.io/nvidia/pytorch:26.05-py3`. The original test devbox had disappeared; after the user renewed Google SSO, a replacement bare 8-GPU devbox was allocated in namespace `ziangli`. Persistent source, Python environment and CUDA 13.2 compilation caches survived.

## Sources and contract

- Before: `002529e17b22567a071091053c6c4dc2a55e050e`, original 64-row weight layout, with the existing benchmark-only `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab` adapter.
- Current OFF / ON: `14a338579eb8acddcc5cfd1cc58871fc0788de22`, respectively compatible old layout / new swap-AB layout. Benchmark source was immutable and separate from host-review changes.
- V3 EP8/TP8, V41F EP4/TP4, K3 EP8/TP8, N3U EP8/TP8; tokens 4, 8 and 16. TP and EP labels describe rank-local benchmark shapes, without communication.
- Functional W4A16 BF16 input, unfused finalization. Before/OFF use the same published baseline choices; ON uses published retained swap-AB choices. Runtime metadata is explicitly rebound to B200; this fixed-choice replay does not claim B200-optimal tactics.
- Per job, all six phases run on one GPU: before, OFF, ON, ON, OFF, before. Strict CUPTI cold-L2 CUDA graphs, 10 warmups and 100 samples per case/phase. No timing fallback, retuning, source mutation or silent tactic fallback in the fixed matrix.

The baseline archive reused only source from the earlier CUDA 13.0 campaign; no CUDA 13.0 compiled artifacts were imported. Source inventory normalization corrected historical PAX long-path documentation placement in new task-owned copies. Source postflight verifies 31,069 baseline and 34,762 current tracked files, with zero mismatches. The earlier validated donor was preserved.

Runtime: Torch `2.12.0a0+5aff3928d8.nv26.05`, Torch CUDA 13.2, system NVCC 13.2.78, CuTe DSL 4.8.0, TVM-FFI 0.1.14.post1, CUPTI Python 13.2.0 / library 13.2.86, CUDA Python/bindings 13.2.0. CuTe's bundled compiler reports CUDA 13.4; this is distinct from system NVCC. Native modules compiled normally outside timed samples and remain on persistent storage.

## Fixed-choice results

All 8 jobs / 48 phases passed: 24 cases per arm and 14,400 raw CUPTI samples. Independent local replay reconstructs every sample from activity correlation IDs and verifies exact medians, cached choices, routes, output hashes and source postflight.

| Current mode | Geometric-mean speedup vs before |
| --- | ---: |
| OFF | +2.149% |
| ON | +2.965% |

Maximum before/after repeat spread across all 72 arm/cells was 0.541%. These aggregate gains coexist with specific small-token EP regressions. Full values and raw evidence remain in `fixed-audit.json`, `fetched-metadata/fixed-summary.json` and `results/`.

## Fresh-native V3 EP8 token-4 confirmation

Separate public autotuning, with fresh per-arm caches, made 69 / 72 / 72 profile calls for before / OFF / ON. Tuning runs are excluded from the balanced timing result. The selected choices were then replayed in the same six-phase order on GPU1.

| Arm | Repeated-median geometric mean | Speedup vs before |
| --- | ---: | ---: |
| Before | 50.904 µs | — |
| OFF | 54.224 µs | −6.123% |
| ON | 53.696 µs | −5.200% |

All 600 replay samples pass independent CUPTI reconstruction. Maximum repeat spread is 0.119%. Native retuning did not eliminate this cell's regression. These results are separate from the fixed matrix and do not replace its values.

- Before / ON winner: FC1 and FC2 `(128,16,256)`, cluster `(1,1)`, raster M.
- OFF winner: FC1 `(256,32,256)`, FC2 `(128,32,256)`, cluster `(2,1)`, raster M.

Full tuning candidates, costs, winners, raw timing and telemetry are under `fresh-native-v3-t4/`; the compact audit is `fresh-native-audit.json`.

## Review validation

Separate review trees preserved benchmark sources and autotune caches:

- Four new autotune cases passed: W4A4 / W4A16, swap-AB OFF / ON. Exact test snapshot `6f528fafb72b9728bbf696cd7fbddc040f7735f72490b5c496c7a6452da8be93`; `autotune-audit.json` and `evidence/autotune-test/` retain the output and JUnit.
- Six-file host-review snapshot: 12 guard/CPU/packing checks, eight typed NVFP4 cases across both layouts and four activations, and one actual MXFP4×MXFP8 gated deterministic accuracy case passed. No failures or skips. `review-tests-audit.json` verifies all six files against the canonical review snapshot; complete output/JUnit is under `evidence/guard-tests/`.

No sanitizer, source commit, push or public update was performed by this worker.

## Evidence and replay

- `fetch-full.json`: eight compressed raw-job archive hashes; original filenames and outputs preserved in `results/`.
- `archives/fixed-metadata.tar.gz`: actual config, source manifests/postflight, imported choices and global receipt.
- `archives/fresh-native-v3-t4.tar.gz`: separate native tuning plus balanced replay; SHA256 `61d388e4fd5e32a557c527bf50c80471b2394d06c97f4e408bb03fcd0637d446`.
- `pilot/ep-v3-w4a16/`: separate qualification run, excluded from full-matrix values.
- `payload/`, `configure.remote.py`, `launch-full.remote.py`, `launch-fresh.remote.py`, `launch-fresh-replay.remote.py`: exact harness/setup commands.
- `audit-fixed.py`, `fetch-fresh.py`: independent raw timing replay checks.

All artifacts are under this task locally and the matching `/data/ziangli/flashinfer-moe-gather-pipeline/integration/pr7290-review-small-w4a16-20261103/c1` path remotely. GPU work ended after the fresh-native replay; no further launches are pending.
