# Static scale-factor selector review

Source reviewed: `flashinfer-static-sf-review`, base `82254e206a44b95d9925e4594fac936731f80d21`; candidate kernel SHA256 `8677cf213ca1dcb55ec9547116038ccf22e8b217f46435e28c4078c3ca8818c9`. Read-only review: no source edits or GPU runs.

**Verdict:** no correctness or maintainability blocker found. This removes redundant runtime address-bit extraction using an existing local layout invariant. It adds no policy, specialization axis, synchronization, or interface. Performance remains a separate qualification; fewer static instructions do not establish an end-to-end gain.

## Why the selector is static here

- `_blockscaled_dynamic_mma` builds its instruction sequence in a Python loop. `start`, `width`, and `tiled_mma.op.sf_vec_size` are compile-time integers. Replacing the two address-derived selectors with `(start // sf_vec_size) % 4` therefore adds no runtime division or modulo.
- Both scale tensors are constructed from the Float32 TMEM allocation plus whole-column offsets, then recast to the byte scale type (`moe_swap_ab_kernel.py:3030–3088`). SFA's second M256 channel bank also adds whole TMEM columns. These bases have zero byte-selector bits.
- Ordinary scale slicing advances along the same logical K coordinate for A and B. K96 explicitly indexes `start // 16`; its SFB narrow/wide adaptation changes the *whole-word* stride and bank placement (`:3117–3151`), preserving the low two byte-offset bits. Thus A and B have the same byte selector even when their TMEM row/bank layouts differ.
- The static descriptor begins with both SF selector fields clear. SFA occupies bits 29–30, SFB bits 4–5, dynamic N starts at bit 17, and K96 uses bit 31. The new OR operations do not overlap those other fields. The actual scale-address operands are unchanged.
- Partial K stages use the existing padded mixed-width sequence; `start` remains divisible by the scale-vector length. A fresh CPU enumeration checked 1,286,400 base/bank/stride cases, including SF32/FP4-K64 in addition to the historical SF16/K64, SF16/K96, and SF32/K32 cases. This is an arithmetic proof under the source-established byte-packed layout, not a substitute for native qualification.

The one-line layout comment is useful. No extra helper, runtime guard, public argument, or fallback is warranted. If this function later accepts arbitrary sub-byte-offset TMEM views, its caller contract must change; the current private call site constructs all views itself.

## Comparison with current surrounding code

Current Blackwell MegaMoE `sm100/next_cutedsl_megamoe/.../dynamic_mainloop.py:149–169` and Rubin MegaMoE `sm107/next_cutedsl_megamoe/.../dynamic_mainloop.py:83–104` both derive SF IDs dynamically from pointer bits. Their descriptor helpers accept arbitrary SF address values and do not expose the known K byte index. They are not examples of an existing constexpr selector implementation. Their bit assignments agree with this candidate. The candidate is justified by this split kernel's narrower, local construction contract, rather than by claiming that MegaMoE already does it.

The existing standard Blackwell/Rubin paths use the CUTLASS MMA abstraction instead of this raw descriptor helper. No shared utility or other backend behavior changes here.

## Fresh native evidence and resource boundary

Independently verified all PTX, cubin, and SASS hashes in the six successful exact-test processes and all 18 captured kernels. Every loaded kernel reports zero local bytes; decoded SASS contains no LDL/STL. The native guard checks the returned compiled library before its first launch. The finalizer is unaffected.

| Native specialization | FC1 static non-NOP instructions | FC2 static non-NOP instructions | FC1 registers | FC2 registers |
|---|---:|---:|---:|---:|
| NVFP4, M128/N16, K96 | 1084 → 1065 | 720 → 701 | 168 → 168 | 82 → 82 |
| W4A8, logical M512/N128 | 4433 → 4322 | 3077 → 2941 | 168 → 168 | 116 → 118 |
| MXFP8, logical M512/N128 | 4433 → 4322 | 3077 → 2941 | 168 → 168 | 116 → 118 |

The MX FC2 register increase is real, so this is not a universal register-count reduction. Actual FC2 launches have 256 threads and no setmaxregister redistribution; the compiler's `max_threads=512` is a resource limit, not the launch size. Both 116 and 118 registers fit the existing one-CTA-per-SM objective, and the reported maximum thread count is unchanged. The FC1 guard still proves the 384-thread initial pool can fund the 128/128/248 role quotas. No register donation hole was found.

Guard limitations are explicit: FC2 checks launch compatibility and zero local allocation, not an arbitrary register ceiling or a runtime occupancy query. That is sufficient for this same one-CTA target and observed allocation, but it does not claim unchanged occupancy for every future specialization. Static opcode counts also include compiler rescheduling and uniform-register choices, not just deletion of the original three source expressions.

The fresh six-process qualification is narrower than the historical 41 exact tests / 80 codegen pairs. In the fresh compiled configurations, all scheduler predicates resolved to ordinary/static scheduling even though the correctness harness requested a CLC tactic. Fresh coverage includes K96 narrow N and the two-CTA M512 MX specializations; it does not independently requalify the wide-N K96 bank transition, every activation, or SM100. That is a qualification boundary, not a discovered source defect. Current native timing proceeds separately under its own measured source/configuration receipts.

Evidence: `audits/static-sf-peer.json`, `experiments/static-sf-selector/fetched/evidence/`, and `experiments/static-sf-selector/codegen-summary.json`. Historical proof was inspected only as supporting context; no historical timing was promoted to a fresh result.
