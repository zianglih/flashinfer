# Epilogue and extension compile-time dispatch audit

Reviewed retained `586994d8a054470a17c3dab05be8209c75a33128`, following repository `AGENTS.md` → `CLAUDE.md` and `docs/code_review_guidance.md`. This note records the source audit and the two subsequently approved epilogue changes. No CuTe compiler, GPU, reader or oracle was run.

Owned source paths below are relative to `flashinfer/flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/`.

## Conclusion

The static shape improvements are: use known H instead of a dynamic output dimension; specialize FC2 hidden extent128 for complete feature clusters; omit the FC1 feature-bound test for complete I clusters. The dynamic hidden tile offset, token predicates, original partial-H clips and partial-I feature predicate remain. The other configuration/optional branches already specialize, and the apparent constant `Int32` cases checked in native code already fold. Runtime phase, readiness, token-tail and thread predicates are required.

Root separately reviewed and approved both changes. Their first `epilogue.py` SHA256 was `95d5e3d1a38ca9304701b143d7640e809b9df1789ba1dff3e2a873a11b5298cd`:7 added/4 removed lines, one existing store body, no new field/helper/knob. The final aligned-H specialization below supersedes that source. `tmem_epilogue.py` and `custom_ext.py` are unchanged. Scoped hooks and diff checks pass; final native/runtime validation remains pending.

## Exact H contract and emitted evidence

`frontend.py:201–205` constructs `static_expert_shape=(local_experts, 2*I, H)`. `megamoe_kernel.py:174–175` requires this static shape and equality between its H and the kernel H. The epilogue retains the same tuple at `epilogue.py:69`. The output paths both have this H:

- Direct return: `frontend.py:377–378` validates `combine_output.shape == (capacity, topk, H)`; `_launch_fc12` chooses that tensor at `megamoe_kernel.py:532–536`.
- Reused dispatch return: the owned local region is `(pool_token_capacity, 1, self.hidden)` at `megamoe_kernel.py:1499–1508`; `_launch_fc12` selects this typed view at516–530.

Therefore `Int32(self.static_expert_shape[2])` and `Int32(self.fc2_output.shape[2])` have the same value for every admitted call. This substitution does not assume a full hidden tile: H32-aligned partial tiles and padded CTAs still need clipping against the live `tile_m_idx`. It changes neither pointer strides nor metadata visibility.

The completed N64/direct I2048 native capture at
`profiles/cu132-recovery0911c-ready-fc1-mapper-loop-candidate-n64-f4-direct-i2048/codegen/`
has the exact three owned files reviewed here. Its scheduler differs from retained; this evidence is used only to establish emitted behavior of these unchanged bodies, not retained whole-kernel identity or performance. `result.json:57–76` records their source pins:

| File | SHA256 before the one-line change |
|---|---|
| `epilogue.py` | `aece9f1f47fb1f4c1ce1a76684748eb05d61b8484e42458854ddf1d2bfa396fd` |
| `tmem_epilogue.py` | `54593512c8fde45e11c024af4b5105589b03a02045d10c0b14ad1ba5cec4a1a8` |
| `custom_ext.py` | `a4f690c006f25ea242674cc194bc68a87ed788a2fc1235c37cc2d3bba3097b40` |

Its sole `dsl/*.ptx` has SHA256 `a122ac51b63b2845684653f7e07afe711745aadea319d44073ef6557a894b46c`. At69 it loads `%r198` from kernel parameter8+16. At6797–6801, attributed to `epilogue.py:221`, it subtracts the live hidden tile base from that parameter, then emits `max.s32` and `min.s32 ...128`. Thus this is an actual dynamic dimension read, not merely a source-level annotation opportunity. The change should make the subtraction use the known H immediate; it does not promise removal of all clipping instructions or a latency gain.

## Branch and loop classification

| Source locations | Classification and action |
|---|---|
| `epilogue.py:61–74` | Python constructor normalizes optional flag batches and computes geometry, stage count and subtile count. Setup work, not device runtime dispatch. |
| `epilogue.py:195–205,231–243,291–297`; `tmem_epilogue.py:338–356,415` | Return mode, optional metadata/mapper and alpha presence are compile-time choices already selected with `const_expr`, or validated in plain Python. Preserve the separate direct metadata-prefetch and reused local-output paths. |
| `epilogue.py:272,328,533` | Release position is already a compile-time specialization. The fallback release still depends on whether the last token subtile is valid. Do not remove or reorder it. |
| `epilogue.py:314,365,482,509–510`; `tmem_epilogue.py:363,477,577` | Fixed subtile, SwiGLU, transpose-half, clamp and store loops already use `range_constexpr`. Clamp presence specializes, while an actual scale or clamp value remains an operand. |
| `epilogue.py:421–437` | The prior-subtile loop has zero iterations for N64 and one for N128, the only admitted token widths. Completed N128 PTX emits the first body guarded by `valid_tokens < 1` at6110–6113, then the last body guarded by `<65` at6701–6704, with no subtile-counter backedge between them. Adding constexpr syntax would be cosmetic. |
| `tmem_epilogue.py:186–201,244,271` | Fixed 16-register permutation methods are ordinary Python methods constructing traced expressions; their `range(16)` loops are not GPU runtime loops. Dtype/size validation is compile-time. |
| `tmem_epilogue.py:459–477,495,567` | The tuple of four fixed fragments, known fragment lengths and vector-width checks are structural trace-time inputs. Arithmetic/conversion loops are already static. No generic-loop rewrite is warranted. |
| `custom_ext.py:149,296–317` | SF-vector validation is host code. Tensor-name branches (`a`, `b/c`, `sfa`) are already `const_expr` over literal caller names. Expert and token offsets must remain runtime. |
| `custom_ext.py:158,253`; `epilogue.py:315,436`; `tmem_epilogue.py:576–578` | Conversion to `Int32` does not itself force runtime work. I2048's FC2 threshold appears as immediate31 in the acquire comparison (N64 PTX990–994); fixed subtile offsets fold. Keep the existing serialization/layout types. |
| `custom_ext.py:108,293` | Reserved record word zero is intentional; the singleton `Int32(1)` belongs to the consumed CuTe shape-rewrite contract. No demonstrated emitted dynamic overhead justifies changing its type. |
| `epilogue.py:129–160,299,316,423,437,545`; `tmem_epilogue.py:379,428,580`; `custom_ext.py:221–264` | These depend on actual work validity/phase, acquire readiness, dynamic route count, thread coordinate or output tail. They cannot be changed to compile-time dispatch without changing semantics. Peek branches may lower to selects; source `if` alone is not evidence of a hardware branch. |

The N128 evidence above is the completed `n128-f4-reuse-i2048/codegen/dsl/*.ptx` sibling, SHA256 `48426bf0c507f3ad03ae3d0c9a214491a9e8b0ba2e109a4ed02497ae2c74da5b`. Native file/line directives inside inline wait assembly can reuse nearby line numbers; the cited loop conclusion follows actual predicates and forward control flow, not counting `.loc` entries.

## Aligned-I specialization

`epilogue.py:545–547` checks the FC1 output feature bound on every vector store even when `I % self.cluster_tile_intermediate_downproj == 0`. The existing `signal_fc1_done` at341–350 already uses exactly this static alignment proof to omit its feature bound. Here each CTA writes64 features in four16-feature warp vectors; an aligned final cluster contains no OOB CTA or warp vector. The scheduler's monotone mapper assigns only `ceil(2*I / cluster_gateup_width)` feature clusters (`fc1_fc2_fuse_sched.py:396–400,846–871`). The N64 I2048 PTX nevertheless emits `setp.gt.s32 ...2047` at6407–6408 and ORs it with the token predicate at6421.

The approved edit initializes `in_bound` with the existing token predicate, then appends the exact original feature predicate only under `const_expr(I % cluster_tile_intermediate_downproj != 0)`. One final `if in_bound` contains the unchanged store body. Token-tail checks, scratch reads/releases and BF16 conversion remain. No extra constructor flag or public knob is needed, since the alignment value already exists. This static branch still needs lowering and numerical validation; source equivalence for the partial-I path does not establish generated-code equivalence.

## Final aligned-H specialization

Root approved completing the analogous FC2 shape proof after the first native4 capture closed. The constructor now stores `cluster_tile_hidden = _EpilogueFc2HiddenTileSize * cluster_shape_mn[0]`, a Python geometry value. `_make_output_router` starts with valid_hidden128; only `H % cluster_tile_hidden != 0` traces the static-H subtraction and both original clips. Token, metadata and store predicates otherwise remain.

For all admitted M128/C1, M128/C2 and M256/C2 geometries, the split helper computes CTA M as `mmaM / size(tiled_mma.thr_id)` =128 (`dense_gemm_bf16_fp4_sm100.py:150–154`). The fused scheduler assigns `ceil(H/(128*C))` FC2 feature clusters, with CTA index `cluster_feature_idx*C + cta_rank`. If H is divisible by128*C, every assigned CTA therefore owns exactly128 real hidden features. There is no direct/reused-return distinction: both output tensors have the validated same H. H%128 alone would be wrong for C2: H128 still has a padded second CTA. Partial H288/H7200 must retain the clips, including zero output for fully padded CTAs.

Final epilogue SHA256 is `68674590e949b5d56b7375fa20fd9b98cdf5f109e45ad23570809aa1a9512fd9`; the incremental `aligned-hidden.patch` SHA256 is `3f7d280a93aba195c4c46423ee23187c58e9a6c659edaf67de56f5e60666ead5`. All scoped pre-commit hooks including mypy/Ruff and diff checks pass. No layout, pipeline, release or public configuration changed. Final native evidence must verify full-H clip/hidden-predicate elimination and unchanged partial-H behavior; the earlier capture is evidence only for the preceding static-H and FC1 changes.

## Validation boundary

Local syntax and diff checks establish only source validity and scope. Existing native capture helpers should later verify direct and reused return paths, the static-H operand, omitted FC1 feature comparison for aligned I, retained comparison for partial I, unchanged resource/stage counts and release/metadata order. Existing I2048 and I2112 fixtures cover full and partial C2 feature clusters; the existing M128/C1 static/S3 case covers the alternative cluster size. Reuse existing H288/H7200 partial-hidden reference/routing cases and aligned-H cases, with I448/2112 partial-I and I256/2048 full-I examples. Preserve both return modes and empty/refill token tails. No new harness, benchmark, tolerance or claimed speedup is justified by this audit alone.

C1 coverage is project-local, not part of the current upstream C2 test products: `candidates/w4a16_ready_fc1_window/execution/run_routing_ready_v2.py:39,69` supplies case2 H256/I2048 M128/C1 static/S3/direct and case6 H7200/I2112 M128/C1 atomic/S2/direct to the unchanged routing oracle. The same worker includes partial-I C2 direct and reused-return cases. These are reusable validation inputs, not evidence that the new epilogue has already passed them.

Final native follow-up: `NATIVE_REVIEW002.md` records PASS on source dd4ce416. Full-H clips/hidden predicates and full-I feature predicates are absent; partial H7200/I2112 remains byte-identical to the preceding capture. Resources/stages are unchanged. Focused numerical tests were released after this admission; no numerical or performance result is asserted here.
