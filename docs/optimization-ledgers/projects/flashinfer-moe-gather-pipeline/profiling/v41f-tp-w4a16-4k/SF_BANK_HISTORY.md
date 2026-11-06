# Scale-load bank signal: exact prior and stop boundary

The current source-correlated SF load conflicts are real, but the simple
swizzle/ownership proposals already have matching historical evidence. No new
source or GPU experiment is justified by rediscovering them.

The current loaded PTX derives each scalar scale-word byte address as

```
shared_base + 82944 + 2048*raw_stage + 1024*transform_group
            + 4*warp_in_group + 16*lane + 512*word
```

There are two transform groups, four warps per group and two words per lane.
`analyze_sf_banks.py` checks the exact PTX expression and enumerates all 2,048
bytes of each of the four raw stages without duplicates or gaps. For a fixed
warp, `(address / 4) % 32 = (4*lane + warp) % 32`: eight banks receive four
different words each. This agrees with both measured scalar LDS sites at
`0x2be0`/`0x2c60`. These are distinct values, not redundant broadcasts.

Any permutation that preserves each 16-byte block leaves address bits 2–3
unchanged. Consequently it cannot spread this warp over more than eight banks.
The CPU replay explicitly checks ordinary B0/B1/B2/B3, M4/S3 XOR swizzles. A
transform-only pointer swizzle would additionally mismatch the plain producer
view: `moe_w4a16_kernel.py:479–498,988–1000,1336` uses separate logical SF and
TMA views of the same bytes. A legal producer/consumer atom change is a different
descriptor contract, not a one-literal fix.

The authoritative exact history is in the sibling project
`/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md`:

| Lines / mechanism | Recorded result and relevance |
|---|---|
| 621–652, wider scale staging swizzles | B1 was correct but retained the same N-way/excess counters; EP/TP GMs 1.0036x/1.0019x. B2 was correct but EP GM 0.9946x, minimum 0.9631x. This is the same low-bank-bit limitation. |
| 926–937, subgroup SF broadcast | Failed all three row-varying scale cases: different words collide in a bank. Loading one value and broadcasting is invalid. |
| 1178–1201, transpose four-warp transform ownership | Derives the identical `4*lane+warp` formula. The conflict-free permutation passed some shapes but failed route8 and route128 numerics because TMEM store ownership cannot move independently. No timing followed. |
| 1203–1218, transpose the TMA scale atom | Changed canonical `16*m0+4*m1+k1` to `4*m0+128*m1+k1` in producer and consumer views. One tactic failed CuTe layout equivalence; another descriptor produced an illegal instruction. A new supported descriptor proof would be required to distinguish another attempt. |

These older experiments used a different pipeline revision; their latency
ratios are historical, not estimates for retained `2b8`. The identical address
formula and failed descriptor/ownership mechanisms are the relevant exclusion.
The newer CLOSED_LEADS index and current gather notes did not contain these
exact entries; the sibling ledger resolves that search gap.

The four current packed-weight LDS.128 sites have four **ideal** wavefronts and
zero excess. The old packed-weight B128-swizzle rejection at lines1153–1176
already warns against treating width-required wavefronts as conflicts. Current
SF wavefront excess is not itself an E2E speedup budget; the scalar load PCs
have only 9 and 10 observations, and their consumers share other dependencies.

This closes ordinary SF swizzle, duplicate-load broadcast, and independently
transposed transform ownership. A supported TMA atom transform with unchanged
external weight packing would need a materially new proof and cost argument.
No such mapping is proposed by this read-only audit.
