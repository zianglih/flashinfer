# C1 validation: post-topK compilation for `moe_utils`

## Scope and revisions

The fresh timing campaign compared merged #4082 directly with the final
macro-free source-owned implementation on top.

- Measured merged #4082 baseline: `fb28d7242b3506a2348265962041acc1fb56cca4`
- Measured candidate / current PR head:
  `4a17da2169e96559e1321524c5186d81f6880fd8`
- Review range: `fb28d7242b3506a2348265962041acc1fb56cca4..4a17da2169e96559e1321524c5186d81f6880fd8`
- Direct delta: 14 files, 381 insertions, 213 deletions
- Stable patch ID: `656c0b9a3152243ad3d5d8cf64837e6b003f7370`

The current binding constructs a zero-initialized `routingCustom::Data`
descriptor and uses the shared post-topK routing/permutation pipeline. Because
`moe_sort` always receives precomputed top-k IDs and weights, its binding calls
`runPostTopKPipeline` directly and `gen_moe_utils_module()` selects four
post-topK routing wrappers.

The new wrappers mirror the block, small-cluster, large-cluster, and entry
translation-unit split introduced by #4635. Each wrapper source owns its
launcher definitions: generic sources retain runtime policy dispatch, while
the policy-bearing post-topK block/cluster sources instantiate only
`NoOpPreprocess + SoftmaxPostprocess`.
Cooperative, histogram, offset, and cluster-selection launchers live in one
implementation header included by exactly one entry translation unit per JIT
module; the shared cooperative/utility launchers retain their existing
`NoOpPreprocess + NoOpPostprocess` instantiations. Kernel algorithm templates
remain shared, and each module preserves the same launcher signatures. There
is no post-topK build-mode selector or caller-specific JIT definition.

The generic `trtllm_gen_routing` source list introduced by #4082 is unchanged.
It continues to compile the DeepSeek, Llama4, and generic custom-routing source
family with the same runtime dispatch. `RoutingCustomPolicy.cuh` is unchanged;
`trtllm_fused_moe_routing_common.cu` changes only its launcher-ownership
comment. There is no Python API, FFI registration/signature, or output-layout
change.

## Direct-call-only control

In a separate, earlier control campaign, the binding called
`runPostTopKPipeline` directly and only the DeepSeek routing source was removed
from `moe_utils`. One isolated cold build/load took 193.865 seconds; that
campaign's repeated #4082 baseline mean was 194.635 seconds, so the control
produced no meaningful wall-time improvement. The raw control record is under
`isolated-no-macro-c1b/output.log`; the fresh campaign below used exact-source
workspaces.

Removing the roughly 53-second DeepSeek object did not shorten the critical
path: the four generic custom-routing objects still took approximately 98 to
186 seconds and instantiated the full policy/tier matrix. This establishes that
the gain comes from narrowing the dominant wrapper translation units, not from
replacing one runtime function call.

There is no JIT, caller-specific, or post-topK specialization flag. Launcher
ownership is expressed by the selected source family; only entry launchers that
are genuinely shared live in a common implementation header.

Representative exact-final Ninja object intervals show where the wall-time
gain comes from:

| Routing object | #4082 (s) | Candidate (s) |
|---|---:|---:|
| block | 158.275 | 48.798 |
| small cluster | 159.612 | 66.141 |
| large cluster | 184.996 | 59.239 |
| entry | 98.614 | 46.739 |
| DeepSeek score routing | 52.905 | not built |
| common | 14.745 | 14.890 |

These objects compile in parallel under `MAX_JOBS=4`; the intervals explain
the critical path and should not be summed.

## W4A4/W4A16 applicability trace

The specialization is based on the precomputed-routing interface, not on an
activation or weight quantization mode:

- W4A4 per-tensor and per-token execution selects
  `CuteDslFusedMoENvfp4Runner`, enters `_moe_core_impl`, and calls the shared
  `moe_sort` helper.
- W4A16 execution selects `CuteDslFusedMoEW4A16Runner`, enters
  `launch_w4a16_moe`, and calls the same `moe_sort` helper.
- `moe_sort` builds `gen_moe_utils_module()` and invokes
  `flashinfer_moe_sort`. Its native binding accepts route IDs, route weights,
  routing shapes, the expert-parallel window, PDL, and output mappings; it has
  no activation- or weight-quantization field.
- The fourteen-file candidate delta contains no W4A16-specific branch or
  literal.

The resulting scope is the shared SM10x `CuteDslMoEWrapper` /
`cute_dsl_fused_moe_nvfp4` W4A4 and W4A16 pipeline. This does not claim that
other W4A4 implementations, including the separate SM12x/B12x path, use this
JIT module.

## Environment

- Cluster/devbox: C1 / `fi-cutedsl-source-owned`, namespace `infra`
- Host: `B200-130`
- Hardware used: 1 NVIDIA B200 (`CUDA_VISIBLE_DEVICES=0`), SM100, 148 SMs
- Image: `nvcr.io/nvidia/pytorch:26.05-py3`
- Runtime image ID reported by the C1 pod:
  `nvcr.io/nvidia/pytorch@sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba`
- Driver: 580.126.09
- Python: 3.12.3
- PyTorch: `2.12.0a0+5aff3928d8.nv26.05`
- PyTorch CUDA: 13.2
- nvcc: `Build cuda_13.2.r13.2/compiler.37668154_0`
- NVIDIA CuTe DSL: 4.7.0
- TVM FFI: 0.1.13.post3
- FlashInfer package version: 0.6.18

The devbox was requested with the explicit image and `--bare`; it remains
running. The macOS-managed `/usr/local/bin/h` 0.2.43 was used for every C1
operation.

## Controlled cold-JIT method

The end-to-end measurements used the same B200 and were serialized. Isolated
`moe_utils` and W4A16 used A/B/A/B order; W4A4 used one fresh A/B confirmation
pair. Every observation used a fresh Python process and a unique empty
`FLASHINFER_WORKSPACE_BASE`. The artifact/header cache was preseeded and shared
through the same `FLASHINFER_CUBIN_DIR`, avoiding download variance. CuTe DSL
and other machine-level caches were also shared by both arms. Therefore the
comparison makes FlashInfer's native JIT cold and isolates this `moe_utils`
source/template delta; it is not a fully cold-machine claim.

Production compile controls:

```bash
export CUDA_VISIBLE_DEVICES=0
export FLASHINFER_CUDA_ARCH_LIST=10.0a
export MAX_JOBS=4
export FLASHINFER_NVCC_THREADS=1
export FLASHINFER_JIT_VERBOSE=0
export FLASHINFER_JIT_DEBUG=0
export FLASHINFER_DISABLE_VERSION_CHECK=1
unset FLASHINFER_DISABLE_JIT
```

`FLASHINFER_JIT_VERBOSE=1` was deliberately not used: in this revision it also
enables JIT debug compilation (`-G -O0`) through `gen_jit_spec()` and is not a
production timing configuration.

Shared artifact cache:

```text
/hai-workspace/fi-source-owned-validation/cubins
```

## Existing W4A4 CuTe DSL MoE cold first-run time

The exact same existing W4A4-only test ran before and after:

```bash
python3 -m pytest -q \
  'tests/moe/test_cute_dsl_fused_moe.py::TestMoeSortBufferInitPoisoned::test_wrapper_with_poisoned_moe_sort_buffers[1-256]'
```

It uses W4A4 per-tensor quantization, 256 tokens, hidden size 256, intermediate
size 512, 256 local experts, top-k 8, EP1, and route tile 128. It selects the
fixed default B200 W4A4 tactics rather than invoking the autotuner. The reported
wall time is end-to-end pytest startup, compilation, first execution, and
assertion time.

| Order | Revision | pytest time (s) | Wrapper wall (s) | Child user (s) | Child sys (s) | Peak RSS (KiB) |
|---|---|---:|---:|---:|---:|---:|
| A1 | merged #4082 | 241.00 | 244.034531 | 729.311933 | 22.086493 | 1,833,096 |
| B1 | source-owned candidate | 118.18 | 121.282397 | 301.994650 | 17.013674 | 1,758,584 |

Wrapper wall time improved by **122.752134 seconds**, from 244.034531 to
121.282397 seconds: **50.3011% lower**, or **2.0121x faster**. Child user CPU
time was 58.59% lower. This is compilation/first-run evidence, not kernel
runtime performance.

Raw timing summaries and wrapper JSON:

```text
A1
1 passed, 112 warnings in 241.00s (0:04:01)
{"child_maxrss_kib": 1833096, "child_system_s": 22.086493, "child_user_s": 729.311933, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestMoeSortBufferInitPoisoned::test_wrapper_with_poisoned_moe_sort_buffers[1-256]"], "returncode": 0, "wall_s": 244.0345314303413}

B1
1 passed, 112 warnings in 118.18s (0:01:58)
{"child_maxrss_kib": 1758584, "child_system_s": 17.013674, "child_user_s": 301.99465, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestMoeSortBufferInitPoisoned::test_wrapper_with_poisoned_moe_sort_buffers[1-256]"], "returncode": 0, "wall_s": 121.28239695169032}
```

## Existing W4A16 CuTe DSL MoE cold first-run time

The exact same existing test ran before and after:

```bash
python3 -m pytest -q \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]'
```

It uses 33 tokens, hidden size 256, intermediate size 512, 8 experts, top-k 2,
route tile 32, and mixed 1/2-CTA W4A16 tactics. The reported wall time is
end-to-end pytest startup, compilation, first execution, and assertion time.

| Order | Revision | pytest time (s) | Wrapper wall (s) | Child user (s) | Child sys (s) | Peak RSS (KiB) |
|---|---|---:|---:|---:|---:|---:|
| A1 | merged #4082 | 240.64 | 244.167043 | 726.829076 | 22.401692 | 1,835,088 |
| B1 | source-owned candidate | 117.92 | 121.352280 | 299.812712 | 16.945436 | 1,764,972 |
| A2 | merged #4082 | 242.81 | 246.205758 | 729.628651 | 22.082143 | 1,836,924 |
| B2 | source-owned candidate | 117.26 | 120.620748 | 299.935187 | 16.972199 | 1,764,800 |
| Mean | merged #4082 | 241.73 | **245.186400** | 728.228864 | 22.241918 | 1,836,006 |
| Mean | source-owned candidate | 117.59 | **120.986514** | 299.873950 | 16.958818 | 1,764,886 |

Mean wrapper wall time improved by **124.199886 seconds**, from 245.186400 to
120.986514 seconds: **50.6553% lower**, or **2.0266x faster**. Child user CPU
time was 58.82% lower. This is compilation/first-run evidence, not kernel
runtime performance.

Raw timing summaries and wrapper JSON:

```text
A1
1 passed, 70 warnings in 240.64s (0:04:00)
{"child_maxrss_kib": 1835088, "child_system_s": 22.401692, "child_user_s": 726.829076, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]"], "returncode": 0, "wall_s": 244.1670428980142}

B1
1 passed, 70 warnings in 117.92s (0:01:57)
{"child_maxrss_kib": 1764972, "child_system_s": 16.945436, "child_user_s": 299.812712, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]"], "returncode": 0, "wall_s": 121.35227965656668}

A2
1 passed, 70 warnings in 242.81s (0:04:02)
{"child_maxrss_kib": 1836924, "child_system_s": 22.082143, "child_user_s": 729.628651, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]"], "returncode": 0, "wall_s": 246.20575772970915}

B2
1 passed, 70 warnings in 117.26s (0:01:57)
{"child_maxrss_kib": 1764800, "child_system_s": 16.972199, "child_user_s": 299.935187, "command": ["python3", "-m", "pytest", "-q", "tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]"], "returncode": 0, "wall_s": 120.62074816320091}
```

## Isolated `moe_utils` cold build/load

The isolated helper imports FlashInfer, constructs
`gen_moe_utils_module()`, and times only `spec.build_and_load()`:

```bash
python3 tools/bench_moe_utils_compile.py
```

| Order | Revision | Build/load (s) | Total process interval (s) | Child user (s) | Child sys (s) | Peak RSS (KiB) |
|---|---|---:|---:|---:|---:|---:|
| A1 | merged #4082 | 193.250064 | 195.158743 | 670.088806 | 16.924010 | 1,836,228 |
| B1 | source-owned candidate | 71.521584 | 73.968224 | 241.156824 | 12.844921 | 1,435,648 |
| A2 | merged #4082 | 195.338605 | 197.276954 | 668.136111 | 17.549271 | 1,838,508 |
| B2 | source-owned candidate | 72.346767 | 74.282780 | 241.801897 | 13.071671 | 1,435,648 |
| Mean | merged #4082 | **194.294334** | 196.217849 | 669.112459 | 17.236641 | 1,837,368 |
| Mean | source-owned candidate | **71.934176** | 74.125502 | 241.479361 | 12.958296 | 1,435,648 |

Mean build/load time improved by **122.360159 seconds**: **62.9767% lower**,
or **2.7010x faster**. Peak RSS was 21.86% lower.

Inner helper records:

```text
A1 {"build_load_s": 193.25006359629333, "child_maxrss_kib": 1836228, "child_system_s": 16.92401, "child_user_s": 670.088806, "import_s": 1.854558078572154, "spec_s": 0.05412162560969591, "total_s": 195.15874330047518}
B1 {"build_load_s": 71.5215839985758, "child_maxrss_kib": 1435648, "child_system_s": 12.844921, "child_user_s": 241.156824, "import_s": 2.3918502628803253, "spec_s": 0.05478984583169222, "total_s": 73.96822410728782}
A2 {"build_load_s": 195.33860528748482, "child_maxrss_kib": 1838508, "child_system_s": 17.549271, "child_user_s": 668.136111, "import_s": 1.8825766574591398, "spec_s": 0.05577211454510689, "total_s": 197.27695405948907}
B2 {"build_load_s": 72.34676724579185, "child_maxrss_kib": 1435648, "child_system_s": 13.071671, "child_user_s": 241.801897, "import_s": 1.878258178010583, "spec_s": 0.057754297740757465, "total_s": 74.28277972154319}
```

The isolated metric starts after import and JIT-spec construction; neither
interval is included in `build_load_s`.

## Compiled-surface audit

The final isolated A1/B1 workspaces independently confirmed the intended
compiled surface:

| Artifact | #4082 | Candidate |
|---|---:|---:|
| CUDA object build edges | 9 | 8 |
| `moe_utils.so` bytes | 12,382,280 | 5,680,624 |
| Build-directory file bytes | 32,220,922 | 14,808,052 |
| Routing wrappers | four generic wrappers | four post-topK wrappers |
| DeepSeek source in `build.ninja` | yes | no |
| Caller-specific JIT compile flag | none | none |

The candidate still emits the block, dynamic-block, small/large-cluster,
cooperative, init, histogram, offset, and post-topK pipeline symbols.
`RoutingCustomPolicy.cuh` is unchanged; the common source differs only in its
launcher-ownership comment. `routingCustom::run`, `launchHistogramScoresKernel`, and
`launchBlockScoresKernel` are absent, and there are no unresolved routing
symbols. The separately compiled current-candidate `trtllm_gen_routing`
artifact retains #4082's DeepSeek, Llama4, four generic-wrapper, and
common-source list. Its fresh `build.ninja` has 9 CUDA edges, points at the
candidate source tree, and has no specialization flag; the resulting DSO is
11,486,312 bytes.

## Semantic parity and CUDA graph validation

`tools/validate_moe_sort_parity.py` captured each arm from a fresh JIT
workspace. It fails closed unless:

- imported FlashInfer and every actual JIT source resolve under the expected
  source tree;
- the module is JIT rather than AOT and its build directory does not preexist;
- the GPU is B200/SM100 and the production compile controls match the recorded
  environment;
- the final library and `build.ninja` exist and their hashes are recorded.

The matrix covers static block, dynamic block with EP, small cluster, large
cluster with non-power-of-two tile 192, contiguous-window EP at 65,536 tokens,
forced multi-kernel routing above 1,024 experts, PDL on/off, and CUDA graph
capture/replay. Graph outputs are poisoned after capture and reconstructed by a
real replay; a second replay consumes mutated selected-expert IDs through the
same captured pointers and is compared with eager execution.

```text
PASS semantic parity: 10 canonical case result(s) match exactly
baseline=fb28d7242b3506a2348265962041acc1fb56cca4 candidate=4a17da2169e96559e1321524c5186d81f6880fd8
```

The reports recorded 13 baseline versus 12 candidate JIT sources, distinct
library hashes, correct source roots, `is_aot_before_first_call=false`, and the
actual candidate commit rather than a descriptive label.

## Existing targeted tests

The current source tree ran this combined W4A4/W4A16 regression set against
warmed module caches:

```bash
python3 -m pytest -q \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_finalize_handles_cluster_padding_and_partial_tiles[256-w4a4-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslFusedMoeFunctional::test_deterministic_finalize_numerical_accuracy[swiglu-per-tensor]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep[8-w4a4-per-token-False]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a4-per-tensor-True]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestMoeSortBufferInitPoisoned::test_wrapper_with_poisoned_moe_sort_buffers[32-256]' \
  'tests/moe/test_moe_sort_route_windows.py::test_permutation_is_a_bijection_over_local_routes[256-at-threshold]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoeW4A16::test_route_tile_boundary_accuracy[route32-mixed]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestExpertParallelism::test_functional_with_ep[8-w4a16-False]' \
  'tests/moe/test_cute_dsl_fused_moe.py::TestCuteDslMoEWrapper::test_wrapper_cuda_graph[256-64-w4a16-False]' \
  'tests/moe/test_moe_sort_route_windows.py::test_permutation_is_a_bijection_over_local_routes[128-at-threshold]'
```

```text
10 passed, 706 warnings in 8.03s
```

This covers fixed W4A4 tactics with cluster padding and partial tiles,
deterministic finalize/unpermute, W4A4 per-token EP with a nonzero expert
offset, W4A4 and W4A16 CUDA graph replay, EP32 poisoned `moe_sort` buffers, the
complete W4A16 route/permute/GEMM path, W4A16 EP8 with a nonzero local-expert
window, and both tile-256 and tile-128 contiguous route-window thresholds.

## Source-owned cleanup validation

The cold W4A4/W4A16 runs above both compiled and passed at the exact candidate
commit, and the ten-test matrix then passed from a warmed candidate workspace.
A single-module AOT-equivalent build used the same `build_jit_specs` and
`copy_built_kernels` helpers as `flashinfer.aot`, compiling and packaging only
`gen_moe_utils_module()`. It compiled all 12 source objects, produced a
5,680,624-byte DSO with SHA-256
`49bb01608f87669a743174c699fd58891484a5b4781524033ab70edf0d00b8c1`, and
loaded it with JIT disabled:

```text
AOT_LOAD_WITH_JIT_DISABLED=PASS
```

The AOT-layout DSO was then exercised on the GPU alongside the current
candidate's generic routing DSO, with `FLASHINFER_DISABLE_JIT=1`, in both load
orders.

## Coexistence with #4082 generic routing

`tools/validate_routing_load_order.py` builds and loads both DSOs from the exact
candidate source tree in both orders. The generic DSO retains #4082's full
source list. Its generic arm uses `SigmoidRenorm`, a raw-score policy excluded
from specialized `moe_utils`, and compares IDs and weights with a Torch
reference before repeating both calls with both DSOs resident.

```text
PASS load order: moe-first
PASS load order: routing-first
tests/moe/test_trtllm_gen_routing.py::test_large_batch_smoke[Renormalize]:
1 passed, 3 warnings in 1.78s
```

## Local checks

```bash
BASE_REV=fb28d7242b3506a2348265962041acc1fb56cca4
HEAD_REV=4a17da2169e96559e1321524c5186d81f6880fd8
pre-commit run --files $(git diff --name-only "$BASE_REV..$HEAD_REV")
git diff --check "$BASE_REV..$HEAD_REV"
```

All applicable hooks passed, including clang-format, mypy, ruff check, and ruff
format. The changed-file hooks and `git diff --check` passed again after the
final cleanup; the repository is clean at the current PR head.

## Limitations and retained artifacts

- Validation is targeted to one B200 with CUDA 13.2; the full repository suite
  and other GPU/toolkit combinations were not run.
- W4A4 and W4A16 applicability is limited to their shared SM10x CuTe DSL MoE
  pipeline. The separate SM12x/B12x W4A4 implementation was not tested and does
  not use this JIT module.
- Timing measures cold FlashInfer JIT build/first load, not steady-state kernel
  latency or throughput.
- Top-k IDs in the semantic harness are unique within each token. Duplicate
  lanes are outside the existing static/dynamic kernel contract exercised here.
- The W4A4/W4A16 timing arms used the same preseeded cubin/header artifact
  cache, and machine-level CuTe DSL caches were shared symmetrically. Every
  FlashInfer JIT workspace for cold timing, parity, and load-order validation
  was unique and initially empty. The 10-case regression matrix intentionally
  reused a warmed candidate workspace and is not timing evidence. Import and
  JIT-spec construction are reported separately and excluded from the isolated
  `build_load_s` metric.
- A single-module `moe_utils` AOT-equivalent build/package/load and AOT-layout
  GPU runtime smoke was exercised; the full FlashInfer AOT/jit-cache package
  build was not run.

Durable remote root:

```text
/hai-workspace/fi-source-owned-validation
```

The exact baseline/candidate sources, unique workspaces, W4A4 A/B and W4A16
A/B/A/B raw logs, JSON provenance reports, binary/build manifests, generic DSO,
and AOT artifact remain on the retained devbox. No devbox was removed.

## Upstream handoff

- Closed test-only draft: https://github.com/flashinfer-ai/flashinfer/pull/4677
- Replacement draft: https://github.com/flashinfer-ai/flashinfer/pull/4678
- Public PR author: `zianglih`
- Head: `zianglih:perf/cutedsl-moe-precomputed-compile`
- Current PR head: `4a17da2169e96559e1321524c5186d81f6880fd8`
- GitHub pre-commit and documentation builds passed. The GPU PR-test matrix was
  skipped pending maintainer/`ci-users` authorization, so its summary check is
  intentionally red; no upstream GPU CI result is claimed.
- The active `gh` account was left as `zianglih`; Git credentials were not
  changed and `gh auth setup-git` was not run.
