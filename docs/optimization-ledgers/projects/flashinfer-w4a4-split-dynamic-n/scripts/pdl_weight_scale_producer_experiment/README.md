# Independent A/SFA TMA issuer experiment

The frozen review copy `flashinfer-pdl-weight-scale-producer-review` starts from the integrated full-capacity FC2 PDL prefetch contract (a92c source, byte-equivalent retained24c). It adds one private compile-time behavior, `separate_weight_scale_producer`; the public FC2 host selects it only when startup prefetch is admitted. Cache policy, stage count, geometry, MMA, epilogue and public API defaults are unchanged.

- Warp0 announces and issues weight payload A, then issues B and optional TMA SFB after the dependency wait. Warp1 announces and issues weight scales SFA, then rejoins the existing 128-thread small-SFB cp.async group after the wait.
- Each full barrier has two producer arrivals. Each warp independently waits for the same empty phase and uses `arrive_and_expect_tx` with only its own bytes. The installed DSL helper elects one lane internally. Neither issuer uses the old full-total `producer_acquire` in this specialization.
- Warp0's announced count includes deferred B/SFB bytes. That pending count and the second producer arrival jointly prevent completion before both weights and dependent activations arrive, regardless of whether A or SFA is issued first. MMA retains one full wait and one empty release.
- Both issuer states prime `min(num_stages, ceil_div(K,tileK))` initial stages, skip only those first-tile stages after the dependency wait, then advance identically through ring wrap and persistent next tiles. No extra barrier allocation, per-stage rendezvous or extra warp is introduced.
- The existing static-one-CTA/nonfused scatter admission excludes CLC and two-CTA kernels. Those paths retain the default false behavior. Zero-work CTAs still execute the dependency wait.

Source pins and exact delta are in `evidence/pdl-weight-scale-producer-r1`. Scoped pre-commit passes. The first gate attempt stopped in the observer while naming an unrelated combine artifact; it did not execute a dual-issuer kernel. Its evidence remains intact. The corrected observer requires the grouped-GEMM PTX signature and runs in `pdl-weight-scale-producer-r2-gate` without changing source.

The bounded gate covers K384 and K2304, N16/N128, three formats, PDL on/off, changing local/zero routes, explicit two-SM persistent continuation, and a two-CTA fallback. Named PTX binds exact FC2 compilation to each variant. Performance screening, if the gate/codegen checks pass, uses fixed N16 and the unchanged native10/100 cold-L2 CUDAgraph/CUPTI method at T4/32/128/512. First compare integrated versus candidate on V41 GPU2 with C-A-A-C; no native AUTO retention claim follows from a fixed screen.

## Result

Rejected after the V41 fixed C-A-A-C screen: T4/32/128/512 geometric means are NV1.000311×, MXFP8 0.993517×, mixed0.995178×. MXFP8 T32/128/512 and mixedT4/T32 regress in both repeats; the NV T32 gain coincides with an unchanged W4A16 control gain. No V3 or native AUTO sweep is justified by this screen. All receipts, raw medians and exact source remain under `evidence/pdl-weight-scale-producer-r1-fixed`; GPU2 is released.

The135 replay gate passed. Named PTX uses one elected per-issuer40960/4096-byte announcement, full barriers with2arrivals, and the existing128-thread SFBcp.async commit. The OFF K2304 specialization is byte-identical to the integrated single-issuer artifact. Compiled resource usage remains106registers forK2304; K384 changes114→110, with zero local/stack use. These resource counts are compiler outputs for the named gate shapes, not performance proof.
