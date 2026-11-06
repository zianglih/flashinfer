# PR #5319 benchmark/runtime audit — 2026-09-28

## Result

Use the **full rebased Python and JIT source**, plus current source `csrc`/`include`, with the official **0.7.0.dev20260923** wheel set. Do not reuse the September 17 three-file overlay or link current Python to the September 23 wheel's entire `data` directory: current `moe_sort` has a changed native ABI.

The latest SM103 provider still omits the shared MoE helpers, so one first-use build of current `moe_utils`, routing, and timing helpers is expected. The available prebuilt `fp4_quantization_103` can remain installed; its seven native source files and generator body are unchanged between the nightly build and current upstream. This is a source-level compatibility finding, not a GPU validation result.

No repository source edits, installations, GPU provisioning, GPU execution, or GitHub operations were performed for this audit. Parent owns the in-progress rebase; all comparisons below use pinned Git objects rather than the changing worktree.

## Source identities and benchmark history

| Role | Commit |
|---|---|
| Previous PR base | `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095` |
| Previous PR head | `f9dd3c10541e087b716772245a9d033499745048` |
| Current upstream audited | `07e519fcc149f39e6dd00264149c092c2e37767e` |
| Latest common nightly wheel build | `b395280a5bc9430244f19be5b905407d5756c1eb` |

`benchmarks/bench_moe_deepseek.py` is **byte-identical between the old base and current upstream**. `git log eb5f05be..07e519fc -- benchmarks/bench_moe_deepseek.py` is empty; its Git blob is `2a68baa4261e67ad1ca713fbc386f7874665a066`, SHA256 `179dba809d7b6c75990d322026519c163b9bbfa4a689ddd3bafa717f540fc815`. The old PR head's benchmark blob is `41010ad5c422d7e39e41bb247dddca3324be227e`.

The PR's CUTLASS finalize wiring is **not already upstream and not superseded**. The old-head diff still adds:

- `use_fused_finalize=True` to `bench_cutlass` and forwards it to `cutlass_fused_moe`.
- Forwarding from `_benchmark_single`.
- CUTLASS-specific help/header text explaining that true allows fused tactics but does not force them.

Current upstream `bench_cutlass` omits that argument, so `--no-fused-finalize` changes CuTe but still leaves CUTLASS at its library default. Retaining the old PR's small forwarding patch is meaningful if CUTLASS remains within the intended PR scope. It has no effect on a CuTe-only run. [Current benchmark](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/benchmarks/bench_moe_deepseek.py#L588), [old PR benchmark](https://github.com/zianglih/flashinfer/blob/f9dd3c10541e087b716772245a9d033499745048/benchmarks/bench_moe_deepseek.py).

Read-only checks:

```bash
git log --oneline eb5f05be..07e519fc -- benchmarks/bench_moe_deepseek.py
git diff eb5f05be 07e519fc -- benchmarks/bench_moe_deepseek.py
git diff eb5f05be f9dd3c -- benchmarks/bench_moe_deepseek.py
git rev-parse eb5f05be:benchmarks/bench_moe_deepseek.py \
  07e519fc:benchmarks/bench_moe_deepseek.py \
  f9dd3c:benchmarks/bench_moe_deepseek.py
```

## Native benchmark contract

Neither `flashinfer/testing/utils.py` nor `flashinfer/autotuner/` changes between the old base and current upstream. The native benchmark call structure and timing method therefore remain unchanged at source level:

- `--backends cutedsl` runs both CuTe W4A4 and W4A16. There is still no native W4A4-only CLI selector; `--use-per-token-activation` changes W4A4 and is ignored for W4A16. The previous external selector patch still matches exactly, but is unnecessary for an ordinary run of both modes.
- Default wrapper path constructs `CuteDslMoEWrapper` with the same named arguments, including `quant_mode`, EP partition, `use_cuda_graph`, and `use_fused_finalize`, then calls `.run` with the same named tensors/scales. `--functional-api` still selects the functional path.
- Warmup/autotuning runs before measurement. Normal measurement calls `bench_gpu_time` with `cold_l2_cache=True`, `enable_cupti=use_cupti`, `use_cuda_graph=use_cuda_graph`, and native input rotation, then returns `np.median(times)`.
- Preserve `FLASHINFER_DIST_AWARE_AUTOTUNE` unset: that opt-in changes the harness to a separate event-timed graph branch. Do not set `--no-cupti` or `--no-cuda-graph` when reproducing the prior method.
- Same workload defaults: H7168/I2048, 256 experts, top-8, 8 groups/top-4 groups, routing scale 2.5, seed 42, routing-bias scale 0.01. EP8 means 32 local experts, offset 0, on one GPU; it does not measure inter-GPU traffic.
- CSV remains `backend,tokens,latency_ms,tflops`; prewarm/JIT/autotune stay outside the reported latency.

Stable source references: [measurement](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/benchmarks/bench_moe_deepseek.py#L244), [CuTe call path](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/benchmarks/bench_moe_deepseek.py#L336), [backend selection](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/benchmarks/bench_moe_deepseek.py#L1175).

A native CuTe-only command, to run against each full source arm with an independent tactic-cache path:

```bash
unset FLASHINFER_DIST_AWARE_AUTOTUNE FLASHINFER_DISABLE_JIT FLASHINFER_DISABLE_VERSION_CHECK
export CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1
TOKENS=1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384
python benchmarks/bench_moe_deepseek.py --backends cutedsl \
  --num-tokens "$TOKENS" --ep 8 --tp 1 --warmup 10 --iters 100 \
  --include-activation-quant --no-fused-finalize \
  --cache /absolute/artifact/path/arm-per-tensor-unfused.json
```

For per-token W4A4 add `--use-per-token-activation`; remove `--no-fused-finalize` for the fused control. Do not silently count repeated W4A16 output from the per-token sweep as independent W4A16 configurations. Keep one forward sweep per explicitly intended configuration and do not mix old results into a new-base table.

The unchanged harness **does not mean the executed CuTe implementation is unchanged**. Current upstream contains large FC1/FC2 changes, prepared launch callbacks, dual-tile routing, and `skip_unpermute`. Use current tests/source and fresh tactics rather than September's copied fixture or fixed tactic cache. The parent is preserving the new bypass/callback paths during rebase. [Current orchestration](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/flashinfer/fused_moe/cute_dsl/fused_moe.py#L255).

## Latest official nightly wheels

Read directly over HTTPS on 2026-09-28; the saved index HTML and `nightly-index-audit.json` are adjacent to this note. Direct requests were used because the browser search cache was older. The newest date common to all four packages was September 23; no September 24–28 package appeared in these live indexes.

| Package | Version | Index |
|---|---|---|
| flashinfer-python | `0.7.0.dev20260923` | [Python nightly](https://flashinfer.ai/whl/nightly/flashinfer-python/) |
| flashinfer-cubin | `0.7.0.dev20260923` | [Cubin nightly](https://flashinfer.ai/whl/nightly/flashinfer-cubin/) |
| flashinfer-jit-cache | `0.7.0.dev20260923+cu130` | [CUDA 13.0 shim](https://flashinfer.ai/whl/nightly/cu130/flashinfer-jit-cache/) |
| flashinfer-jit-cache-sm103a | `0.7.0.dev20260923+cu130` | [CUDA 13.0 SM103 provider](https://flashinfer.ai/whl/nightly/cu130/flashinfer-jit-cache-sm103a/) |

The shim/provider have x86_64 and aarch64 wheels. The `cu132/flashinfer-jit-cache/` and `cu132/flashinfer-jit-cache-sm103a/` indexes both return HTTP 404. For the selected CUDA 13.2 image, use the available +cu130 pair rather than inventing a +cu132 build.

All four wheels' `_build_meta.py` identify `b395280a5bc9430244f19be5b905407d5756c1eb`. The Python and shim wheels were downloaded and their SHA256 values verified against the index. Only ZIP directory/metadata ranges were read for the large cubin/SM103 wheels; their entire content hashes were not verified locally. Their full wheel SHA256 values below are the official index values.

| Wheel, x86_64 where applicable | Index SHA256 |
|---|---|
| Python | `735f49ce8858fea81440507954f37786fb098551ad6097af0d8926c7b46b22ac` |
| Cubin | `f728fd649764962051fcf7065977d44eefe4c7fd689e3381ab9e256ab41eabac` |
| JIT shim +cu130 | `56a7c34f6977cd4e923d670fc3922a962c742339d0907eed030fa43de67a8a1b` |
| SM103a provider +cu130 | `81e4834aece550549c4a6f2af7610a31a9ef870ca937c2b9fbee58377751616e` |

The shim declares dependencies on **all** architecture providers. Explicitly installing only the four packages with `--no-deps` avoids unnecessary architecture downloads. Root must separately satisfy and record runtime dependencies. Current `pyproject.toml`'s CUDA-13 extra requires `nvidia-cutlass-dsl[cu13]>=4.7.0a0`; the base dependency remains `>=4.6.2a0`. Use the CUDA-13 extra floor for this run, not the old 4.6.2 environment by assumption. The nightly's Python METADATA has the same CuTe-extra floor. [Current dependency declaration](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/pyproject.toml#L27).

Exact FlashInfer package pins for the parent to install, if needed (not executed by this audit):

```bash
unset PIP_CONSTRAINT
python -m pip install --no-deps \
  flashinfer-python==0.7.0.dev20260923 \
  flashinfer-cubin==0.7.0.dev20260923 \
  flashinfer-jit-cache==0.7.0.dev20260923+cu130 \
  flashinfer-jit-cache-sm103a==0.7.0.dev20260923+cu130 \
  --index-url https://flashinfer.ai/whl/nightly \
  --extra-index-url https://flashinfer.ai/whl/nightly/cu130
```

## Why nightly data links alone are insufficient

Current Python `moe_sort` unconditionally passes **six new arguments** before the stream pointer: two dual-tile configuration integers and four output pointers. They are still passed as zero/null values when dual-tile mode is disabled. Nightly September 23's native binding predates them. This is an argument-count ABI mismatch, not merely an untested dual-tile feature. The native routing structs and common routing implementation changed with it.

- [Current Python call](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/flashinfer/fused_moe/cute_dsl/moe_utils.py#L867).
- [Current native binding](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/csrc/moe_utils_binding.cu#L354).
- Upstream change: `05ebb2d7`, Kimi-K3 W4A8 MXFP4 SiTU routed MoE, #5430.

The SM103 provider's manifest and ZIP inventory contain **none** of `moe_utils`, `dsv3_fused_routing`, or `trtllm_utils`. They **do** contain `fp4_quantization_103`. Consequently:

1. Keep current source for `flashinfer/jit/`, not a symlink to an older nightly's Python JIT package.
2. Link `flashinfer/data/csrc` to the full current source tree's `csrc`, and `flashinfer/data/include` to its `include`.
3. Current source must build `moe_utils` at first use. The other omitted helpers may also build; do not set `FLASHINFER_DISABLE_JIT`.
4. Prebuilt FP4 quantization remains usable. Its native inputs under `csrc/nv_internal/` and `gen_fp4_quantization_module` are unchanged since the wheel build. The Python quantization change adds `out_scale` specifically to the CuTe per-token path, not the CUDA binding.
5. Current `flashinfer/artifacts.py` also changes `TRTLLM_GEN_BMM` to `4e73ccb74f333ecfebeac52abf3ebe1fa2dd34b3/batched_gemm-b738138-6923fec/`, with checksum `8190fcb70b7661bf11cc5247b98d7fc55153386f969175c196a9e29d5801c7a1`. `gen_moe_utils_module` requests this current artifact's BMM export headers. Keep the current artifact registry and loader, and permit first-use downloads for headers absent from the installed cubin wheel. Do not copy the nightly artifact registry to suppress downloads.
6. Do not claim broad native ABI compatibility for unrelated AOT modules. This audit is scoped to the requested CuTe benchmark and targeted tests.

## Minimal full-source runtime layout

Prefer a fresh full Git source export/checkout of each exact arm, rather than copying changed files into the nightly Python package. Before setting `PYTHONPATH`, obtain the installed wheel's data location with `importlib.metadata.distribution('flashinfer-python').locate_file('flashinfer/data')`; this avoids accidentally importing a source checkout to locate the wheel.

The upstream/nightly Gitlinks for the three shared header dependencies are identical:

| Tree | Gitlink in both nightly build and current upstream |
|---|---|
| `3rdparty/cutlass` | `b46b16d003484063bca4ed365e44095c4c6ed633` |
| `3rdparty/cccl` | `16bd510c9b712e82b0ab6cbb630d8e29ba1f7116` |
| `3rdparty/spdlog` | `c3aed4b68373955e1cc94307683d44dca1515d2b` |

Thus a minimal remote-only layout is:

```text
arm-source/flashinfer/                    full rebased Python package
arm-source/flashinfer/jit/                full rebased JIT Python, not a nightly link
arm-source/flashinfer/data/csrc           -> arm-source/csrc
arm-source/flashinfer/data/include        -> arm-source/include
arm-source/flashinfer/data/cutlass        -> installed-nightly/flashinfer/data/cutlass
arm-source/flashinfer/data/cccl           -> installed-nightly/flashinfer/data/cccl
arm-source/flashinfer/data/spdlog         -> installed-nightly/flashinfer/data/spdlog
```

For a fresh remote source export, this setup creates only the required links and refuses to replace existing files. `SOURCE_ROOT` should name the complete exact-commit source export prepared by the parent; the command is a proposal, not something executed by this audit.

```bash
python - "$SOURCE_ROOT" <<'PY_LINKS'
from importlib.metadata import distribution
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve()
wheel_data = Path(distribution('flashinfer-python').locate_file('flashinfer/data')).resolve()
assert (root / 'flashinfer/__init__.py').is_file()
assert not (root / 'flashinfer/_build_meta.py').exists(), 'Use a fresh source export'
links = {'csrc': root / 'csrc', 'include': root / 'include'}
links.update({name: wheel_data / name for name in ('cutlass', 'cccl', 'spdlog')})
data = root / 'flashinfer/data'
data.mkdir(exist_ok=True)
for name, target in links.items():
    assert target.is_dir(), target
    dest = data / name
    assert not dest.exists() and not dest.is_symlink(), dest
    dest.symlink_to(target, target_is_directory=True)
    print(dest, '->', target)
PY_LINKS
export PYTHONPATH="$SOURCE_ROOT"
# Use a fresh campaign-owned directory; keep it stable after the first build.
export FLASHINFER_WORKSPACE_BASE="$CAMPAIGN_ROOT/runtime-cache"
unset FLASHINFER_DISABLE_JIT FLASHINFER_DISABLE_VERSION_CHECK
```

These are the same five data entries established by `build_backend._create_data_dir`. Avoid invoking the build backend merely to create links: importing it writes build metadata, and editable-install hooks may attempt unrelated EP setup. [Data layout](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/build_backend.py#L1089).

A fresh source export has no `flashinfer/_build_meta.py`. It reports `0.0.0+unknown`; current `jit/env.py` explicitly exempts that source-install sentinel from Python-vs-wheel version checks, while still checking provider-vs-shim versions. This avoids the need to copy stale wheel build metadata or set a broad version-check bypass. Record the **actual Git commit and source hashes** in the validation manifest. Do not describe `0.0.0+unknown` as the source version tested. [Source version fallback](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/flashinfer/version.py#L16), [version checks](https://github.com/flashinfer-ai/flashinfer/blob/07e519fcc149f39e6dd00264149c092c2e37767e/flashinfer/jit/env.py#L74).

Use a fresh task-specific `FLASHINFER_WORKSPACE_BASE` for the campaign, and set `PYTHONPATH` to the full source root. Before testing, verify `flashinfer.__file__`, CuTe orchestration/FC1/FC2 module paths, and resolved `jit_env.FLASHINFER_CSRC_DIR`/`FLASHINFER_INCLUDE_DIR`; all must resolve to the intended arm/current source. This also prevents a September cached helper from being mistaken for a current source build.

To avoid recompiling identical shared native helpers for base/head, the parent may use a single canonical **current-upstream** `csrc`/`include` location for both arms after verifying the PR changes neither tree. Retain each arm's full Python source. Share a fresh campaign JIT cache only under that verified native-source identity; do not point Python `jit/` back to a nightly package to stabilize paths.

## Validation boundaries

- This audit establishes source contracts, exact wheel availability/build metadata, and a proposed runtime layout. It does not claim GPU import/compile/test success.
- Full current-source execution is necessary to catch prepared-launch callbacks, `skip_unpermute`, and changed routing ABI. Small and large-token cases should both be exercised; >1024 uses extra routing scratch.
- Current source tests, not September's copied nightly fixture, should be the primary validation. Preserve original tolerances and fused/W4A16 controls.
- Performance after rebase must be measured anew if reported as current-head evidence. Previous one-sweep tables remain historical evidence only.
