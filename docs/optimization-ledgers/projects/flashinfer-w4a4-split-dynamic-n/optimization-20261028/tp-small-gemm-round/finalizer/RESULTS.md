# Finalizer geometry: rejected

> **Attribution corrected:** [ATTRIBUTION-CORRECTION.md](ATTRIBUTION-CORRECTION.md) supersedes the affected-cell interpretation below. Only8 W4A16 cells changed geometry (GM−0.554918%), not36 scaled/routed cells. Original raw data and analysis are preserved; rejection stands.

The existing exact-divisor5/7-vector policy was extended from expanded output to all routed layouts by removing one host layout predicate. All11 source-paired exact cases passed;22 compiled kernels had no local/stack storage. Affected routed variants raised registers (e.g H7168 FP32scales64→86), so a smaller CTA count alone is insufficient.

The fixed-winner144-cell screen collected57,600 strictCUPTI cold-L2samples across4models,EP/TP,4/64/4096/16384tokens and all supported families.36 affected prefillcells have geometric speedup−0.228%;EP−0.370%,TP−0.050%. Worst affected cell isV3EP MXFP4x8,T16384:−3.501%. This does not justify retention; canonical source is unchanged.

108 unchanged cells are separately recorded (GM+0.012%,range−4.401%…+2.129%); these are not evidence for a causal geometry effect and are not silently dismissed as noise. Full pass medians,drifts,source/winner/routing hashes and rawCUPTIsamples are in `evidence-v2/`, with verifiedarchiveSHA3fcbb6d42874d43ee6b3bf32fe64dd8a2d3299760a67f65fda0d979f99fe53cb. The firstarchive manifest namingcollision is documented in `archive-repair.md`;rawGPUdata were not rerun.

Source was isolated unstaged in `flashinfer-finalize-layout-review`; the closed local experiment copy was removed after hash/diff checks. Helpers,receipts,patch and rawresults are retained locally; persistentnativecaches are untouched. No sanitizer.
