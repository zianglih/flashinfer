# Retained K96 validation

Passed on `21fbe72c6f70643a2b61c7461f42937dbfb307e9`: **95 selected pytest cases**, **11 Linux compilation-cache tests**, and **288 focused sanitizer replays** (96 each for memcheck, synccheck and racecheck). Zero failed/error/skipped pytest cases and zero sanitizer errors/warnings. All jobs passed on their first attempt.

- Source: all 348 recorded file hashes match the pinned retained Git commit; tracked snapshot remained clean before/after every job. The retained reference and actual-plan fixture were used directly from this snapshot.
- Runtime: three assigned NVIDIA B300 SXM6 GPUs (SM103) in C3 `fi-moe-nvfp4-port-1026`, image `nvcr.io/nvidia/pytorch:26.05-py3`, Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA `13.2`, CuTe DSL 4.8.0, pytest 9.1.1 and TVM-FFI 0.1.15.post1.
- Compute Sanitizer 2026.3.0.0 (build 38855100). Persistent native compilation caches retained; isolated dump/output directories. GPUs 1/2/3 were verified idle after completion and released.

| Group | Result |
|---|---:|
| Existing accuracy/kernel tests | 33 passed |
| Wrapper, graph, unified API and autotuner tests | 62 passed |
| Linux compilation-cache tests | 11 passed |
| Memcheck | 96 replays / 48 compiled GEMMs |
| Synccheck | 96 replays / 48 compiled GEMMs |
| Racecheck | 96 replays / 48 compiled GEMMs |

Raw summaries:

```text
33 passed, 1310 warnings in 162.95s (0:02:42)
62 passed, 2425 warnings in 87.37s (0:01:27)
----------------------------------------------------------------------
Ran 11 tests in 5.315s

OK
```

memcheck:

```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 96 source-bound exact replays
```

synccheck:

```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 96 source-bound exact replays
```

racecheck:

```text
========= COMPUTE-SANITIZER
========= RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)
PASS 96 source-bound exact replays
```

Commands used (each on an exclusively assigned idle GPU; synccheck/racecheck followed their pytest group):

```bash
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70 --kind memcheck --gpu 1
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70 --kind exact --gpu 2
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70 --kind api --gpu 3
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70 --kind synccheck --gpu 2
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/21fbe72c6f70 --kind racecheck --gpu 3
```

The unchanged pytest selectors are recorded in [selection.json](evidence/validation-tools/selection.json); every expanded subprocess command, environment, source hash and JUnit result is in the individual receipts. The exact and API commands match the previous published command lists; this run binds them to `21fbe72c6`, not the earlier source.

Coverage and boundaries:

- Focused sanitizer geometry: H512/I384, 257 tokens, top-2, 96 of 192 local experts. Six explicit configs cover NVFP4 per-tensor/per-token, MXFP4x8/MXFP8, narrow/wide N, one/two CTA, M512, static/CLC, PDL off/on and balanced/skewed/empty/reactivated routes. Per tool: 20 partial-K and 28 aligned compiled controls.
- The focused probe checks storage bits within the same source across schedule/PDL variants. Numerical-oracle qualification comes from the separate retained-head pytest group; this probe is not an independent reference or an exhaustive tactic sweep.
- Tracked manual sanitizer options are unchanged, including memcheck `--check-tensor-ops no`. All 48 memcheck cubins contain the requested `-g-tmem-access-check`, nine named TMEM guard trap routines with matching SASS trap sites, and at least three direct guard calls. This proves compiled instrumentation, not execution of every failing guard branch.
- Only GEMM codegen is captured. Filter presence does not prove each matching native routing/prepare function executed. Instrumented memcheck local-memory accesses are not production spills. No performance measurement is claimed.
- The earlier full 150-case sanitizer matrix remains separately labeled d1767 evidence. This focused refresh does not repeat it, qualify Hopper/Rubin, or add reference self-tests.

Evidence:

- [Independent audit](audit.json): SHA256 `9a66148ea2a3622dcc0702ff8f816d2dbf292b1f69d8d0335cf8850d58192c21`.
- [Verified archive](evidence-transfer.tar.gz): 622 files, SHA256 `f0c1aa42cadcdda6746b246ddd1800a48b49ab25d881199fe587464876df1716`.
- [Manifest](evidence/validation/validation-manifest.json): SHA256 `5a176da4b840c87c1767c4b07248fc9247ee84643abf87827438fe512751f4ca`.
- Retained reference SHA256 `d8473bf5bc07ed35873415ac6be48548f86063a0ea60b943ea255ed5f27e6316`; actual-plan fixture/test file SHA256 `b96d1d7c1cf6d72429e1c24c3bf4c496dff608a648e924391e6af10608f5f502`.
