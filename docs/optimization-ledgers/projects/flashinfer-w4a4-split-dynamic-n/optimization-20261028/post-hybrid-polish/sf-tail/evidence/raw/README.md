# Final-stage scale-copy prefix

The isolated review starts at retained `61c2c367009340ca0ed218511ed9382512860f1b`.
Only `moe_swap_ab_kernel.py` is changed and unstaged. `source-local.json` binds
all 348 source files and proves that the existing FC2-hybrid control is byte
identical to the retained head for those files.

The MMA loop already peels the compile-time final K extent. This candidate uses
that same logical extent to limit SFA/SFB SMEM-to-TMEM copies to complete
four-scale words. The copy's original source and destination strides, row banks,
stage offsets and K96 dynamic-N remapping remain intact. A full-stage copy uses
its original tensors without rebuilding a view. All admitted base MMA K extents
divide `4 * sf_vec_size`, so rounding to this scale-copy granule also includes
every scale used by the final padded native MMA atom.

The full TMA transfer sizes, expected transaction byte counts, operand-ring
states, all waits/releases, PDL, scheduling and MMA arithmetic remain unchanged.
The skipped scale words are never read by the shortened instruction plan;
they need no initialization. This is distinct from the rejected independent SF
publisher and multicast experiments. Performance is unmeasured.

Qualification reuses the public-wrapper source-paired gate, with only diagnostic
shape/K-step overrides and compiler artifact capture. It covers full stages,
SF16 tails of 64/128, SF32 tails of 128, one/two CTA, N16/128/256, both CLC and
PDL states, empty/reactivated/skewed routes, and K96 dynamic-N tails. Every live
intermediate and final output is compared by storage bytes. GPU7 on the existing
`fi-moe-descriptor-recover-1028` C3 box is the sole assigned device. No sanitizer,
new repository tests or performance campaign is included.
