# tcgen05.ld.red is not a drop-in final epilogue load

**Do not implement this replacement.** SM103 supports `tcgen05.ld.red.max.abs`, but its legal reduction shapes do not match the current R4 output ownership. A compatible path would need a new transpose/ownership design or an extra store; no simple general replacement was established. No GPU work or production edit was performed.

The [official PTX load contract](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#tensorcore-5th-generation-instructions-tcgen05-ld) restricts reduction loads to32x32b and16x32bx2. It reduces across the loaded columns of each TMEM lane; the latter shape adds a second half at an immediate address offset, not a programmable per-value gather. The reduction requires at leastx2. Both support and asynchronous completion must be respected; changing a load to a reduction load does not remove its completion requirement.

## Exact R4 ownership

Current paired R4 performs two16x128b.x4 loads at row offsets0/16, then `perm1`. CUTLASS `references/cutlass/include/cute/atom/copy_traits_sm100.hpp:744` gives the eight-value load's bit offset:

`32*(lane%4) + 512*(lane//4) + 4096*(reg%2) + 128*(reg//2)`.

For each final channel, let `p=perm1[channel]`, `half=p//8`, `reg=p%8`. The physical row is `16*half + lane//4 + 8*(reg%2)`; column is `lane%4 + 4*(reg//2)`. Therefore one final token lane spans four TMEM rows and four strided columns in each. Inverting gives token=`4*(row%8)+(column%4)`: every physical row contains four tokens. `prove_mapping.py` checks all512 elements against the exact CUTLASS trait and verifies no aliases/missing elements. It also proves every adjacent column pair already mixes tokens, blocking16x32bx2's minimum reduction width as well.

Concrete counterexample: only(row0,col0)=1 and(row0,col1)=100 are nonzero. Final token0's correct maximum is1; a row0 reduction returns100 from token1. A different half-split offset cannot repair this row/column ownership.

Quantized non-per-token FC1 already computes activation **before** this transpose, so the values in its final scratch are suitable arithmetic inputs; the blocker is layout, not activation placement. Per-token FC1 activates afterward and writes BF16 without this scale reduction. SF32 additionally combines the existing two16-channel fragments and cannot combine maxima that already mixed tokens. All-NaN/+0 filtering would also need the existing final zero convention if a compatible layout were ever designed.

## Why attention can use it

`flashinfer/attention/prims_ts/kernels/tcgen05_compat.py:28–96` wraps32x32b max with native DSL or inline PTX, architecture-gated forSM103/SM107. `fmha_context/fmha_resources.py:3994–4047` loads contiguous score columns for one query row per lane and merges hardware chunk maxima after a load fence. Its Sage path around4817–4856 similarly reduces each contiguous16-key score block before scaling. Those layouts already align the hardware reduction group with the mathematical row. They do not provide a rearrangement primitive for the four-token rows here.

CUTLASS32dp32b16x trait at1594 maps a thread to one row and contiguous columns. Its16dp32b traits and PTX immediate half offset preserve row-based reductions; neither has a strided-column reduction mode.

## History boundary

Targeted Markdown searches of `scripts/` and `fc1-gather-20261028/` found no earlier `tcgen05.ld.red` epilogue experiment. This is a bounded search result, not proof of absence. The rejected native-ownership epilogue is separately recorded in `../native-tmem-fc1-audit`; it must not be reopened merely to enable this instruction.

This search also recovered the earlier balanced-absmax experiment at `scripts/fc1_arithmetic_experiment/README.md` and its explicit closed-lead note in `scripts/regular_tma_non_tma_audit.md`. Oldabs3 used nine explicit PTX max calls and one NV16K test; the current eight-site constexpr tree has broader fresh evidence. It is a revisited idea, not a novel mechanism; see the amended closed-lead index.
