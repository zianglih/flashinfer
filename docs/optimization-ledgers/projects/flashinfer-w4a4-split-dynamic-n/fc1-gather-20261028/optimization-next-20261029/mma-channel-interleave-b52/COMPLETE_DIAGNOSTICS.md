# Complete MMA-interleave diagnostic coverage

**The current candidate fails execution qualification; no numerical or timing run is authorized by this report.**

Frozen candidate `3b0114ea7b8099d759d9c62808d8752d2fa94fdda720f77024f4a6c4b8be64ac` on `b52e4e09649dc180fc7583a25ec35ff55f04654d`. The original R0 gate and its report are preserved unchanged. A separately approved compile-only continuation completed the predeclared26 unique kernels, with one intentionally repeated failed FC1 needed to reach its FC2. All27 captured compilations replaced/intercepted owned MoE callables; none launched.

| Signature/capture | Phase | Channels | Static ops Δ | REG old/new | STACK old/new | LDL old/new | STL old/new | Exact PTX/CUBIN |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| matrix:000 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:001 | FC2 | 1 | +0 | 100/100 | 0/0 | 0/0 | 0/0 | yes |
| matrix:004 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:005 | FC2 | 1 | +0 | 125/125 | 0/0 | 0/0 | 0/0 | yes |
| matrix:012 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:013 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:022 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:023 | FC2 | 1 | +0 | 82/82 | 0/0 | 0/0 | 0/0 | yes |
| matrix:028 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| matrix:029 | FC2 | 1 | +0 | 80/80 | 0/0 | 0/0 | 0/0 | yes |
| matrix:036 | FC1 | 2 | -7 | 168/168 | 0/0 | 0/0 | 0/0 | no |
| matrix:037 | FC2 | 2 | +2 | 108/108 | 0/0 | 0/0 | 0/0 | no |
| matrix:038 | FC1 | 2 | -7 | 168/168 | 0/0 | 0/0 | 0/0 | no |
| matrix:039 | FC2 | 2 | +2 | 128/128 | 0/0 | 0/0 | 0/0 | no |
| matrix:040 | FC1 | 2 | +8 | 168/168 | 0/0 | 0/0 | 0/0 | no |
| matrix:041 | FC2 | 2 | -11 | 116/116 | 0/0 | 0/0 | 0/0 | no |
| matrix:042 | FC1 | 2 | +8 | 168/168 | 0/0 | 0/0 | 0/0 | no |
| matrix:043 | FC2 | 2 | -11 | 116/116 | 0/0 | 0/0 | 0/0 | no |
| matrix:048 | FC1 | 2 | +25 | 168/168 | 128/48 | 16/38 | 16/11 | no |
| matrix:049 | FC2 | 2 | +10 | 152/142 | 0/0 | 0/0 | 0/0 | no |
| matrix:050 | FC1 | 2 | +25 | 168/168 | 128/48 | 16/38 | 16/11 | no |
| matrix:051 | FC2 | 2 | +10 | 152/142 | 0/0 | 0/0 | 0/0 | no |
| native-0:000 | FC1 | 1 | +0 | 168/168 | 0/0 | 0/0 | 0/0 | yes |
| native-0:001 | FC2 | 1 | +0 | 106/106 | 0/0 | 0/0 | 0/0 | yes |
| native-1:000 | FC1 | 2 | -23 | 168/168 | 0/0 | 0/0 | 0/0 | no |
| native-1:001 | FC2 | 2 | +0 | 105/105 | 0/0 | 0/0 | 0/0 | no |

Both inherited M512/N128/K8 MX FP4×FP8 and FP8×FP8 FC1 cases shrink stack128→48B but increase local loads16→38. Three common values become locally stored before role donation and reload in multiple roles, as documented in the R0 report. Their FC2 registers fall152→142 with zero local instructions and+10 static operations.

All12 one-channel captures are byte-identical. Native N3U EP16K MXFP8 ReLU² FC1 and FC2 are unchanged. Native K3 EP16K per-token SiTU remains spill-free; FC1 removes23 static non-NOP instructions, FC2 has unchanged instruction count but a different binary. Static counts do not imply speedup.

The actual source proof preserves K order per accumulator, K96 descriptor arithmetic, first-K initialization, all copies/barriers/releases and quotas. No quota/shape rescue or source composition was attempted. The complete coverage is useful for investigating common startup lifetimes, but does not justify retaining this version.

Evidence: `combined-diagnostics.json`, original `RESULTS.md` and `qualification.json`, continuation `harness-proof.json` and `codegen-analysis.json`. Both hash-verified archives and the original gate failure remain separate.
