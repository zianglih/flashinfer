# Merged operand ring: independent source review

**No source-level blocker found; the final R2 repair also passes independent compiled-PTX ordering review.** The initial5d3 source review below is preserved as history; see the final R2 receipt at the end. This reviewer performed CPU/read-only inspection, no GPU execution or production/candidate source changes. The first compile exposed a CuTe scope error, which the source-only review did not establish absent.

## Frozen identity

Base HEAD: `aab93f854054de834447bdd8985b8bbd653fb3c8`. Only the Blackwell core is modified in `flashinfer-merged-operand-ring-review`; `git diff --numstat HEAD` reports145 additions/67 deletions in that file.

|Item|SHA256|
|---|---|
|Control core|`7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`|
|Reviewed candidate core and `selected_core.py`|`5d3a2b8964c0b6d85a52de0e8f80bd047a6ca4e10de7e07fc16691e439e243ef`|
|`source.patch`|`9fed253e8d940a177ee8e627ddd8cdcce8e2d1541b99f64ae4f84c17a17acc00`|
|`manifest.json` at review|`8ce995ed7e466c9495b65c464fe1f4f4f0ccb61d3b8a83f203ddcd4081304e5c`|
|Unchanged Blackwell `utils.py`|`9811c53e0faa4ab39bc8dd3b03152498958938ff17761fdad57a0afae6ede889`|
|Unchanged Blackwell `custom_pipeline.py`|`13dcd385670bb2a14b7134ea12ce5d7a1862be413947068da6ff06dc8e824662`|
|`../epilogue_codesign_audit/installed_api.json`|`0068b929930f479a677e8b54db9c1c0b1d4b0081fdf0cb294614ebfe29075b63`|
|Older matching installed API receipt `../producer_roles_experiment/distributed_tma/receipt.json`|`860c67d8e152c6568d61243d6af521bbd4033b99a501695823fde5d448e61bb5`|

The initial `e6edb147…` review is superseded by the candidate hash above. The only update makes the A/SFA/B byte-selection branches explicit; all three return `cutlass.Int32`, and the enclosing `warp<3` guard makes the final `else` exactly warp2.

## Arrival and transaction accounting

Candidate core line references refer to `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py` in the candidate clone.

- Gate `:356–361` is `cta_group_size==1 && !tma_sfb && overlap_epilogue`. It retains288 threads. The scope includes eligible FC2 and other format combinations at N16/N32/N64; it is not an NVFP4-FC1-only gate. Group2, N128/N256 TMA-SFB, and160-thread inline paths remain disabled.
- Full-ring initialization `:913–928` requests131 arrivals. Exactly three elected TMA arrivals occur, one in each whole warp0/1/2 (`:1083–1118`). Saved installed `MbarrierArray.arrive_and_expect_tx` at helpers.py:456 elects internally. Do not add an outer election or call ordinary `a_pipe.producer_acquire` in this enabled branch: that would double-count or announce the aggregate bytes again.
- Warp0 announces `128*tile_k*weight_width/8*channel_tiles`; warp1 announces `sf_stage_bytes*channel_tiles`; warp2 announces `b_rows*tile_k*activation_width/8` (`:1092–1112`). The sum equals the unchanged TMA aggregate for this one-CTA/!tma_sfb gate. For native FP4 K512/N16:32768+4096+8192=45056 bytes. SFB cp.async bytes do **not** belong in this transaction count.
- Each issuer announces its bytes atomically with its arrival before its own TMA copies (`:1116–1181`). Outstanding reserved arrivals prevent an early completed phase while another issuer has not yet announced. An early TMA or SF completion cannot satisfy the phase while its remaining arrival count is positive.
- All128 SF-copy threads execute the unchanged predicated SF copy loop and then exactly one `arrive_cp_async_mbarrier` (`:1203–1247`), including threads whose copies zero-fill invalid rows. Saved installed helpers.py:419 directly lowers to `cp_async_mbarrier_arrive_noinc`, with **no election**. Therefore131=3 TMA arrivals+128 asynchronous per-thread arrivals. No ordinary full arrival or `ab.producer_commit` remains in the enabled path.
- The full object's stored aggregate `tx_count` is metadata until a standard TMA arrival consumes it. Enabled code bypasses that path and supplies explicit per-issuer bytes. Merely constructing `PipelineTmaUmma` does not add a transaction expectation (`custom_pipeline.py:190–205,251–274`; installed constructor excerpt).

## Stage reuse, phase and tail proof

Every producer thread waits the same empty stage before issuing either kind of copy (`:1067–1082`). All128 threads have the same persistent tile/K iteration count and advance their producer state exactly once at the bottom of that K iteration (`:1248–1251`). Warp0/1/2 can progress independently; the full barrier represents completion of all their work.

MMA waits the joint full before the retained `async.shared` fence (`:1462–1483`), then follows the unchanged SF-to-TMEM and MMA arithmetic. The later separate TMA wait is compiled out only for the merged gate. The SFB cp.async completion alone was never sufficient for TCGEN publication; the existing fence remains after the merged acquire.

After the final MMA consuming the stage, the enabled path emits only `a_pipe.consumer_release`; the old `ab` release is compiled out (`:1579–1590`). The empty object remains the original TCGEN consumer object with its original count; changing the full count to131 does not change empty completion accounting (`custom_pipeline.py:196–205,238–249`). The common post-MMA lifetime protects A/B/SFA/SFB before any producer overwrites that stage. Accumulator ownership and epilogue release are separate and unchanged.

Only warp0 drains the common empty ring (`:1298–1308`). It starts from `producer.clone()`, waits all `num_stages` with their corresponding phases, and advances only that clone. This matches the saved installed `PipelineAsync.producer_tail` wait-only algorithm at sm90.py:337–356. It never arms an unused full phase, so no phantom131-arrival generation is introduced. Waiting all stages covers out-of-order final completions; final whole-CTA barrier1 (`:1602–1604`) joins all producers/MMA/epilogue before teardown. Other producers reaching that barrier early cannot free storage while the drainer is pending. Zero iterations and a partially used final ring retain the original pipeline's initial-empty/phase semantics.

TMEM allocation/retrieval, final128-thread teardown cohort, epilogue barriers, PDL waits/triggers, stage counts, storage layout, accumulator geometry, and register policy are unchanged. Unused `ab_barriers` storage remains allocated; this candidate does not claim a shared-memory footprint reduction. Instrumentation pushes/pops stay paired within each participating warp; enabled labels describe the joint wait.

## Disabled branch and unchanged mathematics

An independent in-memory Python AST check found only `__init__` and `kernel` changed. `utils.py` and `custom_pipeline.py` are byte-identical to control. All other method ASTs match without transformation.

For the disabled case, the complete module AST matches control after narrowly specified normalization:

1. Substitute `self.merged_operands=False`, discard only its new assignment, and fold constant conditionals/neutral Boolean operands.
2. Normalize `warp<1` to `warp==0` using the invariant `warp=tidx//32>=0`.
3. Remove redundant nested `warp==0` guards only inside an already established warp0 branch.

This also checks disabled instrumentation labels, pipeline setup/waits/releases/tails, and the retained one-CTA SF publication fence. It establishes source equivalence under those assumptions, **not** byte-identical generated code or compiler control-flow lowering. In the enabled path, TMA tensor/SMEM coordinates, SF predicates/offsets, MMA arguments, epilogue code and arithmetic are unchanged; the intentional changes are issuing roles and dependency representation.

## Remaining compile/runtime boundary

Saved installed CuTe4.7.1 excerpts pin helpers.py SHA `87baa220853a4f64179300293f747f75a9f10008f5df3c91bdbc4f5c7d74243c` and sm90.py SHA `2d5fae60151278072a92dd21ffc445c16932abdcd69bb070cdcf87f9a179a32a`. They show the exact election/no-election APIs and wait-only tail. The older matching receipt adds initialization and non-mutating wait excerpts. They do not capture every `_get_thread_arrive_count`, `_make_sync_object`, or TCGEN empty-arrival implementation detail.

Before interpreting a GPU result, compiled code must establish131 initialization, three correctly weighted TMA arrival sites, one per-thread SF noinc-arrival site executed by128 threads, one common post-MMA empty completion, and no hidden extra full arrival/tail expectation. CuTe sibling-region dominance/branch typing and emitted instructions remain compilation questions. First exact smoke must retain the existing timeout and compare initialized payload/SF bytes, short-K/tail zero-fill, and persistent stage reuse. This review is source readiness for that bounded validation, not authorization for additional variants or a performance claim.

## Final R2 scope repair and compiled ordering receipt

The5d3 epoch failed during compile, before a kernel launch: `codegen/codegen-r1.log:2–9` reports `NameError: expected_bytes is not defined` at the call after the runtime warp branches. `codegen/codegen-r1/resources.json` has `complete=false`, `kernel_launched=false`, and no resource rows. The source/build/patch/manifest are preserved under `failed-r1/`; no failure is hidden by the repaired epoch.

Final source `53f3b78b…` moves `arrive_and_expect_tx` into each explicit warp0/warp1/else-warp2 branch and passes its byte expression directly. An independent AST extraction verifies that the three final byte expressions are identical to the expressions previously wrapped in `cutlass.Int32`. The enclosing warp<3 guard, own-transfer order, all128 SF arrivals, full/empty counts, and all other source remain unchanged. This eliminates the cross-branch `expected_bytes` binding; successful compilation establishes that this particular CuTe scope failure is repaired. Actual clone bytes equal `selected_core.py`.

|Final R2 item|SHA256|
|---|---|
|Candidate core / `selected_core.py`|`53f3b78bd602058d6b57e50a809241b35af97771cc3664ddbfc16487389ab176`|
|`source.patch`|`07e6dd9dff31217d140381bd5b867164ac72bbd45cecdc746b8aa21ac2086bfa`|
|Final `manifest.json`|`817c3df5649bca5491ae018dfe391dfc352069b2a19a3c097a530868841e2afd`|
|`ptx-ordering-proof.json`|`373807690e29d2edac212fd341d5cb210e5d19180ff37907d7d92c8b5c7a83c1`|
|`codegen/codegen-r2/producer-fc1-n16.ptx`|`e4d0c7f3f341a10c10ad5af8905c17c460746f9dfb3e427d21d8e83c1b87d322`|
|Matching cubin|`deb8c88ad87647da8ed1cd1e31e773e9c6c7043af9a0938dd7bd19ce2737efe4`|
|Matching SASS|`acce2ce8984b031f367bda79703679cc855769ae5c66d747087f6d0c6a592d8e`|
|Matching `resources.json`|`d7ec9f42fa2abcf5a6b6c4ffaeb5745f8d5753db48f801bc95d222e658add972`|

Independent inspection of the emitted PTX confirms the supplied ordering proof:

- `:75–79`: four full stages at offsets0/8/16/24 initialize with131. `:86–90`: four empty stages at32/40/48/56 initialize with1.
- `:125–126` restricts the producer branch to `tid.x<128`; all these threads reach the common empty wait `:216`. `:208,222` restrict TMA issuing to `tid.x<=95`.
- `:223–245`: whole warp0/1/2 branches elect once and announce32768/4096/8192 bytes at229/238/245. Their TMA transfer sites follow the announcements; split A/B transfers still sum to the announced bytes.
- `:300–315`: all128 producer threads reconverge, execute their eight SF cp.async sites, and execute the single unpredicated `cp.async.mbarrier.arrive.noinc` site315. There is no election around this arrival. The producer state advances once afterward `:316–320`.
- `:1077` waits the joint full; `:1083` retains `fence.proxy.async.shared::cta` before SF-to-TMEM copies. After all eight MMAs for the K512 stage, one elected TCGEN commit at1304 targets the common empty barrier `%r46+32`. The second commit at1319 targets the separate accumulator-full barrier `%r45+128`; it is not a duplicate operand release.
- `:328–397`: warp0 alone drains four empty stages at337/355/373/391, with wrap/phase progression and no added `expect_tx`. `:1352` joins288 threads, followed by the retained128-thread teardown barrier1359.

The compile-only resource receipt is complete and pins the final manifest: B200,288 threads, grid148, physicalN32/logicalN16, four operand stages, two accumulator stages,128 TMEM columns,197504 dynamic shared bytes,64 registers/thread, zero local bytes, one active block/SM. It explicitly reports `kernel_launched=false`. This closes the emitted-count/order question for this one compiled FC1 N16 specialization; it does not prove every gate-eligible format/geometry.

Independent SASS review corroborates the PTX: three elected TMA arrival sites at0xc70/0xcd0/0xd10; unpredicated SF `ARRIVES.LDGSTSBAR.64.ARVCNT` at0x1280 for the128-thread producer branch; four warp0-only empty waits at0x1370/0x1410/0x14b0/0x1560 without arrivals; common operand completion at0x3ba0 and separate accumulator completion at0x3c70. No material lowering mismatch was found.

The collected exact receipts were independently compared locally:

|File under `evidence/merged-operand-ring-aab/raw/logs/merged-operand-ring/`|SHA256|
|---|---|
|`exact-control.json`|`3718577831a451e5148d7f59baf0fb21fafd0ba7e1f4e1594f22a07efab72439`|
|`exact-candidate.json`|`1dcb8b960907e16e097da8dbda55ccb57bdb5720ab5da5a36403ca411abd585a`|

Both are complete, contain exactly seven rows, and pin final manifest817c3df5 plus the expected control7c0fe69f/candidate53f3b78b source hashes. **All seven complete row objects match**, including each case's ten input hashes, full initialized output-buffer hash, output-SF hash where present, original-SF guard result, and invalid-output-row result. The bounded cases are K64/K384 live17 and K1216 live33, each with quantized and per-token BF16 output, plus zero-live K64, all N16/M384. `probe_exact.py` uses `sm_count=2` to exercise persistent reuse and preserves sentinel padding. This is full-buffer digest equality against the retained control in these cases, not an independent mathematical oracle or coverage of every enabled format/geometry. No timing or broader correctness claim follows from it. The manifest's `gpu_executed=false` is a source-build snapshot, not a live status field for subsequent validation. This reviewer launched no GPU work.
