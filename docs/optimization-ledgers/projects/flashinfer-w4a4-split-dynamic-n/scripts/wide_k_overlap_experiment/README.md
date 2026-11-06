# Wider K with overlapping FC1 accumulators

Rejected after matched forward/reverse NVFP4 timing. Production is unchanged;
GPU7 is released. See [RESULTS.md](RESULTS.md) for raw medians and the
validation boundary, [summary.json](summary.json) for verified source/result
hashes, and [AUDIT.md](AUDIT.md) for the ownership proof.

Immutable control: `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. Task-local
modules; native diagnostic timing uses 10 warmups / 100 cold-L2 graph/CUPTI
samples. No primary baseline or AUTO rerun.

Scope: FC1 logical M512/N128 and M256/N256. Double the native K256 FP4 or K128
FP8/mixed load tile and use two operand stages. Preserve the MMA accumulation
order, dynamic N, output contract, weight layout, and fused epilogue. FC2 and
other FC1 geometries remain identical to the frozen control.

For NVFP4/SF16, NB2 K512 has 92 KiB/stage and two stages use 184 KiB. N256 K512
has 76 KiB/stage and two stages use 152 KiB; three stages exceed the CTA limit.
SFA/SFB occupy 96 TMEM columns. Protected96 yields accumulator windows [0,256)
and [160,416), with scales [416,512). The existing alternating 32-column slab
traversal can release after three protected slabs. This requires a fresh full
layout-address/ownership audit and six-format exact checks before native timing.
No register budget or warp-role changes are included.
