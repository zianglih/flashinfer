# Final442 retained-source validation

**95 existing numerical tests passed; all bounded memcheck and racecheck cases completed cleanly.** Production/test sources remained at `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. No source changes, test additions, experimental overlays, or additional benchmarks were made during validation.

| Stage | GPU | Cases completed | Failures/errors/skips | Tool result |
| --- | ---: | ---: | --- | --- |
| Existing focused numerical suite |4|71|0/0/0|366 Python deprecation warnings|
| Existing unfused W4A16 boundary suite |5|24|0/0/0|24 fused cases deselected;400 Python deprecation warnings|
| Memcheck independent-reference smoke |6|3|0/0/0|0 errors; no tool warnings|
| Memcheck production NB2 FC1 |6|12|0/0/0|0 errors; no tool warnings|
| Memcheck production FC2 N128/N256 |7|24|0/0/0|0 errors; no tool warnings|
| Racecheck production NB2 FC1 |6|12|0/0/0|0 hazards,0 errors,0 warnings|
| Racecheck production FC2 N128/N256 |7|24|0/0/0|0 hazards,0 errors,0 warnings|

Environment: C1 `fi-w4a4-pipeline-1025`, B200 GPUs4–7, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, PyTorch2.12.0a0+5aff3928d8.nv26.05, CuTe DSL4.7.1, pytest9.1.1, Compute Sanitizer2026.1.1.0(build37663202). Every shell used the candidate442 cache environment. Protected source hashes match before/after all runs. The three documented vendor symlinks resolve to exactly the Git commits pinned by442; receipts preserve both paths and gitlinks.

The numerical suite covers NVFP4 K-tails and poisoned SF guards, NV per-tensor/per-token and W4A16 reference accuracy, W4A16 row/K SF mapping, gated route boundaries, and cluster-padding reuse. The sanitizer phase probes use production imports directly, covering all six low-level formats, quantized/per-token FC1 output, twoCTA NB2 N128, FC2 N128/N256 TMA-SFB and epilogues, route/channel tails, and output canaries. FC1 direct probe completion is not an independent numerical oracle; the previously completed72 composed phase pairs and15 native exact configurations remain the separate numerical evidence for all six formats.

Fused finalize is excluded. Optional57 wrapper/graph/EP tests, synccheck/initcheck, PDL-on sanitizer reruns, and exhaustive geometry/dtype/reference combinations were not run. Existing reference tolerances were unchanged. The75 instrumented case completions are a separate check from the95 pytest passes, not75 additional independent numerical comparisons.

- [Numerical logs, JUnit, sources and archive verification](numerical/README.md)
- [Sanitizer campaign and exact receipts](sanitizer/20261025T095319Z/campaign.json)
- [Commands, selection matrix and explicit coverage boundary](../../scripts/final442-validation/README.md)

Numerical archive:144,295 bytes; SHA256 `f5582d3968bb13a24b436d11dd90e2df0922b220432f1f1ab8b0ca1e68bd9f32`. Sanitizer archive:4,220,245 bytes,28 files; SHA256 `6e94b9c7107c2681efc36fc2066ae204172f36666e446de4bdb2801b63ce9bd1`. Both archive digests were independently recomputed locally.

GPUs4–7 were released; release checks show0 MiB,0% utilization and no owned compute processes. The archive retains an initial vendor-symlink preflight stop and a corrected CPU-only closeout quoting error; neither launched failed GPU work or required sanitizer/test reruns.
