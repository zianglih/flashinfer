# Isolated ACCA audit and bounded conclusion

The replay selection was sealed before execution: all ten original retention cells below −2%, plus two paired MXFP4x8 cells retained by the MX family invocation. Eight jobs ran serially on their original GPUs with unchanged source, frozen choices, routes, and native ELF/Ninja hashes. Normal Ninja postflight was a no-op.

Independently reconstructed all 4,800 CUPTI spans, 48 phase medians and 12 source comparisons. All eight jobs retain identical observed resources and pipeline configurations across ACCA, with zero local-memory spills.

| Job | Tokens | Dtype | Main CAAC | Isolated ACCA | Control spread | Candidate spread |
|---|---:|---|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 4096 | CuteDSL W4A16 | -6.17% | +1.74% | 3.12% | 0.11% |
| ep-nemo3-ultra-mxfp | 8192 | CuteDSL MXFP4x8 | +0.08% | -1.19% | 0.08% | 2.41% |
| ep-nemo3-ultra-mxfp | 8192 | CuteDSL MXFP8 | -2.53% | +0.12% | 0.16% | 0.16% |
| ep-nemo3-ultra-w4a16 | 16384 | CuteDSL W4A16 | -5.79% | -0.29% | 1.35% | 1.27% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP4x8 | -0.41% | +3.01% | 3.19% | 6.23% |
| ep-v3-mxfp | 16384 | CuteDSL MXFP8 | -2.23% | +4.66% | 3.98% | 5.81% |
| ep-v3-w4a16 | 8192 | CuteDSL W4A16 | -3.22% | +1.04% | 2.12% | 0.48% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP4x8 | -2.74% | -2.64% | 6.53% | 0.49% |
| ep-v41-flash-mxfp | 16384 | CuteDSL MXFP8 | -3.75% | -2.14% | 4.48% | 2.86% |
| ep-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -5.97% | -0.97% | 2.42% | 4.11% |
| ep-v41-flash-w4a16 | 16384 | CuteDSL W4A16 | -3.96% | -0.48% | 0.73% | 2.57% |
| tp-v41-flash-w4a16 | 8192 | CuteDSL W4A16 | -2.54% | +2.41% | 3.22% | 1.74% |

Aggregate replay delta is +0.4179%; six of twelve cells remain measured slower. The six selected W4A16 cases now range from −0.9695% to +2.4146%, so the largest initial W4A16 losses do not reproduce at their original magnitude. N3U EP8192 MXFP8 is +0.1223%; V3 EP16384 MXFP8 flips to +4.6614% with substantial repeat spread.

**Unresolved:** V41F EP16384 remains −2.6359% for MXFP4x8 and −2.1413% for MXFP8. Their control spreads are 6.53% and 4.48%, respectively, and clock excursions remain in the diagnostic. Those measurements are preserved; neither source causality nor per-cell non-regression is established.

The full campaign remains the publication dataset: −0.0878% overall, −0.3550% prefill, with all original negative cells retained. Its average is near zero and the large initial W4A16 losses are not stable across reversed-order isolated replay. This supports a bounded statement of no broad rebase slowdown established, not a uniform non-regression guarantee. No repeat value replaces a plot/table entry. No source changes or additional GPU work were performed by this audit.

Offline SASS comparison remained unavailable because the configured persistent CuTe caches contained no MoE artifacts; resource identity is not instruction identity.
