# PR8 optimization batch — 2026-09-19

PR8 remains at `d01f074`. No candidate in this batch has been promoted. Source,
benchmarks, raw outputs and independent review records are preserved in this
project. Sanitizer is deferred during performance iteration as requested.

## Method

Two separate 8×B300 devboxes use `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2,
EP8, H7168/I2048/E256/K8, O3 and the four native autotune tactics. Each shape has
100 cold-L2 CUDA-graph CUPTI samples; the reported statistic is the median of
per-iteration rank-MAX latency. Shapes: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
4096, 8192 and 16384 tokens.

Retention prioritizes 4–512-token decode and checks each prefill row. The 1/2
rows remain reported but do not affect retention. Every comparison uses its own
same-node d01 baseline. Ratios from different nodes are never multiplied.
A ratio above 1 means faster than the baseline. Serial measurements can drift;
full tables include MAD and 25-sample quarter medians.

## Completed results

| Candidate | Decode geometric speedup | 4K | 8K | 16K | Decision |
|---|---:|---:|---:|---:|---|
| Striped source-CTA readiness, ca05 | 0.944671× | 0.970046× | 0.984111× | 1.008488× | Reject; decode consistently slower, 16K aggregate affected by drift |
| Early scheduler-ID broadcast, 2bb | 0.987321× | 0.999837× | 0.959524× | 0.987197× | Do not promote |
| Staging before pipeline initialization, ec742 | 1.000089× | 1.004228× | 0.963794× | 0.989230× | Do not promote; mixed decode, no net gain |
| Fifth combine WG after dispatch cleanup, 2739 | Inactive for decode capacity | 1.010541× | 0.960070× | 0.979782× | Do not promote; mixed active prefill results |
| Constant-stride coordinate recurrence, 63f49 | Inactive for decode capacity | 1.007633× | 0.990740× | 1.008518× | Do not promote; small mixed prefill effects |
| Linear worker addresses, 3b42 | 1.005822× | 1.008967× | 0.962814× | 0.971607× | Do not promote; small mixed decode gain and prefill regressions |

Each candidate passed all 104 finite bit-exact benchmark-output comparisons.
Selected tactics were unchanged for every shape. These checks do not substitute
for the full native accuracy suite or sanitizer. No further qualification is
warranted for candidates without a useful performance result.

Full tables and evidence:

- [Striped readiness](cta-ready-staging/decode13-benchmark-hu15-recovery/RETENTION.md)
- [Startup comparisons](parallel-startup-node-20260919/performance/RETENTION.md)
- [Fifth combine WG](dispatch-combine-current/decode13-benchmark-hu15/RETENTION.md)
- [Coordinate recurrence](reducer-coordinate-recurrence/decode13-benchmark-hu15/RETENTION.md)
- [Linear worker addresses](linear-combine-address/decode13-benchmark-hu115-v2/RETENTION.md)

Independent terminal audits verified 169 member files for each hu15 candidate
and 436 files for the hu115 three-arm study. Original compressed archives remain
remote; the complete member bytes, hashes and timing arithmetic are verified
locally. The interrupted earlier hu59 striped run is excluded entirely.

## Linear-address compiler repair and result

The linear-worker address experiment applies on decode's first pass, respects
actual static route-buffer strides, casts to Int64 before multiplication and
introduces no alignment requirement. Initial ce0 compilation lost CuTe's
alignment proof after flattening and failed before any timing row. That failure
is preserved separately and is not a performance result.

Successor `3b42f0d` restores the divisibility implied by the existing strides
using `cute.assume`; this adds no runtime check or caller constraint. Source
review `a068a23b` and runtime review `f02ebfcb` passed. D2 launched on hu115 at
1789832979.761842 (PID/PGID26774), against its original same-node d01 A1 control.
The full sweep completed with 104 finite bit-exact output pairs and all 13
tactics unchanged. Decode improved only 0.58% geometrically, with regressions at
8 and 64 tokens; 8K and 16K were slower. No promotion or broader qualification.
Independent terminal audit `1b64cd87` verified all 166 original member files,
104 exact output pairs, unchanged tactics, and process/GPU closure. The original
gzip remains remotely sealed; complete member bytes are verified locally.

All candidates are independent. They preserve ordered BF16/FP32 reduction,
two dequant WGs, five-WG CTA layout and all readiness/lifetime barriers.
None is stacked on a rejected overlap experiment. Native/codegen qualification
is conditional on a useful full-sweep performance result.
