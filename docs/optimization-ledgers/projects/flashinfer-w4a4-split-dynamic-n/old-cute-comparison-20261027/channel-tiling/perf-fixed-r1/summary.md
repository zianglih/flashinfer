# Channel-tiling fixed screen

Complete: True. Ratios >1 favor the named candidate. All arms run the same candidate source on GPU2; this is fixed-geometry evidence, not an AUTO or cross-source retention result.

| Case | Native / Matched | Native / FC1 | Native / Both | Matched / FC1 | Matched / Both |
|---|---:|---:|---:|---:|---:|
| v3-nvfp4 | 0.940790× | 0.916924× | 0.842020× | 0.974632× | 0.895014× |
| v3-mxfp | 0.928805× | 0.912020× | 0.854890× | 0.981928× | 0.920419× |
| kimi-k3-nvfp4 | 0.996724× | 0.877540× | 0.814999× | 0.880424× | 0.817677× |
| kimi-k3-mxfp | 1.000000× | 0.906737× | 0.846850× | 0.906737× | 0.846850× |

Native means its retained0b7 selected geometry, measured again here. Matched normalizes to sharedN128/M256/group2/K4. FC1 changes only its CTA group; Both changes both phases. NV includes initial activation quantization; MX excludes it. Each leg retains100CUPTI cold-L2 samples and unfused public functional workflow.

Raw samples in completed cases: 3000. Source, cache/tactic, dispatch, route identity and actual import checks passed for every listed case.
