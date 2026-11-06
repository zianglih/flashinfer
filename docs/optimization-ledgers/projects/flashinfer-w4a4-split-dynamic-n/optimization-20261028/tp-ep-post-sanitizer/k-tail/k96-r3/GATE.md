# K96 descriptor reuse R3

Frozen kernel: `9617d7da660d201a5e7c56bf33613cc24b1a20c05f8d1e022cd545c37efc31b5`.
Source receipt: `d7f5d010436e5ef91f8ccda1cf8f7742353257cfd1bd30af84db834172fca854`.
Gate receipt: `b4457b7038d1f19ba83268a79d6ff5ac8010f612d6de438ea8519a768dbc3c85`.

R3 changes only descriptor construction relative to R2. It builds the relative SDK descriptor once per acquired operand stage, derives static physical row-zero offsets from the partition layout, and preserves all descriptor fields except the current start address and K96 absolute LBO. The arithmetic update plan, scale publication, allocation, synchronization, public API, and tactics are unchanged.

The compile-time offset assertion proves SW128 source bits 9:7 are zero. Combined with 1024B stage alignment, the logical layout offset equals the physical pointer displacement. FP4 element offsets divide by 32 to give 16-byte descriptor units. K64 retains the relative LBO. K96 overlays the absolute next-segment address and mode bit 52. Shared-memory allocations remain below 256KiB, so an in-bounds address fits the 14-bit start/LBO fields; addition cannot carry into a neighboring field.

Validation:

- 68 exact cases pass: 12 cancellation discriminators and 56 geometry/CLC/PDL combinations, including selected-cache-hit replays. Both CTA groups, M128/256/512, N16/32/128/256, K256/512, masked final tiles and partial reduction tails are covered.
- 7 separate project-only descriptor checks pass. Every emitted descriptor is compared on GPU against the original SDK builder, trapping on any bit difference. Reduction 4096 ensures every allocated ring slot is exercised. These instrumented kernels are excluded from performance and ordinary codegen comparisons.
- 123 captured owned kernels have matching PTX/SASS identities, 1024B shared alignment and zero local-memory/stack use. 52 have effective CLC. This does not assert absence of uniform-register spills.
- 516 gate files independently hash-verified; archive SHA `7776d8313bf260cbe4b9995077d363e6ff0319972842a4109172d488edd6bd56`.

Actual frozen-winner codegen is recorded in `codegen-summary.json`. R3 versus R2 total SASS instruction changes: K3 decode FC1−32/FC2−32; K3 prefill FC1+16/FC2−24; V3 prefill FC1−8/FC2−8. K3 prefill FC1 adds two uniform spill/fill pairs relative to R2, but remains seven pairs below K64. Other uniform spill/fill counts are unchanged or lower. Static instruction counts are not performance claims.

The final matched performance screen compares R3 against the retained tail-only K64 source with identical frozen winners. C-A-A-C, 100 CUPTI samples per phase, 10 warmups and cold L2. All four models, both EP/TP, W4A4/per-token, tokens 4/64/4096/16384; 64 cells. Standard medians are primary; time strata remain diagnostic. No baseline rerun, tuning, or published-cell replacement.
