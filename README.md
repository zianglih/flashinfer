# W4A16 mixed-cluster full13 performance evidence

This bundle contains one complete, ordered baseline/candidate AUTO screen over global token counts 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. [RESULTS.md](RESULTS.md) gives every point, including sample0; [comparison.json](comparison.json) contains the full selected tactics. This dataset is separate from the earlier partial-grid common-cache iterations. No samples or earlier runs are pooled into it. The measurements do not by themselves establish statistical significance or release qualification.

**Exact measurements.** The [baseline raw records](runs/baseline-full13/raw-records.json), [candidate raw records](runs/candidate3r-full13/raw-records.json), [baseline summary](runs/baseline-full13/summary.json), and [candidate summary](runs/candidate3r-full13/summary.json) are byte-identical to the completed captures. Every sample, including large sample-zero outliers, is retained. Each point has 100 cold-L2 CUPTI/CUDA-graph samples after 3 warmups. Each sample is the per-iteration maximum rank activity span, including gaps and overlap; reported latency is the median of the 100 rank-MAX samples. Preparation, AUTO tuning, routing preparation, graph capture, warmup, and L2 flushing are untimed.

**Source and policies.** Baseline is `316faec37a4706a2ecc7d46265087f8190b40baa`; candidate is `3d047d3f8e7923118ffea8b8d36151504ab1fa3d`. Both captures require clean source status and unchanged manifests. The frozen [native comparison audit](validation/native-comparison-audit.json) checks timer controls, runtime/image, fixtures, controlled environment, and benchmark-source equivalence before bundle construction. Baseline uses the original 16 native AUTO candidates with policy `all`. Candidate uses AUTO over the 18 new preferred4/fallback2 tactics selected from product catalog of 34 with policy `mixed-only`; this is not a fixed-tactic or tactic-matched comparison. Both arms use identical native-driver and policy-wrapper bytes. All eight rank winners, candidate counts/hashes, source manifests, helper hashes, runtime versions, and controlled flags are included. The effective shared driver differs from the pristine baseline checkout's driver; its exact bytes are in [recipe/benchmarks/bench_cute_dsl_moe_distributed.py](recipe/benchmarks/bench_cute_dsl_moe_distributed.py).

**Workload.** Synthetic GLM5 routed-expert core: D6144, intermediate 2048, 256 experts, top8, SwiGLU, EP8, BF16 activations, NVFP4 weights, precomputed routing, deterministic fused combination, PDL enabled, routing weights applied during combine, in-kernel FC2 reduction disabled. [fixture.json](fixture.json) records seeds and routing parameters. Attention, shared experts, outer model layers, and router computation are outside this benchmark's scope.

**Environment.** Eight NVIDIA B300 SXM6 AC GPUs, 148 SMs/GPU, CC10.3; GPU-pair topology NV18. Image `nvcr.io/nvidia/pytorch:26.05-py3`; PyTorch `2.12.0a0+5aff3928d8.nv26.5.50603568`; CuTe DSL 4.7.1; CUDA 13.2; CUDA Python/CUPTI Python 13.2.0; CUPTI package 13.2.86; NVSHMEM 3.6.5; nvshmem4py 0.3.1. The host driver from `nvidia-smi` is 595.91.07; the container's `CUDA_DRIVER_VERSION` environment value is 595.58.03. These are preserved as separate fields. See [runtime.json](runtime.json) and per-run metadata/hardware extracts.

**Compiled caches.** Both arms explicitly select `separate-flashinfer-workspace-v1` with distinct `FLASHINFER_WORKSPACE_BASE` values. The captured source reads that base and derives the Python variable `FLASHINFER_WORKSPACE_DIR` as `<base>/.cache/flashinfer/<version>/<target-architectures>`. CUDA-driver, CuTe DSL, and Triton cache roots remain shared. Persistent AUTO winner cache is disabled. Cache enablement is not proof that every direct CuTe compilation is reused; initial cache contents were not snapshotted. Compilation and AUTO tuning are outside the latency samples. Earlier iteration results used a shared FlashInfer base and must remain a separate dataset.

**Current validation evidence.** The [host pytest log](validation/host/pytest.log) records `134 passed, 3 warnings in 10.73s` for `tests/moe_ep/test_w4a16_mixed_cluster_config.py` and `tests/moe_ep/test_mega_workspace_knobs.py`. The [scoped pre-commit log](validation/precommit/precommit.log) records all applicable checks passing, including mypy, Ruff checks, and Ruff formatting; nonapplicable hooks remain marked skipped. [Pre-commit metadata](validation/precommit/metadata.json) lists the exact files and hashes. The [commit freeze](validation/candidate-commit-freeze.json), host source manifest, and unchanged-source records link those tested bytes to candidate 3d047d3. The host capture's HEAD field remains the baseline commit because the candidate edits were uncommitted at that time; it has not been rewritten. These are host/static checks, not current rigorous numerical or sanitizer qualification. Graph lifecycle, exhaustive static/atomic/shape coverage, unsynchronized first-use behavior, and in-kernel FC2 reduction (IKR) remain unqualified.

**Public extraction.** Raw measurements and source manifests are copied unchanged. Metadata uses repository-relative paths and explicit parameters. The pytest/pre-commit logs retain every character except replacement of a captured absolute checkout prefix with `${SOURCE}/`; replacement counts and original/output hashes are in [validation/log-extraction.json](validation/log-extraction.json). [extraction-log.json](extraction-log.json) enumerates all byte copies and metadata transformations. Raw orchestration/connection logs, process IDs, NIC identities, private host identifiers, and absolute checkout paths are excluded. [validation.json](validation.json) records preservation/content checks, and [SHA256SUMS](SHA256SUMS) covers bundle files. The content scan is supplemented by explicit metadata allowlisting; it is not a claim of exhaustive secret detection.

**Reproduction.** Use the exact image above on an otherwise reserved eight-GPU B300 system. [setup.sh](recipe/setup.sh) creates independent pinned checkouts, initializes the captured submodules, pins runtime packages while preserving the image's PyTorch, and installs both sources editable with `--no-build-isolation`. The pinned candidate is available at `https://github.com/zianglih/flashinfer.git`. [reproduce.sh](recipe/reproduce.sh) invokes the exact captured `run.py`/policy wrapper/native driver with the full grid and distinct FlashInfer workspace bases:

For a Docker-based reproduction, start the pinned image with the bundle mounted read-only and a new writable workspace:

```sh
BUNDLE=/absolute/path/to/published-bundle
WORK=/absolute/path/to/new-workspace
mkdir -p "$WORK"
docker run --rm -it --gpus all --ipc=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -v "$BUNDLE:/evidence:ro" -v "$WORK:/work" \
  nvcr.io/nvidia/pytorch:26.05-py3 bash
```

Inside that container:

```sh
bash /evidence/recipe/setup.sh /work https://github.com/zianglih/flashinfer.git
bash /evidence/recipe/reproduce.sh /work/baseline /work/candidate3r \
  /work/results /work/compile-cache
```

These setup/invocation helpers are parameterized reproductions of the captured recipe, not new validation runs performed during publication preparation. They write complete local provenance and logs, which may contain machine paths. New outputs require the same public metadata extraction before sharing, with raw measurement JSON left unchanged.
