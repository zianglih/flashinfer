# Compact output workspace cleanup: bounded GPU qualification

Pass for frozen patch `3027b1b40824720568d8dcd132ab07098cb18525444ce14f3a1353148b5f0d79` against retained `9e3cb4d5fa0f45bba7014f67e968bf04e3cffa0f`. No repository source was edited by this validation.

- **Exact execution:** 128 paired bit-exact changing-route graph replays (256 total source executions), covering balanced, skewed, empty, and reactivated routing. Each source verifies compact prefixes, dense-index range/uniqueness, and the unchanged reciprocal caller-routing maps. Independent router processes may choose different within-expert row order; all route counts/prefixes and final output bits match.
- **Generated code:** all **70 captured pairs (64 FC1/FC2 + 6 combine)** have byte-identical raw PTX and SASS; 70/70 cubins also match byte for byte. All captured compile-time states and resource counts match. This includes static/CLC, PDL off/on, one/two CTA, N64/128/256, M512N128 versus M256N256, K96/non-K96, overlap enabled/disabled, and expanded/compact output metadata. Captured register counts are 73–160; all have zero local/stack storage, LDL/STL, MOV.SPILL, and R2UR.FILL sites.
- **Generic combine:** eight paired checks (four unique expanded/permuted × PDL off/on combinations repeated in two lanes) omit the private workspace. Invalid/nonlocal routes and all-zero output rows are included.
- **Existing public APIs:** requested eight unchanged tests passed, **8 passed, 311 warnings in 28.07s**, with no failures/errors/skips. Four MX cases cover N16 and two-CTA N128 for MXFP4x8/MXFP8; four NVFP4 cases cover standard/per-token wrapper accuracy and CUDA graphs. All 3,019 relevant test/source files remain hash-identical after execution.
- **Environment:** NVIDIA B300 SXM6 AC (SM103), container `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, PyTorch 2.12.0a0+5aff3928d8.nv26.05, CuTe DSL 4.8.0, Python 3.12.3. Primary GPUs 0/1 ran paired probes and GPU 2 ran public tests; each was idle-checked and all are now released. Persistent native compilation caches were reused without clearing; every process had a private compiler-artifact CWD.

This is a bounded pairwise gate with eight format/geometry selections and fixed K4 stages, not a full tactic matrix. It exercises bulk-64 and no-bulk output plans, including full/tail stores, but does not independently repeat the prior bulk-32 qualification. The exhaustive automatic-planner proof is separate. No sanitizer or performance timing was run for this cleanup; raw code identity supports retaining the existing timing evidence for these specializations.

Evidence is immutable and source-bound: `gpu-evidence.tar.gz`, SHA256 `4dae372ded6cc78613db8f4b06b55fec3a625e1770164f653d14115af19a0d70`; all 603 manifest entries were independently verified after download. Full receipts, exact argv, environment, selected test IDs, compiled attributes, PTX/cubins/SASS/resources, output hashes, and raw logs are under `gpu-evidence/`. `analysis-local.json` independently reproduces the remote comparison. `final-receipt.json` binds the final summary.

Reproduce the artifact audit locally:

```sh
python3 compare.py --root gpu-evidence --output analysis-local.json
python3 finalize_report.py
```
