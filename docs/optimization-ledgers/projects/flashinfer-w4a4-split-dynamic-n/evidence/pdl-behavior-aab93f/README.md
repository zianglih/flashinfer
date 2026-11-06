# Direct behavior configuration and producer-exit PDL: bounded gate

Candidate carried forward for the parent’s full retention campaign. This fixed-tactic diagnostic does not establish primary AUTO retention or a TRTLLM comparison. Production remains unchanged by this task.

- Control: corrected retained `aab93f854054de834447bdd8985b8bbd653fb3c8`. Candidate: five unstaged files on that base, six pinned source files; byte-identical clean measurement freeze `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` created by parent.
- Direct internal behaviors are selected explicitly by the existing public wrappers; no phase flag/config object or public signature change. Preparation and activation GEMM signal after their prerequisite wait; scatter GEMM signals at producer exit, before cloned ring drains, with GPU release before the nonfused handoff.
- Native NVFP4, nonfused finalization, per-tensor scales, simulated EP8 / 32 local experts; same original native inputs/routing and input quantization outside the timer. Full-chain includes routing, preparation, both GEMMs and combine.
- Image `nvcr.io/nvidia/pytorch:26.05-py3`; CUDA 13.2.78; CuTe DSL 4.7.1; PyTorch `2.12.0a0+5aff3928d8.nv26.05`. One B200 on B200-92, GPU2 `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`. Only current adjacent control/candidate arms are paired.
- Timing: 10 warmups, 100 cold-L2 CUDA-graph CUPTI samples per arm. Order `control,candidate,control,candidate,control,candidate` represents ABA then BAB. Ratios are geometric means of the three control medians divided by the three candidate medians. No sample or arm filtering.
- All 90 timed arms (30 full-chain + 60 phase) and all 9,000 samples passed exact pre/post checks. T1 native exact plus true zero-route FC2 sentinel and T16384 native exact also passed. CPU policy audit: 90 configurations / 9,408 cases. Changed-file pre-commit passed. No broad GPU dtype matrix or sanitizers in this performance gate.

## Complete paired medians

All medians below are microseconds. FC1 phase timing includes its internal preparation. Full-chain is the decision metric.

| Tokens | Phase | Control 1 | Candidate 1 | Control 2 | Candidate 2 | Control 3 | Candidate 3 | Control / candidate |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | full chain | 49.7760 | 47.1040 | 49.8560 | 47.2320 | 49.8085 | 47.4240 | 1.054183x |
| 4 | fc1 | 28.8635 | 28.2880 | 29.2800 | 28.3040 | 29.3280 | 28.2560 | 1.030894x |
| 4 | fc2 | 16.1915 | 16.2240 | 16.1920 | 16.1600 | 16.2400 | 16.1285 | 1.002290x |
| 32 | full chain | 107.9525 | 104.8005 | 107.9205 | 105.0725 | 107.9360 | 105.4085 | 1.027050x |
| 32 | fc1 | 66.4805 | 65.0560 | 66.9120 | 65.2325 | 66.9760 | 65.1680 | 1.025126x |
| 32 | fc2 | 35.5045 | 35.5520 | 35.6165 | 35.5520 | 35.4080 | 35.5840 | 0.998507x |
| 128 | full chain | 144.4480 | 140.5125 | 144.5920 | 140.8010 | 144.7050 | 140.7685 | 1.027632x |
| 128 | fc1 | 89.8565 | 88.9765 | 90.4000 | 88.9920 | 90.4645 | 88.8645 | 1.014566x |
| 128 | fc2 | 48.2720 | 48.1920 | 48.2240 | 48.1600 | 48.1920 | 48.1765 | 1.001103x |
| 4096 | full chain | 204.9285 | 202.7680 | 204.5925 | 203.2650 | 204.5765 | 203.4570 | 1.007560x |
| 4096 | fc1 | 114.1760 | 113.9520 | 114.9760 | 114.1600 | 114.8965 | 114.0005 | 1.005654x |
| 4096 | fc2 | 63.1360 | 63.1040 | 63.4880 | 63.2810 | 63.2000 | 63.3600 | 1.000415x |
| 16384 | full chain | 483.2180 | 484.2575 | 482.9455 | 484.0975 | 493.2020 | 483.8100 | 1.004910x |
| 16384 | fc1 | 220.9770 | 220.2730 | 225.4410 | 227.2165 | 226.2565 | 226.1125 | 0.998662x |
| 16384 | fc2 | 133.4730 | 133.3605 | 133.4090 | 133.2160 | 133.5045 | 133.2165 | 1.001485x |

Decode improves by about 5.4% at T4 and 2.7% at T32/T128. Prefill is near-neutral: the final T16K control is 493.202 µs versus its earlier 483.218/482.9455 µs. All three control/candidate pairs remain included; the 1.004910x aggregate is not a stable prefill-gain claim.

## Actual native code generation

`CUTE_DSL_KEEP=ptx,cubin` and a unique `CUTE_DSL_DUMP_DIR` preserve artifacts from each actual native `cute.compile` call, with unchanged compilation options. Each export is archived immediately before names can be reused. Explicit object caches serve timing, and every timer asserts no compilation happened inside capture/measurement. No extra compile-only exporter was used.

| Route N | Phase | Control registers | Candidate registers | Control instructions | Candidate instructions | Local / stack |
|---:|---|---:|---:|---:|---:|---|
| 16 | FC1 | 64 | 64 | 1141 | 1167 | 0 / 0 |
| 16 | FC2 | 90 | 90 | 1310 | 1319 | 0 / 0 |
| 256 | FC1 | 80 | 80 | 5374 | 5374 | 0 / 0 |
| 256 | FC2 | 120 | 120 | 2441 | 2449 | 0 / 0 |

Registers match within each actual invocation, and all saved PTX/cubins have zero local-memory operations/LOCAL/STACK. The emitted launch cap remains 288 threads. `cuobjdump` SHARED=1024 reports static shared allocation only; it is not the total dynamic launch allocation. Policy/geometry audit verifies unchanged layouts and stage counts.

Instruction counts parse all addressed instructions including mixed-case TMEM opcodes and uniform predicates, excluding only trailing padding NOPs. The original inspector missed `@UP`-predicated sites; `native-codegen-verified.json` corrects only that analysis. The immutable raw archive, timing samples, original code bytes and resource fields are unchanged.

## Reproduction and provenance

The actual source copy and six source hashes are in `local-evidence/manifest.json`. Public wrapper/host/core/epilogue/preparation/finalizer paths and hashes are recorded per arm; observers release captured intermediates before full-chain timing. Numerical/oracle/timing function ASTs match the previous bounded helper.

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
source scripts/recovery442/env_candidate.sh
bash scripts/pdl_behavior_experiment/run_pairs.sh
```

The script fixes N16 for T4/T32/T128 and N256 for T4096/T16384, using GPU2 and a private CuTe cache. Existing result paths are refused; reproduction must select a fresh output directory. Full source/preparation/graph launch settings and raw 100-sample arrays are in each JSON receipt.

T1 used epoch r1. Pre-commit required merging two identical FC2 stage=5 branches with `or`; r2 changes only that host expression. All device/preparation/epilogue bytes are unchanged, and the full CPU policy audit re-passed. r1 source/manifest and T1 outputs remain preserved.

Raw archive SHA256: `8941bc1089a9c9aa6f5e11c5978ebbc5091613acfb327fbad6861fa204b63bd0` (220 files). `files-sha256.json` pins the local archive, summaries and independent review receipts.
