# Independent full-campaign audit

Source comparison: `a620ce779` → `2b4732791`; full CAAC campaign. Fetched archive SHA256: `3398f3067d72954914d2ef34cf4466eba7a1fa29dd5ae87c969b74d2c896211a`.

- Reconstructed all 187,200 CUPTI graph spans from kernel activities and correlation IDs, independently checked all 1,872 phase medians and 468 candidate/control comparisons. No profile fallback or retuning occurred.
- All 31 jobs have identical observed launch resources and static pipeline configurations across CAAC; zero local-memory spills. This does not prove SASS identity.
- Summary excludes 1/2 tokens: 396 retained comparison cells. Geomean: **−0.0878% overall**, **+0.0173% decode (4–64 tokens)**, **+0.0049% middle (128–512)**, **−0.3550% prefill (4096–16384)**. EP −0.1536%; TP −0.0141%.
- All 15 losses below −1% are prefill; 10 are below −2%. These are measured full-window differences, not yet source-attributed regressions.

| Job | Tokens | Backend | Full-window delta | C repeat spread | A repeat spread |
|---|---:|---|---:|---:|---:|
| ep-kimi-k3-w4a16 | 4096 | CuteDSL W4A16 | -6.17% | 0.30% | 1.14% |
| ep-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -5.97% | 0.34% | 4.76% |
| ep-nemo3-ultra-w4a16 | 16384 | CuteDSL W4A16 | -5.79% | 3.32% | 2.99% |
| ep-v41-flash-w4a16 | 16384 | CuteDSL W4A16 | -3.96% | 9.17% | 5.19% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP8 | -3.75% | 3.97% | 1.66% |
| ep-v3-w4a16 | 8192 | CuteDSL W4A16 | -3.22% | 1.30% | 4.64% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP4x8 | -2.74% | 3.69% | 0.51% |
| tp-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -2.54% | 2.80% | 1.21% |
| ep-nemo3-ultra-mxfp | 8192 | CuteDSL MXFP8 | -2.53% | 0.05% | 3.51% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP8 | -2.23% | 5.59% | 2.08% |
| ep-kimi-k3-mxfp | 16384 | CuteDSL MXFP4x8 | -1.98% | 4.43% | 0.79% |
| ep-kimi-k3-w4a16 | 8192 | CuteDSL W4A16 | -1.56% | 0.60% | 1.57% |
| tp-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP4x8 | -1.44% | 1.78% | 0.19% |
| ep-nemo3-ultra-mxfp | 16384 | CuteDSL MXFP8 | -1.28% | 0.43% | 2.69% |
| ep-kimi-k3-per-token | 16384 | CuteDSL PER-TOKEN | -1.11% | 0.14% | 2.30% |

## Diagnostic boundary

The initial W4 losses develop late within sample windows, and multiple phases show lower clocks. The two MXFP8 negative points without a recorded SM-clock drop also exhibit late-window drift in both source arms:

- N3U EP8192 MXFP8 first-quartile CAAC medians: 469.795 / 470.339 / 469.635 / 470.179 µs; later quartiles reach approximately 495–501 µs in both arms. Telemetry records 2032 MHz throughout.
- V3 EP16384 MXFP8 first-quartile CAAC medians: 697.220 / 696.324 / 698.084 / 697.508 µs; later quartiles reach approximately 750–796 µs in both arms. One candidate quartile has no NVML samples; the available samples record 2032 MHz.

First-quartile slicing is diagnostic only and is not used to replace full-window results. NVML sampling can miss changes and does not prove stability. The original data remain immutable. Review the separate serial ACCA replay before attributing losses to source changes.

The configured persistent CuTe caches contain no W4/SWAP artifacts, so an offline SASS identity comparison was not available. Native source caches were built normally per source; no ELF/header transplant was used.
