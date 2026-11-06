Independent fixed-screen audit passed: 4 cases, 30 public measurements, 3000 raw samples. All listed ratios were recomputed from the raw 100-sample medians. Values above 1 favor the denominator arm.

| Case | Native / matched | Native / FC1 | Native / both | Matched / FC1 | Matched / both |
|---|---:|---:|---:|---:|---:|
| v3-nvfp4 | 0.940790x | 0.916924x | 0.842020x | 0.974632x | 0.895014x |
| v3-mxfp | 0.928805x | 0.912020x | 0.854890x | 0.981928x | 0.920419x |
| kimi-k3-nvfp4 | 0.996724x | 0.877540x | 0.814999x | 0.880424x | 0.817677x |
| kimi-k3-mxfp | 1.000000x | 0.906737x | 0.846850x | 0.906737x | 0.846850x |

Source, plan, cache, dispatch, route, model, quantization environment, runtime identity and chronology checks passed. Source remained unchanged. No blockers found.

This is a fixed-geometry comparison on one candidate source. It does not establish AUTO selection quality or a cross-source performance improvement. No GPU work or collection was performed during this independent audit.
