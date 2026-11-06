# Swap paired SiTU qualification

The frozen `b47bf19b` swap candidate passed 16 existing zero-tolerance exact calls and 24 native image pairs against immutable retained `49c91adf` sources. All native resources are identical, all kernels have zero local memory, and all 18 unaffected FC1/FC2/finalizer images are byte-identical. No performance timing has run.

The six affected FC1s retain 168 registers and unchanged launch/shared-memory configuration. Scalar EX2/RCP counts and `.approx.ftz.f32` modifiers match the control. Native arithmetic tracing checks all 384 tanh lanes, including beta 3.1: reciprocal of rounded FP32 beta, distinct RN −2 then log2(e) products, scalar SFUs, packed fused RN `2 * inverse - 1`, and the FP32 beta product. This preserves swap’s own rounding contract rather than using the W4 contract.

| Existing case | Control non-NOP | Candidate non-NOP | Change | Other native differences |
|---|---:|---:|---:|---|
| w4a4-0-Swiglu | 1148 | 1075 | -73 | Control/allocation/move changes; full opcode deltas saved. |
| per-token-9-Swiglu | 1861 | 1745 | -116 | Control/allocation/move changes; full opcode deltas saved. |
| mxfp8-11-Swiglu | 5432 | 4472 | -960 | Arithmetic opcode changes only; scheduling identity not asserted. |
| w4a8-15-Swiglu | 1932 | 1812 | -120 | Arithmetic opcode changes only; scheduling identity not asserted. |
| w4a4-13-Swiglu | 1329 | 1257 | -72 | Arithmetic opcode changes only; scheduling identity not asserted. |
| per-token-7-Swiglu | 2021 | 1899 | -122 | Control/allocation/move changes; full opcode deltas saved. |

Coverage includes NVFP4, per-token, MXFP8 and MXFP4×8; gate-only and gate+linear; ordinary and native CLC scheduling; one/two CTA; PDL on/off; partial/full and long K; ordinary SwiGLU and ReLU² controls. It uses the existing finite-output oracle and does not establish universal NaN-payload behavior.

The candidate adds 40 source lines net (+53/−13), including one private pair helper. Fewer static instructions are not sufficient evidence to retain that added source complexity; the native instruction reordering must be evaluated by a separately authorized causal performance screen.

## Preserved orchestration boundary

The first attempt (`qualification/`) failed with `KeyError('metadata_matches_existing')` before native preflight, compilation or any GPU call. Its empty run receipt and archive remain intact. The retry (`qualification-r1/`) uses the exact package-runtime and cache receipts from the successful alpha qualification. Its entire recovery preflight block is byte-identical to that runner. All helper, compiler, resource guard and source-manifest bytes are unchanged; no resource exception was added.

The active local review was subsequently fast-forwarded to `2b8eb9d8` across the disjoint retained W4 change. The b47 swap source and unstaged patch remain byte-identical (`composition-2b8/receipt.json`). The qualification still measures the original 49-based pair and makes no composed-performance claim.

Evidence: `qualification-r1/evidence/1793381604025822000/data`, archive SHA `78131c4285a2046a9f7221fea295ed2bcfc1e203a48cf1101d47efa773073b32`. The source/cache preflight and postflight both passed. `qualification-summary.json` and `native-arithmetic-proof.json` are replayable with the adjacent Python scripts.
