# Retained compact FC2 validation

Passed on `83dfef8a656384f5cd10db847602593bb6f9b2c6`: **95 selected pytest cases**, **11 Linux compilation-cache tests**, and **384 focused sanitizer graph replays** (128 each for memcheck, synccheck and racecheck). Zero failed/error/skipped pytest cases and zero sanitizer errors/warnings. All five groups passed on their first attempt; pytest warnings remain visible in the raw output below.

- All 348 recorded source hashes match the pinned Git commit. The tracked snapshot stayed clean before/after every group and at postflight; the retained reference and actual-plan fixture were used directly.
- Five assigned NVIDIA B300 SXM6 GPUs (SM103), C3 `fi-moe-nvfp4-port-1026`, image `nvcr.io/nvidia/pytorch:26.05-py3`. Python 3.12.3, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CUDA `13.2`, CuTe DSL 4.8.0, pytest 9.1.1, TVM-FFI 0.1.15.post1.
- Compute Sanitizer 2026.3.0.0; persistent native compilation caches retained and dump/output directories isolated. GPUs 1–5 were idle/0 MiB at postflight and released to the parent benchmark campaign.

| Group | Result |
|---|---:|
| Existing accuracy/kernel tests | 33 passed |
| Wrapper, graph, unified API and autotuner tests | 62 passed |
| Linux compilation-cache tests | 11 passed |
| Memcheck | 128 replays / 64 compiled GEMMs |
| Synccheck | 128 replays / 64 compiled GEMMs |
| Racecheck | 128 replays / 64 compiled GEMMs |

Raw summaries:

```text
33 passed, 1311 warnings in 140.70s (0:02:20)
62 passed, 2424 warnings in 95.41s (0:01:35)
Ran 11 tests in 5.687s

OK
```

memcheck:
```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 128 source-bound exact replays
```

synccheck:
```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
PASS 128 source-bound exact replays
```

racecheck:
```text
========= COMPUTE-SANITIZER
========= RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)
PASS 128 source-bound exact replays
```

Commands used (each on an exclusively assigned idle GPU):

```bash
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind memcheck --gpu 1
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind synccheck --gpu 2
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind racecheck --gpu 3
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind exact --gpu 4
python3 -u /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563/validation-tools/run.py --root /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/optimization-20261028/tp-ep-post-sanitizer/retained-refresh/83dfef8a6563 --kind api --gpu 5
```

The existing pytest selectors are unchanged in [selection.json](evidence/validation-tools/selection.json). All expanded subprocess commands, environment settings, source hashes and JUnit results are retained in the per-group receipts. The graph probe is a local artifact and adds no repository test or production source changes.

Coverage and boundaries:

- H512/I384, 257 tokens, top-2, 96 local of 192 experts. Eight explicit configs 0/3/4/5/6/7/8/9 cover NVFP4 per-tensor/per-token, MXFP4x8/MXFP8, narrow/wide N, one/two CTA, M512, static/CLC, PDL off/on and balanced/skewed/empty/reactivated routes. Each tool compiled 24 partial-K and 40 aligned GEMMs.
- Each tool executes 64 compact-output replays across all four formats. Actual compiled metadata reports `output_is_routed=True`, 64-row/two-stage slabs. Every skewed replay has **six full and three partial slabs**, for both schedules and PDL settings. N128 valid rows are `[128,43,128,44,128,43]`; N256 rows are `[171,172,171]`. Each maps exactly 514 live rows. Post-replay inspection verifies exclusive compact prefixes, unique expanded indices, and exact dense-index mapping within allocation bounds. All-nonlocal and reactivated replays exercise index lifetime changes.
- Automatic 64-row slab coverage here is separate from the prior forced 32-row-slab source-paired gate. The focused probe checks storage bits across schedule/PDL variants within the same source; the separate 33-test group supplies the maintained independent numerical oracle. This is not an exhaustive tactic sweep.
- Tracked sanitizer filters/options are unchanged, including memcheck `--check-tensor-ops no`. All 64 memcheck cubins contain `-g-tmem-access-check`, nine named TMEM guard routines with matching assembled trap sites, and at least three direct guard calls. This establishes compiled instrumentation, not execution of each error branch. Only GEMM codegen is captured; native filter presence does not prove every matching native routing/prepare function executed. Instrumented memcheck local-memory accesses are not production spills.
- Earlier broad 150-case sanitizer results remain separately labeled d1767 evidence. This refresh does not repeat that matrix, qualify Hopper/Rubin, or add reference self-tests. No performance timing is included.
- Upstream precommit and Build Docs passed for this head. The upstream GPU jobs were skipped pending authorization; the failed [Test Results Summary](https://github.com/flashinfer-ai/flashinfer/actions/runs/40717866793/job/122920420727) is that gate, not a GPU test result.

Evidence:

- [Independent audit](audit.json), SHA256 `10b7f1ced543b1a193106841e48c4eefc483d142f3282605ac60158cfe8c690c`.
- [Verified archive](evidence-transfer.tar.gz): 813 files, SHA256 `b0c9272c65b63f5ba2717205bfc3e33319520e7531fb681212c8a50a86b55c5c`.
- [Manifest](evidence/validation/validation-manifest.json), SHA256 `d4e2282a527a4693ac77e2cab7b432b6a87137237d1b451ea5fd19a15733e815`.
- [Postflight](evidence/validation/postflight.json), SHA256 `435460999c71e7527c2c17cbbc0c2f5bfae692394373f94b431e8f25ff13556a`.
- Source receipt SHA256 `2744243f82e04fc0e45b93051ba3d5418768c47565ea839aef12902927a1f200`; runtime receipt SHA256 `eee35fe2acf3186a4ffb1c3269725cbfb2737fc5df3d4ae734351f4c1474d1a5`.
- Retained reference SHA256 `d8473bf5bc07ed35873415ac6be48548f86063a0ea60b943ea255ed5f27e6316`; actual-plan test file SHA256 `b96d1d7c1cf6d72429e1c24c3bf4c496dff608a648e924391e6af10608f5f502`.
