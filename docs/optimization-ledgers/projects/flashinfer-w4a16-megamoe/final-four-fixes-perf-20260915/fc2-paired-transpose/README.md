# FC2 paired transpose proposal

**Unapplied experiment proposal.** No production checkout, frozen source, GPU
run or active helper was changed. No performance or sanitizer result is claimed.

The patch is based on native `979ac4bd532ca1d9e2f5309b3935e77b0759d30d` and changes
only `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/tmem_epilogue.py`: **46 added,
18 removed lines**. `candidate.patch` SHA256 is
`0337d1dcea9d79150112ff280dcdb3085a6da0e8cd9a5fa7c957746371a417f7`.
The base file SHA is `a27abc13871e85671ce17c28ef619738ecb586ea9fe598424a771569ea02920a`;
the proposed file SHA is `2093de641b8e416196b56df2671d2e48eab31a65b68e35f8a507e6b8790f53a5`.
`manifest.json` also pins the unchanged epilogue and kernel callers.

## Small implementation change

The existing three store methods retain their exact default operation order.
A private `_wait: cutlass.Constexpr[bool] = True` parameter lets the new fixed
two-half helper supply their waits. Its six `_wait=False` calls are the only
call sites disabling those defaults. This adds no runtime branch, public option,
tactic, allocation or new class hierarchy. The now-unused owned single-transpose
wrapper is replaced by the paired helper; its only production callers were these
two FC2 calls. FC1 uses the individual round methods.

FC2 already prepares both packed BF16 inputs. The new helper advances both
existing transpose objects through each round together. FC1 continues calling
the existing default store methods; its `979ac4bd` behavior is unchanged. Input
gather, the two constructor pointer/input expressions, every per-half atom and
permutation, output variables and final BF16 scatter are unchanged.

| Boundary | Proposed order | Retained obligation |
|---|---|---|
| Initial/R1 | Both register permutations → load wait → both R1 stores → store wait | Finish all four raw accumulator loads before scratch overwrite; finish both stores before R2. |
| R2 | Both R2 loads → load wait → both R2 stores → store wait | Finish reads before overlapping in-place writes; finish writes before R3. |
| R3 | Both top/bottom loads and register permutations → load wait → both R3 stores → store wait | Preserve the same overwrite and next-read edges. |
| R4/release | Each half's top/bottom loads and register permutation → unchanged caller load wait → release | Finish both final scratch reads before accumulator reuse. |

This changes **12 source-level waits to 6 per valid 64-token subtile**, excluding
the unchanged final stage-release wait. It does not yet establish the emitted
instruction count or a latency improvement.

PTX 9.3 specifies that a `tcgen05.wait::ld/st` completes all corresponding prior
operations issued by that thread; participation is uniform across the warp.
Each warp issues both halves here, so one shared wait covers both. The spec also
preserves true register dependencies from loads, while requiring explicit waits
for memory anti-dependencies. Thus R3 register permutation can remain before its
load wait, while the overlapping store stays after it. No inter-warp ordering is
removed or newly inferred. [Wait semantics](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#tcgen05-instructions-tcgen05-wait),
[register dependency semantics](https://docs.nvidia.com/cuda/archive/13.3.0/parallel-thread-execution/index.html#tcgen05-memory-consistency-model).

## Address and output proof

For warp `w ∈ [0,3]`, subtile `s`, half `h ∈ {0,1}`, a relative TMEM word is
`((32*w + dp) << 16) + 64*s + 32*h + col`.

- R1 store/R2 load use `S = [0,16) × [0,32)` in `(dp,col)`.
- R2/R3 stores use `D = [0,32) × [0,16)`; top/bottom R3/R4 loads partition `D`.
- `S ∪ D` has 768 words and remains within that half's 32-column region and its
  warp's legal 32-row band. The two halves, all four warps, and successive
  64-column subtiles are pairwise disjoint. N64/N128 need 6,144/12,288 distinct
  scratch words across four warps; neither exceeds the original accumulator view.
- Within each half the complete operation sequence is identical to the original.
  Only operations on disjoint halves are interleaved. Their register fragments
  are separate, and the shared waits close every original memory hazard.
- The unchanged class contract maps input `(lane,reg)` to output
  `(dp=2*reg+(lane//2)%2, col=(lane%2)*8+lane//4)`. The CPU tag oracle checks this
  bijection for 4,096 `(warp,half,lane,reg)` cells. Unchanged per-half operations
  plus unchanged gather/scatter preserve the existing output layout.

The caller in `epilogue.py` remains byte-identical. Valid subtiles stay under the
same uniform work-record guard. The last valid subtile's release-after-reorder
wait remains; the final invalid-subtile branch still drains earlier loads and
releases once, including zero-token tiles. Both token return modes retain the
same output routing and global stores. No proxy fence, barrier, pipeline
ownership or register-allocation setting changes.

## Register risk and validation boundary

The epilogue remains **144 registers** with initial maxregs 96 and the existing
61,440-register CTA pool. No increase or donation rebalance is proposed.
Interleaving extends both halves' fragment lifetimes: two helper objects expose
up to 64 named 32-bit fragment slots concurrently, versus roughly 48 when the
first result is retained during the second serial transpose. This is a source
liveness estimate, **not** an allocated-register count; permutations/temporary
copies may coalesce. Packed inputs, routing pointers and other epilogue state
also remain live. Spills or changed scheduling could outweigh the saved waits.

`python3 -B prove.py` passed a CPU-only structural/address model: default methods
match the base AST after constant folding, each half retains its operation
trace, constructor/gather/scatter expressions match, and both N64/N128 address
sets satisfy ownership/disjointness. Removing any of the six shared waits fails
the conservative pending-read/write model; a 16-column half stride overlaps and
is rejected. This is not execution of CuTe atoms or compiled numerical proof.
Ruff and `git apply --check` also passed; the source checkout stayed clean.

Before promotion, a separate authorized experiment must check actual O3 PTX/SASS
wait placement, epilogue register/spill usage and unchanged 144-register setting;
run exact-output and guarded TMEM controls for both halves; exercise both return
modes and N64/N128 tails; then compare the affected rows under the preserved
timing protocol. A favorable source-level wait count alone is insufficient.

## Applied trial

Applied on 2026-09-16 as local native `71f94c12` and HashInfer `f14a1b1`, after restoring the unpromoted FC1 early wait. The native parent `7717228f` contains only validated host/preflight changes relative to corrected baseline `a48e5706`. The corresponding Hash parent is `e0f6b4c`, relative to `59dc674`. The proposed transpose bytes are unchanged; package imports normalize identically. Scoped pre-commit passed. GPU code generation, resource checks, numerical qualification and performance remain pending. The earlier proposal-base references above preserve the design history.
