# Further existing-tactic prefill retuning

Clean `fb66a27e` throughout. Native existing-tactic search at token buckets 4096/16384 followed by independent same-GPU old/new/new/old replay. No source edits or new tactics. The NVFP4 arm includes its input quantizer; MX uses the existing benchmark contract.

| Shape | Mode | Tokens | Old (us) | New (us) | Retune | Old/new phase spread |
|---|---|---:|---:|---:|---:|---:|
| V41F EP4 | W4A4 | 4096 | 341.155 | 341.602 | -0.131% | 0.019% / 0.028% |
| V41F EP4 | W4A4 | 16384 | 673.020 | 610.404 | +10.258% | 0.055% / 0.283% |
| N3U TP8 | MXFP8 | 4096 | 445.170 | 445.217 | -0.011% | 0.022% / 0.116% |
| N3U TP8 | MXFP4x8 | 4096 | 411.194 | 407.705 | +0.856% | 0.113% / 0.035% |
| N3U TP8 | MXFP8 | 16384 | 1369.459 | 1333.771 | +2.676% | 2.332% / 1.736% |
| N3U TP8 | MXFP4x8 | 16384 | 1330.776 | 1284.587 | +3.596% | 0.607% / 0.221% |
| N3U TP8 | PER-TOKEN | 4096 | 617.301 | 613.293 | +0.653% | 0.031% / 0.050% |
| N3U TP8 | PER-TOKEN | 16384 | 2000.360 | 2000.056 | +0.015% | 0.004% / 0.028% |

- V41F 16K selects FC1 M512/N128 instead of M256/N256, increasing gathered activation reuse. At4K only FC2 K steps change4→8 and the result is effectively neutral/slightly negative.
- N3U TP16K MX modes select FC1 M256/two CTA and K steps8 instead of M128/one CTA and K steps4; MXFP4x8 also selects ordinary scheduling. MXFP8 16K has 2.33% control /1.74% new phase spread, so its +2.68% magnitude needs caution; MXFP4x8 +3.60% is more consistent.
- N3U TP per-token4K widens FC1M128→M256 with two CTAs for +0.65%. The16K winning tactic is unchanged and the result is neutral. Tactic selection alone does not close its remaining performance gap.

| Job | Native process wall | cute.compile API | Profiling excl. compile | Other context |
|---|---:|---:|---:|---:|
| ep-v41-flash-w4a4 | 165.69s | 137.59s | 11.33s | 4.36s |
| tp-nemo3-ultra-mxfp | 401.54s | 319.07s | 46.30s | 21.76s |
| tp-nemo3-ultra-per-token | 173.13s | 129.90s | 19.23s | 11.62s |

All source, route, frozen-winner, cache-manifest, strict CUPTI, and runtime resource checks passed. Each dtype admits the existing320 tactics at each of the two profiles. Compilation spans include SDK cache/runtime checks; profiling exclusive time also includes warmups, graph capture, waits and timing machinery. Persistent native compilation caches are preserved.

Raw CAAC samples, exact tactics, commands, hashes and timing details: `report-more/{cells.csv,summary.json}` and `evidence-more/runs`. Fresh native managed caches are included under `evidence-more/runs/<job>/cache-native/`. Archive SHA256: `1b617e7e9fe97cca798bfb2550901db4ae44d135d153cd6c52c6eb51254c2765`.
