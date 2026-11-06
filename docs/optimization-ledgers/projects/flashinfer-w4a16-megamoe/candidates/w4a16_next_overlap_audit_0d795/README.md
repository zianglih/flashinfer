# Next overlap audit at source 0d795

**No additional implementation or compile cohort is recommended now.** Prioritize the queued input-on-epilogue and FC2 first-32-value predecode candidates. One small source-parity difference remains worth recording, but its useful scheduling window has not been established. This audit made no production edits, remote-host calls, native compilation or GPU operations.

All source locations below are relative to the `flashinfer/` repository. Full current source identity is `0d795ec767c1a588e4982d6972ef12dcf5b10683f55141310adab96efb6e1e86`; kernel SHA is `2b85c9e3f727fddf60bc5327ecc63bdb38785367f17a398cdebf6bc32df8a17d`. The source/helper hashes were checked against the exact owner declaration. `evidence.json` freezes reviewed source/ledger hashes and selected excerpts. The historical ledgers were read before proposing a direction.

## One conditional source note: carry the raw-producer readiness token

The retained split weight producer in `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1491–1529` probes the current raw stage with `producer_try_acquire`, passes that Boolean to `producer_acquire`, then probes the next stage after commit/advance. Current Mega `_weight_task`, `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/w4a16/kernel.py:815–839`, instead calls blocking `producer_acquire(state)` directly. The activation producer also blocks directly, matching the retained split activation path.

A possible future change would copy exactly the weight producer pattern into `_weight_task`, with no new stage, register budget, payload tensor, public knob, geometry or cache policy. It would change at most one logical readiness token; physical allocation must be checked separately. Both FC phases share this producer helper. Its lifetime proof is straightforward:

- Reset only `count`, as today. For a nonempty K loop, probe the exact current `index/phase`; never assume the first stage is empty at a work-tile boundary.
- A true token applies only to this producer's current raw stage. No other producer overwrites that stage, and the token is consumed before this producer changes the transaction or advances its state. A false token retains the original blocking acquire.
- Preserve packed A and E4M3 SF in the same transaction barrier, identical byte total, stage index and multicast mask. Issue both copies, commit and advance exactly once; probe again only if another K iteration exists.
- Preserve the raw consumer releases after decoded-TMEM store/fence, persistent index/phase across FC1/FC2 tiles, and `producer_tail` only after the sentinel. Zero-K/sentinel behavior gains no probe.

This is distinct from input-role placement and first-fragment predecode: it changes warp 5's **free-raw-slot** polling; queued predecode changes transform warps' RMEM work before the **free-decoded-slot** wait. It moves no packed/SF payload or BF16 result across a wait.

There is nevertheless little independent work between the proposed end-of-K probe and next acquisition: primarily loop control and source/destination address preparation. The source does not establish a latency-hiding interval. A future source-correlated control/candidate codegen comparison would need to show actual useful separation or a smaller polling/control path, without extra slow-path queries, spills, barrier arrivals or MMA duplication, before any timing cohort is justified. No such new evidence exists now, so this remains a note, not a prepared patch.

The exact kernel source already appeared in the earlier e2d88 EP1 NCU capture. Its two actions sampled the weight producer's free-raw-stage branch at 5172/5216 samples in one FC site and 2454/2452 in the other. These are source-specific observations from a different epilogue and EP1 workload, not a latency fraction, root-cause proof, or prediction for source 0d/EP8. The same historical split experiment on the **activation** producer was rejected: ledger lines 1928–1948 reports EP8 geomean 0.9934x and simulated TP8 0.9918x. Do not extend this note to activation polling or generic eager prefetch.

## Stage topology and cache changes already accounted for

| Direction | Current source/history | Decision |
|---|---|---|
| Full register pool | Mega role budget is 128×(176+80+128+128)=65536; two decode groups are fixed. | No unused-pool rebalance remains. |
| Extra decoded stage | `_compute_stages_and_tmem_cols:95–115` uses 512 TMEM columns: N64 is 2×64 accumulator +3×128 decoded; N128 is 2×128 accumulator +2×128 decoded. | No extra decoded slot fits without changing accumulator buffering. No new evidence justifies that trade. |
| Raw/SF rings | `_fit_raw_stages:329–344` fits preferred depth 5 down to 2 using actual SMEM; `_weight_task:817–834` combines packed/SF transactions. | The old independent six-stage SF ring is superseded by the retained merged-barrier change (old ledger lines 1001–1034). Do not resurrect it from an earlier “retained” label. |
| Metadata stages | Mega defaults to 3 (`kernel.py:175`), matching retained static split depth. | No broader stage/topology knobs; extra depth needs a demonstrated metadata-boundary gap. |
| Data-cache policies | `_weight_task:824` already uses EVICT_FIRST; `_activation_task:890` uses EVICT_LAST; SF stays default. | Retained PR4048 policies already match. Prior SF FIRST/LAST, weight LAST and FC1-store retention variants were rejected. |
| Descriptor prefetch | Absent now, but tested in Mega. Current ledger line 543 records restored-control regressions 19.40/4.35/2.54% at T1/8/64 and 0.69% improvement at 4096, with T1 control drift. | Archived; do not present it as an untried missing optimization. |
| Generic lookahead/early raw release | Persistent states already span work tiles. Prior full-decode hoist, next-fragment load lookahead, explicit fragment TMEM stores and raw release before TMEM stores were rejected. | The queued first-32-value prologue is the bounded distinct direction; do not broaden it. |

Historical ratios are from their original B200 or earlier B300 controls, not fresh current-source measurements. The acquisition audit and both ledgers retain their original limitations.

## PDL is a different boundary, with little transferable independent work

Current mixed-helper construction pins `enable_pdl=False` (`kernel.py:261`); the actual Mega launch at 755–761 omits `use_pdl`. The public frontend calls the vendor BF16 reducer only after the fused call (`frontend.py:608–628`); `TopkReduce.__call__:301–305` also has no PDL launch opt-in, and `_reduce_bf16:367–424` has no dependency wait. Merely changing the mixed helper flag cannot enable this two-kernel boundary.

NVIDIA's [Programmatic Dependent Launch guide](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html#api-description) distinguishes permission to launch early from data availability. All primary blocks must trigger (or exit); the secondary must synchronize its dependency or otherwise prove the data is available. The standard dependency synchronization waits for primary completion and global-memory flush. Concurrent execution is opportunistic, not guaranteed. Its [graph section](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/programmatic-dependent-launch.html#use-in-cuda-graphs) also requires the appropriate programmatic edge semantics.

Consequently, standard PDL would permit only reducer-independent setup before the wait: index/descriptor arithmetic, register initialization and score loads (`topk_reduce.py:381–418`). BF16 combine loads and FMA reduction at 424 onward must stay after the dependency wait. PR4048 can do substantial next-GEMM static-weight TMA/decode before dependent activations are ready (`moe_w4a16_kernel.py:1395–1396,1440–1530`); this reducer has no corresponding independent GEMM/decode phase. Standard PDL does **not** make the actual reduction overlap Mega cleanup.

The source also forbids treating local FC2 epilogue completion as all combine data ready. In epi-return mode, epilogue warps finish stores, system-fence, and free TMEM before the common tail (`kernel.py:1375–1380`). In dispatch-return mode, decode WG0 first pushes BF16 outputs, drains its bulk stores and system-fences (`token_comm.py:1380–1424,1480`). All 512 threads then rendezvous (`token_comm.py:1791–1795`). The first tail NVLink barrier drains all ranks, shared counter zeros are published through the second barrier, and local counters are cleared last (`token_comm.py:1830–1869`). Those counter writes are required for the next call; they are distinct from combine data, but there is no reducer-visible early-combine-ready protocol that substitutes for dependency synchronization.

A custom readiness protocol that allowed combine reads before primary completion would be a new synchronization/lifetime design, not direct reuse of split PDL. It would need to preserve both return modes, empty ranks, cross-rank visibility, TMEM/pull-buffer completion, next-call workspace reuse, stream capture and downstream dependencies. No patch is proposed. Full-pool persistent CTAs also leave no established co-resident reducer execution window; resource availability and any launch-latency benefit would require new evidence. The source-proven conservative boundary remains completion of the fused kernel, including cleanup.
