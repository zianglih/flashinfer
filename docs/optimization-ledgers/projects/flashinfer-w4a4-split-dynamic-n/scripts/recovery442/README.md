# C1 replacement environment at442d

Replacement devbox `fi-w4a4-pipeline-1025`, cluster c1, namespace ziangli,
explicit image `nvcr.io/nvidia/pytorch:26.05-py3`. The parent allocated it;
these scripts do not allocate or run a primary benchmark.

The verified WekaFS task directory is
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/recovery442-20261025`.
It passed write, fsync and advisory file-lock checks. The usual
`/workspace/flashinfer-w4a4-split-dynamic-n` is a symlink there. `/workspace`
and `/scratch` themselves are ephemeral. Source repositories, environment,
logs and explicit JIT caches are durable; local copies of recovery receipts
remain in this folder as well.

`setup_remote.sh` derives from the original project setup. It clones the
upstream baseline at `a65d5b09e7e4c4c5c160b0161c48becd100b3970` and fetches the
pushed fork candidate `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. The candidate
is a project-owned linked worktree; both git directories and the common store
must resolve inside this durable project. The three shared header submodules
must have identical pinned gitlinks before symlinking. No source edits occur.

The system-site-packages venv uses the same PyTorch image runtime and the
original recorded package versions as constraints. Explicit additions retain
CuTeDSL4.7.1, CUPTI Python13.4.0/CUPTI13.4.58, pytest9.1.1 and pre-commit4.7.0.
The environment recorder verifies active distribution versions and import paths;
it does not infer active versions from an unordered list containing both system
and venv distributions. The exact resolved freeze and pip-check report are kept.

## Required environment for subsequent probes

From the candidate directory, source this before every independent remote shell:

```bash
source ../scripts/recovery442/env_candidate.sh
CUDA_VISIBLE_DEVICES=4 PYTHONPATH=. ../.venv/bin/python <task-local-probe.py>
```

For original controls, enter `baseline` and source
`../scripts/recovery442/env_baseline.sh`. Candidate and baseline use separate
`FLASHINFER_WORKSPACE_BASE` and `CUTE_DSL_CACHE_DIR` roots under `cache/`.
The baseline cache started empty. Candidate and then baseline MoE routing,
FP4 and MXFP8 native module builds were prewarmed serially onGPU0. Neither
prewarm ran a benchmark or repeated B1.
Do not switch a shared native-cache epoch between the two revisions.

Symlink-aware import checks should compare resolved paths on both sides.
The older `native_readiness.py` assumed a non-symlink root; the recovery version
explicitly resolves both paths and verifies its private candidate cache.

## Evidence boundary

Initial inventory shows the same node `B200-83`, all eight original GPU UUIDs,
indices and driver580.178.04. `record_environment.py` checks this against the
archived original inventory. The pod/container, editable environment and JIT
cache are newly created, so this remains a distinct environment epoch. This
setup authorizes no new paired retention claim against earlier B1 results.
All scripts use the managed `/usr/local/bin/h`; transfer writes named files
only and never mirrors a partial source checkout.

Setup verification passed. Every non-editable line in `pip freeze` matches
the original archived environment; only FlashInfer's editable source commit
changes froma65 to442d. Active PyTorch display version is
`2.12.0a0+5aff3928d8.nv26.05`, while its wheel metadata version is
`2.12.0a0+5aff3928d8.nv26.5.50603568`. The initial constraint mistakenly used
the display version; pip rejected it before installing, and the failed log is
preserved. The corrected constraint matches the original wheel.

The pip-check report contains two diagnostics: the PyPI `nvidia-cuda-runtime`
package is absent (the container supplies system CUDA), and DALI requires
packaging<=26.0 while the recorded environment has26.3. These were not repaired
by changing the original package set. Native readiness is the relevant check
for this recovery and is recorded separately.

Native readiness completed successfully: routing, FP4 and MXFP8 readiness
markers plus the final exact442d completion marker are present. The bootstrap
and serial prewarm command exited0; GPU0 was released to the parent. No primary,
baseline-control or retention timings were collected. The original source
checkout remains untouched. A later baseline-only prewarm also completed all
three readiness markers and its exacta65 completion marker, then released GPU0.
Full log, six arm-specific build.ninja files and hashes are in
results/baseline-native-readiness; the command and source are preserved as
baseline-prewarm-command.json and native_prewarm_baseline.py.

All recovery evidence is archived under `results/`, including final environment
JSON, all8 GPU UUIDs, full `nvidia-smi -q`, package freeze, setup logs (including
the failed first resolver attempt), pip diagnostics and complete native prewarm
output. `setup-receipt.json` and `artifact-manifest.json` record commands/hashes.
