# Saved AUTO selection audit

Verified 182 measured-token snapshots.

| Comparison | T | Selected before | Selected after |
|---|---:|---|---|
| C1_to_A1/nvfp4 | 1 | N32; FC1 M128/1CTA; FC2 M128/1CTA | N64; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_A1/nvfp4 | 64 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_A1/mxfp8 | 64 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_A1/mxfp8 | 8192 | N128; FC1 M512/2CTA; FC2 M256/2CTA | N256; FC1 M256/2CTA; FC2 M256/2CTA |
| C1_to_A1/mxfp4 | 1 | N32; FC1 M128/1CTA; FC2 M128/1CTA | N16; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_A1/mxfp4 | 16384 | N128; FC1 M512/2CTA; FC2 M256/2CTA | N256; FC1 M256/2CTA; FC2 M256/2CTA |
| A1_to_A2/nvfp4 | 1 | N64; FC1 M128/1CTA; FC2 M128/1CTA | N16; FC1 M128/1CTA; FC2 M128/1CTA |
| A1_to_A2/nvfp4 | 64 | N32; FC1 M128/1CTA; FC2 M128/1CTA | N16; FC1 M128/1CTA; FC2 M128/1CTA |
| A1_to_A2/mxfp8 | 2 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| A1_to_A2/mxfp4 | — | No changes in 13 measured selections | — |
| C1_to_C2/nvfp4 | 1 | N32; FC1 M128/1CTA; FC2 M128/1CTA | N16; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_C2/nvfp4 | 2 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_C2/nvfp4 | 32 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_C2/mxfp8 | 16 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_C2/mxfp4 | 1 | N32; FC1 M128/1CTA; FC2 M128/1CTA | N16; FC1 M128/1CTA; FC2 M128/1CTA |
| C1_to_C2/mxfp4 | 2 | N16; FC1 M128/1CTA; FC2 M128/1CTA | N32; FC1 M128/1CTA; FC2 M128/1CTA |
| T1_to_T2/trt | 1 | (8, 254) | (8, 50) |
| T1_to_T2/trt | 2 | (8, 19) | (8, 156) |
| T1_to_T2/trt | 4 | (8, 321) | (8, 188) |
| T1_to_T2/trt | 16 | (8, 199) | (8, 104) |
| T1_to_T2/trt | 32 | (16, 99) | (8, 319) |
| T1_to_T2/trt | 64 | (8, 104) | (8, 69) |
| T1_to_T2/trt | 128 | (8, 200) | (8, 188) |
| T1_to_T2/trt | 256 | (16, 316) | (16, 302) |
| T1_to_T2/trt | 512 | (32, 38) | (32, 57) |
| T1_to_T2/trt | 4096 | (128, 52) | (128, 49) |
| T1_to_T2/trt | 8192 | (128, 57) | (128, 52) |
| T1_to_T2/trt | 16384 | (128, 57) | (128, 52) |

The T column is the measured token count. Token counts 1 and 2 are excluded from performance geomeans.
M512 is the logical FC1 tile with two M256 operations in a two-CTA cluster.

Source-reconstructed cached selections from each measured token's own SHA-pinned snapshot, not an independent executed-cubin trace. Cache counts are context only. Other buckets may be synthetic profiles. Cache contains winners and policy, no losing-candidate timings or winning margin. Tactic changes do not establish causality. TRT pair is (tile_N, config); config is an opaque native tactic ID, not FC2.

Helper SHA256: `21d2e7e3a42ebd3d6a2f0498e4bef166131b9c267d7d78ed4ddfe39edce26718`
