# w4a8 gated-layout campaign

This version preserves the frozen w4a8 sweep byte-for-byte and uses an
explicit per-arm preparation contract. The baseline tools and their full
original protocol are archived under `tools/baseline/` in each campaign.

Only gated W1 physical grouping changes from64 to16 on SM100/103; Rubin
retains64, and nongated/FC2 rows stay unchanged. All logical inputs, routing,
quantization, timing and AUTO controls stay unchanged. The source AST audit
and exact per-arm hashes reject any additional benchmark change.

Use `--baseline-tools` to select the original frozen mode directory and
`--reuse-baseline-r1` to preserve its completed13-point measurement. The
campaign executes candidateR1, candidateR2, baselineR2 in that order and
archives both tool versions and the accepted preparation diffs.

Grid:1,2,4,8,16,32,64,128,256,512,4096,8192,16384. Report T1/T2 but exclude
only those from retention. Same GPU/image/runtime, H7168/I2048, simulated
EP8/TP1,10warmups,100cold-L2CUDAgraphCUPTI samples,PDLon,normalAUTO.
W4A8 requires fused finalize; other full-MoE modes are unfused. Homogeneous
results are independent BF16 FC1/FC2 microbenchmarks.

The complete commands and scope are in `scripts/post-layout/README.md`.
