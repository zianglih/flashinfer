# W4 final-stage dequantization: native pilot evidence

The affected native FC1/FC2 kernels skip group1 only when its entire128-element interval is outside logical K. Shared raw/decoded stage waits and completion arrivals remain common.

| Kernel | Logical K | Native skip branch | Skipped static region | Scale/payload/TMEM store sites |
|---|---:|---|---|---|
| FC1 | 384 | `0x3130 BRA.U UP0, 0x3d20` | `0x3140–0x3d10` | 2 / 4 / 8 |
| FC2 | 640 | `0x3a20 BRA.U UP0, 0x46d0` | `0x3a30–0x46c0` | 2 / 4 / 8 |

The bypassed region includes FP4 unpack, scale conversion and BF16 scaling. Counts are static instruction sites bypassed by the final inactive warpgroup, not whole-kernel instruction reductions. FC1 adds24 static instructions and FC2 adds32 for the two-CTA pilot. Both keep96/128 registers and zero local memory.

For aligned H256/I256, all FC1, FC2 and combine PTX/cubin/SASS are byte-identical. The same holds for the one-CTA/CLC/PDL-off aligned control in the completed remaining group. The one-CTA/CLC affected kernels add16 static instructions each without resource growth.

No performance conclusion is drawn. This branch must justify its extra control work in the separately gated performance screen.
