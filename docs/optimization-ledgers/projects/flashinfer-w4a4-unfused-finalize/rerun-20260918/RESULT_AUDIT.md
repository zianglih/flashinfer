# Uniform rerun result audit

Audited all downloaded results and the candidate `PR_BODY.md` at PR head `f9dd3c10541e087b716772245a9d033499745048`, base `eb5f05be1f8e3ef8aa017a66dcbd5d80119b1095`, pinned runtime `0.7.0.dev20260917` / `d233e27ddddbcfdc24eec38ab4dffda1f43ff49c`. No reruns, source changes, or GitHub writes.

## Publication verdict

**No numerical or data-integrity blocker.** Independently recomputed, without relying on the summarizer's derived ratios:

- 12 complete sweeps, with exactly 15 forward-ordered counts in each.
- 180 native CSV lines match the returned full-precision JSON at the native six-decimal formatting; the PR body reproduces all180 correctly.
- All135 PR ratio cells (three tables ×15 counts ×three modes) match ratios recomputed from the original JSON, rounded to four decimal places.
- All45 base-unfused/head-unfused comparisons improve; the body correctly qualifies this as one sweep, not statistical proof.
- TFLOPS matches the native simulated-uniform-local workload formula.
- Runtime source hashes match the exact base/head git blobs. PR raw-log/result/cache SHA-256 identities match downloaded files. No timing log reports CUPTI fallback.
- Numerical correctness remains attributed to earlier tested revisions; the new campaign is performance evidence. No old Nsight timings are presented as a cause of the new timing changes.

**Cleanup:** remove the internal HTML drafting comment `Parent may replace this with fresh local checks; do not relabel the historical GPU tests.` before publishing, if it is still present.

## N2 W4A4 fused controls

These are material control differences, not evidence that fused-finalize arithmetic changed:

| Mode | Base fused ms | Head fused ms | Base/head ratio | Head latency change |
| --- | ---: | ---: | ---: | ---: |
| W4A4 per-tensor | 0.038304 | 0.0408645 | 0.9373417025 | +6.68468045% |
| W4A4 per-token | 0.050657 | 0.055984 | 0.9048478137 | +10.51582210% |

The exact N2 cache keys exist in both arms. Token2 maps to bucket2 under the unchanged native hybrid bucket mapper. Cached selected tactics differ:

```text
W4A4 tactic = (routing_tile, GEMM1, GEMM2)
GEMM tactic = (mma_tiler_mn, cluster_shape_mn, raster_along_m)

per-tensor base fused:
(128, ((128,128),(1,1),False), ((128,128),(1,2),False))
per-tensor head fused:
(128, ((128,256),(1,1),False), ((128,128),(1,1),False))

per-token base fused:
(128, ((128,128),(1,1),False), ((128,128),(1,1),False))
per-token head fused:
(128, ((128,256),(1,1),False), ((128,128),(1,2),False))
```

The two N2 fused control regressions coincide with independent autotuning selecting different GEMM1 tilers and GEMM2 clusters. The cache supports saying selection differed. It does **not** isolate how much of the measured change is caused by each tactic versus run variation. Do not describe the differences simply as noise or subtract them from the unfused speedup. The PR's current “complete selected path” limitation is correct; an explicit sentence naming these outliers would make the control evidence easier to interpret.

## N16384 W4A16 controls and optimization

| Arm | Mode | Latency ms | Cached GEMM1 and GEMM2 tactic (identical within arm) |
| --- | --- | ---: | --- |
| Base | fused | 1.4835310000000002 | `((128,128,256),(2,1),True)` |
| Head | fused | 1.454523 | `((256,128,256),(2,1),True)` |
| Base | unfused | 1.4010349999999998 | `((256,128,256),(2,1),True)` |
| Head | unfused | 1.3335625 | `((256,192,256),(2,1),True)` |

W4A16 GEMM tactic is `(mma_tiler_mnk, cluster_shape_mn, raster_along_m)`. This kernel maps output channels to M and routed rows to N, so the unfused head selects route tile192 instead of128. The fused head selects MMA M256 instead of128. Thus the measured unfused **1.0506×** and fused-control **1.0199×** both include different selected complete paths. They cannot be combined into an isolated causal estimate of the finalizer optimization.

All exact cache keys and cached tactic values for these control points (plus their unfused arms) are preserved in `selected-control-tactics.json`. No cache fallback/error warning appears in the sweep logs. This is source/cache-derived tactic evidence, not a new kernel trace proving executed instruction timing.

## Suggested concise PR clarification

“Independent autotuning selected different tactics at the N2 W4A4 fused-control outliers (head latency +6.68% per-tensor and +10.52% per-token) and at N16384 W4A16 in both finalize modes. Accordingly, the tables report complete selected-path performance; they do not isolate kernel-only gains.”
