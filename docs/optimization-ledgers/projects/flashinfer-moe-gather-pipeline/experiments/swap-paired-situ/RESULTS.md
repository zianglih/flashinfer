# Swap paired SiTU — rejected

Reject the `b47bf19b` candidate. Across 66 retention cells, E2E geometric mean improved only **0.113%**, with **22 negative rows**, while the source adds 40 lines net (+53/−13) and one private helper. The 78 raw cells include tokens 1/2 and give +0.107%, with 25 negative rows. The result does not justify the added implementation complexity. No reverse-order repeat, narrowed policy, further timing or publication refresh is planned.

| K3 arm | Retention cells | E2E GM | Negative |
|---|---:|---:|---:|
| EP CuteDSL W4A4 | 11 | +0.276% | 3 |
| EP CuteDSL PER-TOKEN | 11 | -0.085% | 4 |
| EP CuteDSL MXFP4x8 | 11 | -0.228% | 7 |
| TP CuteDSL W4A4 | 11 | +0.433% | 1 |
| TP CuteDSL PER-TOKEN | 11 | +0.220% | 2 |
| TP CuteDSL MXFP4x8 | 11 | +0.061% | 5 |

Decode (4–64) is +0.100%, middle (128–512) +0.062%, and prefill (4096–16384) +0.184%. The prefill aggregate is not a dependable gain: candidate repeat spread reaches 5.993%. All 1,248 NVML quartiles are present; 23 show non-2032 MHz or nonzero throttle reasons. No rows or samples were filtered.

Component attribution preserves the E2E losses. EP per-token at 8 tokens is −2.069% with C/A repeat spreads 0.002/0.039%; routing extension rises 1.512 µs while FC1 duration falls 0.264 µs. EP per-token at 4096 is −0.685% with spreads 0.070/0.219% and FC1 duration rises 2.305 µs. TP MXFP4×8 at 8192 is −1.130% with spreads 0.211/0.202%; observed clocks include 1845 MHz/reason 4. EP MXFP4×8 at 16384 is −1.452% with candidate spread 2.277% and FC1 duration rises 11.441 µs. These are attribution observations, not reasons to discard losses; overlapping component medians are not summed into E2E.

All six complete CAAC jobs use the immutable 49 control and b47 candidate, original frozen choices/routes, quant included, strict CUPTI 100 samples after 10 warmups, cold L2 and the unchanged timing helpers. All 31,200 raw intervals and 312 phase medians replayed; 360 loaded resource records are LOCAL0. All 90 paired actual resource configurations, dynamic shared allocation and occupancy are unchanged. Source/cache preflight and postflight passed, and GPUs 0/2/4/6 were released.

The complete primary [78-row table](../../evidence/swap-paired-situ-screen/1793382854980524000/report/table.md), [retention matrix](../../evidence/swap-paired-situ-screen/1793382854980524000/report/matrix.md), component tables and all raw phases remain under the same evidence leaf. Archive SHA: `dc4b415d01ee2507a794679338dfa458f93b56942a01e3d79a9bafe4a94817bc`. Independent raw replay: `audits/swap-paired-situ-data-root.json`.

## Exact/native qualification
The frozen `b47bf19b` swap candidate passed 16 existing zero-tolerance exact calls and 24 native image pairs against immutable retained `49c91adf` sources. All native resources are identical, all kernels have zero local memory, and all 18 unaffected FC1/FC2/finalizer images are byte-identical. No performance timing was run during this qualification.

The six affected FC1s retain 168 registers and unchanged launch/shared-memory configuration. Scalar EX2/RCP counts and `.approx.ftz.f32` modifiers match the control. Native arithmetic tracing checks all 384 tanh lanes, including beta 3.1: reciprocal of rounded FP32 beta, distinct RN −2 then log2(e) products, scalar SFUs, packed fused RN `2 * inverse - 1`, and the FP32 beta product. This preserves swap’s own rounding contract rather than using the W4 contract.

| Existing case | Control non-NOP | Candidate non-NOP | Change | Other native differences |
|---|---:|---:|---:|---|
| w4a4-0-Swiglu | 1149 | 1076 | -73 | Control/allocation/move changes; full opcode deltas saved. |
| per-token-9-Swiglu | 1864 | 1746 | -118 | Control/allocation/move changes; full opcode deltas saved. |
| mxfp8-11-Swiglu | 5447 | 4487 | -960 | Arithmetic opcode changes only; scheduling identity not asserted. |
| w4a8-15-Swiglu | 1937 | 1816 | -121 | Control/allocation/move changes; full opcode deltas saved. |
| w4a4-13-Swiglu | 1330 | 1258 | -72 | Arithmetic opcode changes only; scheduling identity not asserted. |
| per-token-7-Swiglu | 2025 | 1901 | -124 | Control/allocation/move changes; full opcode deltas saved. |

Coverage includes NVFP4, per-token, MXFP8 and MXFP4×8; gate-only and gate+linear; ordinary and native CLC scheduling; one/two CTA; PDL on/off; partial/full and long K; ordinary SwiGLU and ReLU² controls. It uses the existing finite-output oracle and does not establish universal NaN-payload behavior.

The candidate adds 40 source lines net (+53/−13), including one private pair helper. Fewer static instructions are not sufficient evidence to retain that added source complexity; the native instruction reordering must be evaluated by a separately authorized causal performance screen.

## Preserved orchestration boundary

The first attempt (`qualification/`) failed with `KeyError('metadata_matches_existing')` before native preflight, compilation or any GPU call. Its empty run receipt and archive remain intact. The retry (`qualification-r1/`) uses the exact package-runtime and cache receipts from the successful alpha qualification. Its entire recovery preflight block is byte-identical to that runner. All helper, compiler, resource guard and source-manifest bytes are unchanged; no resource exception was added.

The active local review was subsequently fast-forwarded to `2b8eb9d8` across the disjoint retained W4 change. The b47 swap source and unstaged patch remain byte-identical (`composition-2b8/receipt.json`). The qualification still measures the original 49-based pair and makes no composed-performance claim.

Evidence: `qualification-r1/evidence/1793381604025822000/data`, archive SHA `78131c4285a2046a9f7221fea295ed2bcfc1e203a48cf1101d47efa773073b32`. The source/cache preflight and postflight both passed. `qualification-summary.json` and `native-arithmetic-proof.json` are replayable with the adjacent Python scripts.

The independent peer caught omitted uniform-predicated instructions in the initial static-count parser. `parser-v0/` preserves that report and proof. The final parser accepts both ordinary and uniform predicates and asserts that every address-bearing instruction line is counted. Final affected deltas are −73/−118/−960/−121/−72/−124; no runtime, source, exact result or resource claim changed.

## Retirement

The rejected local `flashinfer-swap-paired-situ-review` worktree and `codex/swap-paired-situ` branch were removed after exact head, owned diff, source SHA, staged/untracked and project-local Git checks. The kernel, patch, status, Git pointers and generated checker caches are preserved under `retirement/`; all remote frozen sources, helpers, native images and performance data remain. Canonical head/status stayed unchanged at `2b8eb9d8`. Only the swap-SiTU coordination entry was removed.
