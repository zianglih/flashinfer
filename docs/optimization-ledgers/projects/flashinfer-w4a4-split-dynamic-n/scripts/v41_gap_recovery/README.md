# V4.1 gap iteration: C2 runtime recovery

The previous C1 devbox was no longer present. The replacement is
`fi-v41-gap-c2-1025` in `c2/ziangli`, hostname `hu-pdx-150`, with 8 B300 GPUs,
driver 595.91.07 and explicit `nvcr.io/nvidia/pytorch:26.05-py3`. C1's durable
project was absent on the C2 filesystem, so no old compiled artifacts or timing
medians were reused.

- Durable project: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/v41gap-c2-20261025`
- Alias: `/workspace/flashinfer-w4a4-split-dynamic-n`
- Clean source: `baseline-0c`, commit `0c1e00fc3e4f913c8c241796c70a29673737c542`
- Python: `.venv/bin/python`, system-site-packages from the explicit image.
- Environment: `scripts/recovery442/env_candidate.sh`, now `FLASHINFER_CUDA_ARCH_LIST=10.3a` on this new host, `TRTLLM_ENABLE_PDL=1`, `MAX_JOBS=8`.
- Native cache: `cache/gap-c2-native`; CuTe per-source/model/family caches remain managed by `run_model_tables.py`.
- Exact runtime imports: CuTe 4.7.1, Torch 2.12.0a0+5aff3928d8.nv26.05/CUDA13.2, CUPTI 13.4.58.
- Source/helper/environment provenance: `evidence/v41gap-c2-bootstrap` and each launched run receipt.

`setup_c2.sh` captures the recovery recipe, with dependencies constrained to the
prior validated runtime. It skips the unrelated native EP build. The inherited
DALI dependency conflicts with the previously pinned packaging 26.3; the raw
pip-check log is preserved and the benchmark's required modules import with
verified versions.

The initial attempt to clone the filtered source through local upload-pack
failed because Git disabled lazy fetching of missing promisor objects. The
original setup script/log are preserved. The seed was recovered with a direct
shallow fetch of exact `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` from the public
fork, with no benchmark run on that seed. Its native source/header trees were
verified identical to 0c before sharing `flashinfer/data`. The seed remains clean
and supports the existing independent deployment helper.

Fresh native controls run V3 on GPUs 4/6 and V4.1 on GPUs 2/3. GPU 5 is reserved
for kernel gates, GPU 7 for the parent's overlap experiment, and GPUs 0/1 for
profiling. Existing B200 data remains historical evidence, not a denominator
for B300 retention decisions. No original a65 benchmark is rerun.
