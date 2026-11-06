# Bounded five-WG overlap audit

No additional implementation candidate is justified by this source/history pass. Keep the existing FC1 first-x16, fixed epilogue144/decode96 allocation, and FC1 alpha-before-wait candidates separate and ahead of further polling or topology experiments. This audit used local source only: no production changes, remote calls, native compilation, GPU activity, new tactics or capture harness.

The four reviewed runtime files still have these exact bytes. This is a file-level source audit, not a newly admitted full runtime owner or a performance result.

| File, relative to the repository | SHA256 |
| --- | --- |
| `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py` | `2d53b2c3a983fea4abf9f11df857568c4910594b44f9fd9d6ef30eb978106feb` |
| `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/epilogue.py` | `604935b57f14a78a69b6f3a8dd160234b20550980cd6f678605e9e3a32a1131a` |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py` | `b473a1e03c2783255404300c15d477afe1c51eaafb36a215417081e014846e95` |
| `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_utils.py` | `3579088892bcf72027318e039270d5eba7337ab2a19e24291e2b18162ab88368` |

## One source difference, insufficient evidence to promote

The retained split MMA warp probes decoded-A readiness before accumulator acquisition and carries the next decoded-A probe between K iterations (`moe_w4a16_kernel.py:1745–1759,1788–1796`). The immutable NVFP4 Mega reference uses the analogous combined-AB pattern (`src/moe_nvfp4_swapab/mega_reference.py:1464–1477,1541–1549`). Current W4A16 Mega instead blocks directly on the accumulator, decoded A, then activation B (`shim/w4a16/kernel.py:1258–1263`), issues the MMA tile, releases A/B and advances (`1264–1277`).

A decoded-A-only carried probe would be source-compatible: the same consumer owns the same stage/index/phase until its release, so a successful readiness observation cannot be invalidated while accumulator acquisition runs. It would reset only work-local count, retain persistent index/phase across FC1/FC2, preserve the leader predicate, guard the first and next probes by K count, and leave B's blocking wait, MMA, releases and tail unchanged. It adds no payload tensor or stage, but does add a live status and probe/control instructions.

This is not the previously rejected *dual*-operand probe; I found no isolated current-Mega trial of this exact decoded-A-only difference. Nevertheless, it has no demonstrated useful scheduling interval here. The first probe can overlap an accumulator wait, but a failed probe must still be checked later. Between subsequent K iterations the obvious interval is mainly state/address/loop work; a try-wait does not initiate weight transfer or decode. Source parity alone does not establish a gain. The old raw-producer carried-acquire note in `../w4a16_next_overlap_audit_0d795/README.md` has the same limitation and is not a second proposed experiment.

Only fresh source-correlated evidence of repeated decoded-readiness polling with useful independent work would justify revisiting this. A later native gate would require actual probe separation and unchanged A/B/acc stage addresses, phase/release/commit counts, MMA count and resource limits, with no extra slow-path churn, locals or cloned role CFG. The present audit does not create that trial. Historical 512-thread PC samples cannot establish a bottleneck in the current five-WG kernel.

## The apparent larger windows are already covered or required

- **Decode/raw lifetime:** shared `_transform_tile:491–617` already probes raw and free decoded stages, carries the next raw probe from the final packed load, and preserves the current raw stage through collective TMEM stores/fence. FC2 first-x16 is already enabled at private `kernel.py:1227`; the queued FC1 extension addresses the distinct remaining prologue. Whole-fragment preload, next-fragment buffering and earlier raw release are repeats, not new directions.
- **FC2 metadata before its dependency:** private `epilogue.py:249–265` retains the vendor early accumulator wait when scheduler `peek_ready` is false, then prefetches routing metadata. The metadata comes from dispatch: `src/src/token_comm.py:1102–1135` stores `TokenSrcMetadata` before publishing input readiness. Vendor `epilogue_refactor.py:2040–2054,2376–2405` reads it to form peer destination pointers. Scheduler `custom_ext.py:401–422` peeks FC1 completion; false does not prove metadata availability. Unconditionally moving router prefetch above this wait can read unready metadata. Doing so safely would require another dependency protocol, not a free reorder. FC2 alpha is immutable and already loads before the wait.
- **FC1/FC2 overlap:** scheduler publication and weight/decode roles are separate from activation readiness (`kernel.py:1048–1101,1103–1147,1211–1230`). Only activation TMA waits for FC1 output flags before FC2 activation reads. There is no scheduler-wide FC1 completion wait to remove to unlock FC2 weight decode.
- **Epilogue release:** static FC2 already releases only after its final post-reorder TMEM scratch use and before independent output packing/STG (`epilogue.py:305–322`), including the existing empty/last-invalid branch (`294–299`). The analogous FC1 scratch-load release and empty FC1 bulk-drain removal already have separate preserved candidates. Releasing at the first raw LDTM would violate subsequent scratch ownership.
- **Capacity and hints:** private `kernel.py:98–116` uses two accumulator stages plus the maximum decoded ring fitting512 TMEM columns (N64:3, N128:2). `_fit_raw_stages:328–344` already fits preferred5 downward against actual shared storage. The five-WG allocation remains640×96=61440, with exactly two80-register decode WGs; setmaxnreg does not add another4096 registers. Packed-weight TMA evict-first (`823`) and activation evict-last (`889`) match retained split policies. No new stage/register/cache axis is proposed.

## Trial history checked first

The historical ledger below is `../flashinfer-w4a16/w4a16_optimization_experiments.md`, relative to this effort's root directory. These are prior split-kernel trials, not current-source timing:

| Historical lines | Mechanism and relevance |
| --- | --- |
| 1268–1309 | Complete packed preload and one-fragment lookahead rejected; no broad preload or extra fragment buffering. |
| 1348–1410 | Early scale release, final-load raw release and pre-TMEM-store raw release rejected; no repeat disguised as a different release position. |
| 1850–1872 | Epilogue accumulator pre-probe effectively neutral on EP8; no generic early-poll recommendation. |
| 1874–1925 | Retained two-accumulator policy already supplies the current extra decoded capacity; reducing a two-stage accumulator ring to one had a regression. |
| 1927–1948,1989–2020 | Activation producer carry and dual MMA operand probing rejected. The decoded-only source difference above is distinguished from those experiments. |
| 5290–5348 | Extra decode registers did not address the measured dependency; a later GEMM2 dual-input probe again regressed. No new register pool or activation poll suggested. |

Current effort ledger `w4a16_optimization_experiments.md:532–544` also records the missing-descriptor-prefetch trial and its restored-control regressions. Its absence is deliberate. The preserved `w4a16_next_overlap_audit_0d795` PDL analysis remains applicable to the unchanged reducer boundary: standard dependency synchronization permits reducer-independent setup but does not make BF16 combine reads safely overlap Mega communication cleanup. There is no new substantial reducer-independent compute phase.

The queue already contains the source-supported independent changes. This pass recommends no additional patch or cohort.
