Fixed in [14a338579](https://github.com/flashinfer-ai/flashinfer/pull/7290/commits/14a338579eb8acddcc5cfd1cc58871fc0788de22): both suites now share the MMA-plan observer, preserving selected FC1/FC2 stage boundaries and K64 tails.

Validated on CUDA 13.2: B200/SM100 (K64) and B300/SM103 (K96) each pass 8/8 zero-tolerance cases covering unified, functional, wrapper and per-token paths. The original four cases also passed on both, so this corrects a latent reference-plan mismatch. No kernel, oracle-arithmetic or tolerance changes.
