# Shared CLC control, N3U TP8 at 16,384 tokens

Only the single shared FC1/FC2 CLC flag changes; source 475cae6b, per-token recipe, input quantizer, route tensors and both GEMM geometries remain identical. No AUTO. Cloned caches changed exactly one matching entry each; original caches remain untouched. Same GPU0, 100 strict CUPTI samples per on/off/off/on phase, passive NVML telemetry.

| Shared CLC | Full call geometric mean µs | Quantizer tail after FC1 µs | FC1 µs | FC2 tail after quantizer µs |
|---|---:|---:|---:|---:|
| On | 1956.908 | 641.1 | 536.9 | 450.0 |
| Off | 2018.004 | 641.7 | 549.9 | 498.8 |

CLC on improves end-to-end throughput by 3.122%. The exposed quantizer interval barely changes; it remains the principal target. The standalone kernel duration differs (662 versus 705.5 µs) because it includes waiting/overlap with FC1; the residual interval after FC1 is the relevant comparison here.

All source/route/cache/register guards passed; zero GEMM local bytes. No clock throttling reported; every phase quartile was 2032 MHz, clock-reason bits 0. Repeat spreads: CLC on 0.041%, off 0.010%. No compiler options or persistent cache policy changes.

Raw evidence: `full-evidence`; per-iteration components and clock quartiles: `component-samples.json`, `summary.json`; exact one-entry cache mutations: `full-evidence/cache-changes.json`. Archive SHA 8c3844bec5e937139051efe04f94a2f243017eb643e5adf25332e1df5d6d1900.
