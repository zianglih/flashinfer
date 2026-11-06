# W4A16 full-tile TMA / partial-tile SIMT

The unstaged candidate uses TMA for complete output subtiles and predicated SIMT stores for partial subtiles in both FC1 and FC2, including gated FC1. It adds no descriptor bank or public interface. The independent source clone is [flashinfer-w4a16-hybrid-output-review](../../flashinfer-w4a16-hybrid-output-review).

Fresh paired timing against padded R2 is **−0.21%** geometric mean across 32 W4A16 cells: **−0.14% decode**, **−0.28% prefill**, **−0.37% EP**, and **−0.04% TP**. Individual changes range from **−1.49% to +1.13%**. Positive means the hybrid candidate is faster.

![Fresh paired speedup heatmap](hybrid-output-speedup.png)

[SVG](hybrid-output-speedup.svg) · [Plot provenance](plot-manifest.json)

| Model / parallelism | 4 tokens | 64 tokens | 4096 tokens | 16384 tokens |
|---|---:|---:|---:|---:|
| V3 EP8 | -0.06% | -0.05% | -1.47% | +1.13% |
| V3 TP8 | -0.38% | -0.29% | -0.61% | +0.17% |
| V41F EP4 | -0.69% | -0.19% | -0.98% | +0.04% |
| V41F TP4 | +0.23% | -0.04% | +0.77% | -0.63% |
| K3 EP8 | -0.07% | -0.33% | -1.20% | -0.08% |
| K3 TP8 | -0.06% | -0.20% | +0.58% | +0.20% |
| N3U EP8 | +0.17% | -0.11% | -0.56% | -1.49% |
| N3U TP8 | -0.02% | -0.12% | -0.17% | -0.07% |

## Method and evidence

- B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, C3/ziangli recovery box. Each fresh control/candidate pair uses the same GPU; GPU UUIDs are recorded.
- `bench_moe_deepseek.py`, public functional API, swap-AB, unfused finalize, NVFP4-family input-quantization option preserved. Only W4A16 measured. Frozen saved tactics; no AUTO. C-A-A-C order, 10 warmups and 100 strict CUPTI samples per phase, CUDA graphs with cold L2. Timings are means of the two phase medians; speedup is `control/candidate − 1`.
- Control: immutable padded R2, whose W4A16 implementation is unchanged from retained `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Candidate: `hybrid-01`, same HEAD plus one W4A16 kernel delta from R2. All 348 source hashes verified; native C++ caches reused.
- Complete raw samples, commands, logs, source manifests and config: [perf-evidence](hybrid-01/perf-evidence). [32-cell CSV](hybrid-01/perf-cells.csv) contains absolute timings and repeats; [summary JSON](hybrid-01/perf-summary.json) contains all aggregates.

## Validation

All 400 exact paired graph replays passed, including 800 untouched-padding checks, old/swap layouts, CLC/static, PDL off/on, one/two CTA, dynamic expert boundaries, actual epilogue-subtile boundaries, and an intermediate 192 channel tail. All 76 captured candidate compilations had no local-memory spills. Ten existing W4 tests and four fused-finalize compatibility cases also passed. Details: [VALIDATION.md](VALIDATION.md), [IMPLEMENTATION.md](IMPLEMENTATION.md), and [source manifest](hybrid-01/source-local.json).

No sanitizer ran. Changes remain unstaged and unpushed; the PR was not modified.

## Descriptor04 context

The descriptor04 experiment is separate historical context, not the paired baseline. TP V3 at 64 tokens measures 155.201 µs here, versus 182.313 µs in that earlier descriptor04 run (+17.47% by the same ratio). The fresh paired R2 comparison for this cell is 154.753→155.201 µs (−0.29%). All historical descriptor values are preserved in the CSV and are excluded from the paired aggregates above.
