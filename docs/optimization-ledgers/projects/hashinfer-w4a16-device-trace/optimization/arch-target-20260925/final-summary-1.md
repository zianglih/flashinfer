# Full architecture ABBA: independent timing summary

PASS: `40d0ceb67aa67dbf366ff61f85309e8ef53aa743` / `df90d2d0aa8f65881624fef55fe7bcd8e1aa91a1227124796947a45e685cd716`. A=`sm_100f`; B=`sm_103a`. All ratios below are A/B: above 1 favors native SM103a.

12 serial trials, 108 cold rows, 10,800 untrimmed cold rank-MAX CUPTI samples and 51,200 hot tuner samples pass. All 640 rank/shape winner exports match source/target/tactic/cache receipts. The 160 distinct rank/shape output hashes agree across all four trials; all 640 output records are finite and repeated-bit equal. All 64 independent T128 reference records pass.

| Scope | Decode4–512 pooled GM | First A1/B1 GM | Reverse A2/B2 GM |
|---|---:|---:|---:|
| Native EP4 | 0.99449746 | 1.00969780 | 0.98868258 |
| Native EP8 | 1.00568443 | 0.99480828 | 1.01495604 |

Aggregate decode results are close to parity and change direction between orders in both topologies. The uniform row also changes direction. These data do not establish a consistent end-to-end advantage for either compilation target.

| Scope | Global T | A pooled µs | B pooled µs | Pooled A/B | First A/B | Reverse A/B | A2/A1 | B2/B1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| native EP4 | 1 | 73.1520 | 74.0485 | 0.987893 | 1.087642 | 0.919881 | 1.045542 | 1.236221 |
| native EP4 | 2 | 93.0085 | 98.4170 | 0.945045 | 0.882511 | 1.046059 | 1.090304 | 0.919838 |
| native EP4 | 4 | 116.7855 | 118.4815 | 0.985686 | 1.061368 | 0.948672 | 1.000141 | 1.118951 |
| native EP4 | 8 | 153.0895 | 151.9850 | 1.007267 | 0.986629 | 1.032776 | 1.012921 | 0.967662 |
| native EP4 | 16 | 207.5055 | 203.7620 | 1.018372 | 1.060303 | 0.989883 | 0.990944 | 1.061439 |
| native EP4 | 32 | 265.7625 | 265.9540 | 0.999280 | 1.008495 | 0.991593 | 0.972360 | 0.988934 |
| native EP4 | 64 | 292.9945 | 302.2100 | 0.969506 | 0.986553 | 0.970500 | 1.014293 | 1.031070 |
| native EP4 | 128 | 321.4275 | 325.5225 | 0.987420 | 0.975272 | 1.015550 | 0.996869 | 0.957332 |
| native EP4 | 256 | 326.7550 | 331.0910 | 0.986904 | 0.982841 | 1.001326 | 0.997113 | 0.978706 |
| native EP4 | 512 | 353.2680 | 352.4350 | 1.002364 | 1.020182 | 0.961928 | 0.963531 | 1.021883 |
| native EP4 | 4096 | 794.3115 | 796.0545 | 0.997810 | 0.989057 | 1.010566 | 1.019307 | 0.997611 |
| native EP4 | 8192 | 1440.2990 | 1451.8680 | 0.992032 | 0.991620 | 0.958822 | 1.006611 | 1.041043 |
| native EP4 | 16384 | 2861.1270 | 2854.0695 | 1.002473 | 1.001729 | 1.001992 | 1.002975 | 1.002712 |
| native EP8 | 1 | 71.4560 | 77.3450 | 0.923861 | 0.931471 | 0.941507 | 0.941101 | 0.931070 |
| native EP8 | 2 | 95.0410 | 94.3845 | 1.006956 | 0.990592 | 1.002930 | 0.967194 | 0.955296 |
| native EP8 | 4 | 107.3770 | 104.5760 | 1.026784 | 0.989126 | 1.047738 | 0.994503 | 0.938869 |
| native EP8 | 8 | 126.3375 | 126.3365 | 1.000008 | 0.966359 | 1.034309 | 1.026650 | 0.959203 |
| native EP8 | 16 | 139.8890 | 146.5770 | 0.954372 | 0.945238 | 0.962630 | 1.026311 | 1.007769 |
| native EP8 | 32 | 171.6815 | 164.4180 | 1.044177 | 1.045471 | 1.042717 | 0.987024 | 0.989630 |
| native EP8 | 64 | 188.0500 | 190.0015 | 0.989729 | 0.979378 | 1.000436 | 0.971424 | 0.950977 |
| native EP8 | 128 | 198.6725 | 192.4495 | 1.032336 | 1.031271 | 1.033158 | 0.997511 | 0.995689 |
| native EP8 | 256 | 200.3380 | 198.9930 | 1.006759 | 1.011632 | 1.003313 | 0.984545 | 0.992709 |
| native EP8 | 512 | 201.5685 | 202.7525 | 0.994160 | 0.993863 | 0.998289 | 1.029688 | 1.025122 |
| native EP8 | 4096 | 466.5640 | 471.9865 | 0.988511 | 0.995471 | 0.981057 | 0.982826 | 0.997266 |
| native EP8 | 8192 | 775.8440 | 800.7080 | 0.968947 | 0.960622 | 0.974275 | 1.008862 | 0.994725 |
| native EP8 | 16384 | 1505.2085 | 1494.4220 | 1.007218 | 1.010888 | 1.016231 | 1.022251 | 1.016877 |
| uniform128 EP4 | 128 | 279.8420 | 287.2510 | 0.974207 | 1.005275 | 0.961974 | 0.993727 | 1.038457 |

Selected tactics: E=`epi_warps`, D=`reuse_dispatch_warps`. All use M=K=256, cluster(2,1,1), two-CTA MMA, flag batch4, epilogue flags(2,4), scheduler depth2, atomic-counter scheduling and deterministic combine.

| Scope | Global T | A1 | B1 | B2 | A2 |
|---|---:|---|---|---|---|
| native EP4 | 1 | G512/N64/E | G512/N64/E | G512/N64/E | G1024/N64/E |
| native EP4 | 2 | G1024/N64/E | G1024/N64/E | G512/N64/E | G1024/N64/E |
| native EP4 | 4 | G512/N64/E | G1024/N64/E | G1024/N64/E | G512/N64/E |
| native EP4 | 8 | G1024/N64/E | G512/N64/E | G512/N64/E | G1024/N64/E |
| native EP4 | 16 | G1024/N64/E | G1024/N64/E | G1024/N64/E | G1024/N64/E |
| native EP4 | 32 | G1024/N64/E | G1024/N64/E | G1024/N64/E | G1024/N64/E |
| native EP4 | 64 | G1024/N64/E | G1024/N64/E | G1024/N64/E | G1024/N64/E |
| native EP4 | 128 | G1024/N64/E | G1024/N64/E | G1024/N64/E | G1024/N64/E |
| native EP4 | 256 | G1024/N64/E | G1024/N64/E | G1024/N64/E | G1024/N64/E |
| native EP4 | 512 | G1024/N64/E | G1024/N64/E | G512/N64/E | G1024/N64/E |
| native EP4 | 4096 | G1024/N128/D | G1024/N128/D | G1024/N128/D | G1024/N128/D |
| native EP4 | 8192 | G1024/N128/D | G1024/N128/D | G1024/N128/D | G1024/N128/D |
| native EP4 | 16384 | G512/N128/D | G1024/N128/D | G1024/N128/D | G512/N128/D |
| native EP8 | 1 | G1024/N128/E | G1024/N128/E | G1024/N128/E | G512/N64/E |
| native EP8 | 2 | G1024/N64/E | G512/N64/E | G1024/N64/E | G512/N64/E |
| native EP8 | 4 | G1024/N64/E | G512/N64/E | G1024/N64/E | G512/N64/E |
| native EP8 | 8 | G1024/N64/E | G512/N64/E | G512/N64/E | G512/N64/E |
| native EP8 | 16 | G512/N64/E | G512/N64/E | G512/N64/E | G1024/N64/E |
| native EP8 | 32 | G1024/N64/E | G512/N64/E | G512/N64/E | G1024/N64/E |
| native EP8 | 64 | G512/N64/E | G1024/N64/E | G1024/N64/E | G512/N64/E |
| native EP8 | 128 | G1024/N64/E | G512/N64/E | G512/N64/E | G512/N64/E |
| native EP8 | 256 | G1024/N64/E | G1024/N64/E | G512/N64/E | G1024/N64/E |
| native EP8 | 512 | G512/N64/E | G512/N64/E | G512/N64/E | G512/N64/E |
| native EP8 | 4096 | G1024/N128/D | G1024/N128/D | G1024/N128/D | G1024/N128/D |
| native EP8 | 8192 | G1024/N128/D | G1024/N128/D | G1024/N128/D | G1024/N128/D |
| native EP8 | 16384 | G1024/N128/D | G1024/N128/D | G1024/N128/D | G1024/N128/D |
| uniform128 EP4 | 128 | G512/N64/E | G1024/N64/E | G512/N64/E | G1024/N64/E |

Notable qualifications:

- EP4 T64 favors family SM100f in both orders (A/B0.986553/0.970500) with the same tactic in every trial. EP8 T16 also favors family in both orders (0.945238/0.962630), but A2 changes group size.
- EP8 T32 favors native SM103a in both orders (1.045471/1.042717), with different group sizes between targets. EP8 T128 favors native in both orders (1.031271/1.033158); the reverse pair uses the same tactic.
- Prefill favors family at EP4 T8192 and EP8 T4096/T8192 in both orders. Native wins T16384 in both topologies/orders; EP4 uses different group sizes, while EP8 keeps the same tactic.
- The largest repeated-arm movement is EP4 T1: native B2/B1=1.236221, despite the same native tactic. T1/T2 remain in the full table and are excluded from the decode4–512 geometric mean.
- Direction flips occur in 10/13 EP4 native rows, 4/13 EP8 rows, and the uniform row. AUTO tactics differ across the four trials in 6/13 EP4 rows, 9/13 EP8 rows, and the uniform row.

All exported PTX headers identify NVIDIA NVVM23.0.0, compiler build CL-38657139, CUDA13.4 V13.4.59 and PTX9.4. The image/PyTorch runtime is CUDA13.2. Family PTX declares sm_100f while the installed cuobjdump prints sm_100; the native arm declares/displays sm_103a. Both representations are checked explicitly.

Hot selection scores and cold-CUPTI latencies are different measurements.
AUTO winners differ in some rows; comparisons measure the whole selected policy, not a universally matched-tactic architecture effect.
ABBA does not guarantee drift removal. Per-order direction changes are retained rather than averaged away.
Reference coverage is native and uniform global T128 only. Every other rank/shape has finite, repeated-bit and cross-run hash equality.
Only the selected main-kernel PTX/CUBIN target is explicitly audited; the process target override can also affect helper kernels.
All raw samples, trial medians, MADs, quarter medians, selected knobs and binary bindings remain in the underlying audit.
