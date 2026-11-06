# FC1 CLC request for all admitted CTA groups

Only the FC1 host request changes: `cluster_shape_mn == (1, 1)` becomes `True`. The generic allocated-work, explicit SM reservation, and CUDA grid-Y guards remain. Control is frozen `f4aaa68d…`; candidate is `21368ce8…`. Both use 40 admitted geometry pairs and the then-current queued-K planner. This experiment does not include the later explicit K tactic extension.

Sequential C1 → A1 ran on the same B300 GPU5, V41-Flash EP4, tokens4/128/4096, native AUTO,10 warmups/100 graph/CUPTI repetitions, cold L2, fused finalize disabled. All15 result points completed. Exact source, helper, runtime, GPU and route checks pass (`comparison.json`); all raw outputs and AUTO caches are preserved in the sibling `generality-clc-auto-r1-{c1,a1}-v41-flash/raw` directories.

All four affected T4096 arms resolve FC1 M256/N128, group2, CLC enabled:287 allocated route tiles ×18 channel tiles =5,166 work clusters, versus74 resident clusters. This is a source-derived constructor-dispatch proof using the immutable allocator/host code and actual148-SM device (`selected-dispatch.json`), not an instrumented cancellation-count trace. Mixed precision keeps both FC tactics unchanged; other prefill arms change FC1 one→two CTA. T4/128 use one-CTA FC1, where the requested CLC behavior was already enabled.

C1/A1 speedups atT4096: NVFP4 1.008665×, per-token NVFP4 1.007757×, MXFP8 1.008497×, MXFP4x8 1.005730×. Decode points are near neutral, ranging0.994766–1.001979×. The unchanged W4A16 T4096 control drifts0.976139×, so these data support closing the policy whitelist with final combined validation, not a reliable performance-gain claim. No repeat or retention campaign is claimed.

The source-private CuTe/native workspace setup receipts and exact arm commands are saved in `cache-setup/`; the same corrected canonical native include/lock setup is used by both arms. No frozen source was edited during or after timing.
