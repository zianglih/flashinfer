# Rank 2 decoded-weight pipeline analysis

Source: `002ef1454cbacde09972ed5e2ec7dcfe37e55749` (capture source-tree SHA256 `f725918d2e71864c45fbbbc795aecd7086e4db051c71b9e488da02d52142a8b3`). Native trace: `artifacts/uniform256/rank2.trace.json.gz`, compressed SHA256 `9625cbc446ce79ab78bc25bc2ad756ea6d870fad6bb0d0d2609e79b4237a28b1`. This analysis changes no repository code and launches no GPU work.

Reproduce from project root:

```sh
python3 optimization/trace-analysis.py > optimization/trace-analysis.log
```

Outputs: `trace-analysis.json` (aggregate statistics), `trace-analysis.csv` (488 matched K iterations), and `trace-analysis-gaps.csv` (per-warp inter-iteration gaps). The script joins parent work records by ordinal, verifies identical phase/expert sequence across all 16 transform warps and the MMA leader, and verifies every child K payload. Work payload lacks output tile index, so phase/expert alone is insufficient for joining.

## Scope and principal finding

EP4, H6144/I2048/E256/top8, 256 tokens/rank, exactly uniform 32 routed tokens/expert. Native launch is 148 CTAs; recorder selects cluster 0, containing two 640-thread CTAs and 40 warps. Rank2 records 33 output work tiles: 14 FC1 tiles ×24 K256 iterations and 19 FC2 tiles ×8, totaling488. The recorded span is598.336µs. These instrumented durations are neither uninstrumented latency nor hardware utilization; nested scopes and concurrent warp sums cannot be added as GPU occupancy.

The MMA issue warp is overwhelmingly gated by the collective decoded-weight ready condition. In486/488 iterations its weight wait ends within0–64ns of the latest of16 transform-store/commit endpoints (383 at32ns,87 at0ns,16 at64ns). The other2 are initially prefetched K1/K2 delayed behind K0 activation readiness. The trace therefore establishes a real dependency on the **last contributing producer**, but does not establish that the entire weight-wait interval is idle tensor-core time.

| Instrumented range | FC1 aggregate / median per K | FC2 aggregate / median per K |
|---|---:|---:|
| MMA weight-ready wait |234.944µs /672ns|132.832µs /768ns|
| MMA activation-ready wait |47.424µs /64ns|9.120µs /64ns|
| MMA asynchronous issue |42.048µs /128ns|17.344µs /128ns|
| Transform explicit slot wait, **mean over16 warps** |49.356µs /66ns|10.780µs /70ns|
| Transform raw-ready wait, mean over16 warps |18.000µs /46ns|7.326µs /48ns|
| Transform load/decode, mean over16 warps |112.900µs /324ns|59.038µs /378ns|
| Transform store/fence/commit, mean over16 warps |80.928µs /240ns|48.374µs /298ns|

MMA accumulator-slot wait totals only2.240µs over33 work tiles, median64ns. Extra decoded depth cannot be obtained for free: current N64 uses128 columns for2 accumulators and384 for3 decoded K256 tiles, exhausting512 TMEM columns. Changing accumulator allocation or K geometry would be a separate, larger experiment; earlier failures are documented in `ledger-audit.md`.

## Startup backpressure and actual wait placement

The standout explicit producer wait is **first FC1 tile K3**: mean23.632µs across16 warps. K0's MMA activation wait is25.504µs. During that wait the producer fills K0/K1/K2, then reaches K3, which aliases K0's TMEM slot. This is expected backpressure caused by input arrival, not evidence that TMEM recycling is intrinsically23µs. Every other K iteration has mean explicit slot wait below1µs; overall median68ns and p90 90ns.

There is an important naming blind spot. `_transform_tile` invokes `producer_try_acquire` before entering its first K and again after each store/commit, **outside** `transform_wait_tmem_slot_free`. That API is not guaranteed nonblocking. The pipeline delegates through `MbarrierArray.try_wait` to `cute.arch.mbarrier_try_wait`; NVIDIA distinguishes potentially suspending `mbarrier.try_wait` from nonblocking `mbarrier.test_wait` in the [PTX ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait).

The capture's exact `evidence/uniform2.sass` confirms `SYNCS.PHASECHK.TRANS64.TRYWAIT` at0x12330 and0x13df0, after store/commit's pop and before the next raw-ready push. This closes the compiler-placement question even though the locally archived runtime source is older than the pinned4.8 environment.

Across455 within-tile transitions per warp, these unmarked gaps total68.9–81.0µs per warp, median128ns/p90 224ns/max1.248µs across all16 warps. They include state updates, loop control, instrumentation, and potential suspension; **the trace does not isolate how much of each gap is actual barrier waiting**. There are103 gaps >=500ns; median gap-end minus prior slot owner's MMA-issue end is160ns, consistent with buffer-release backpressure in this subset. Do not characterize every gap as a stall.

Consequently, moving only the explicit `producer_acquire` after decode while retaining the earlier `producer_try_acquire` would leave the early suspension hazard intact. Full predecode must defer/remove both early try calls as well as move the actual acquire to immediately before TMEM stores. Raw SMEM cannot be released before all weight/scale loads have completed; decoded-ready publication remains after the TMEM fence.

## Cross-warp skew

All producers work on disjoint portions of the same K tile. One producer's explicit wait therefore need not correspond to the consumer's current K. Producers can partially populate the next two stages while another producer still completes the current stage.

For the same K, earliest-to-latest store/commit endpoint spread is median1.824µs, p90 2.528µs. Decode-start spread is median1.824µs, p90 2.400µs. CTA0 warp16 is among the latest endpoint ties in292/488 iterations; its median lag from the first producer endpoint is1.792µs. This is a candidate signal for producer balance or scheduling/issue overhead, **not proof of an arithmetic imbalance**: partitions have equal element counts and this heavily instrumented trace can change scheduling and register allocation.

Example: FC2 work tile14, K4, relative to first recorded range:

- Fast contributors begin decode around290.976–291.072µs and finish store/commit around291.680–291.840µs.
- CTA0 warp16 begins decode293.216µs, stores/commits293.568–293.920µs.
- MMA waits for that K from293.184–293.920µs, then issues294.048–294.144µs.

Most explicit free-slot waits in that example are32–64ns; the consumer dependency is the last decoded part, not a simultaneously blocked same-K stage. Fast producers can already be handling later K indices. This is why a visual impression of producer and consumer “both waiting” needs matched K identities.

## Minimal candidates grounded in this trace

1. **Complete K256 decode before TMEM acquisition, and defer the potentially blocking probes.** This overlaps independent load/decode with prior MMA use of the destination slot. The register tensor already holds the whole decoded tile in the existing code, but altered lifetime across a wait may add moves or spills. Inspect uninstrumented SASS and resource usage, and measure the full forward with the prior HashInfer cold-L2 CUDA-graph CUPTI methodology. Prior K128 and partial predecode outcomes are historical context, not this experiment.
2. **TMEM store repetition8→16 in the owned MegaMoE copy atom.** Exact current SASS emits eight `STTM.x8` instructions per K, with address staging and local reloads. Store/fence/commit averages265ns per producer iteration (FC2 mean318ns), materially comparable with mean352ns load/decode. If supported by the copy layout, repetition16 could replace eight store instructions with four. It might instead create register moves/spills; require exact-address/numerical validation and uninstrumented codegen/timing. This changes no buffer ownership or completion rings.
3. **Lower-priority: aggregate decoded-full barrier arrival per warp.** Current producer group counts512 threads, and SASS uses all-lane `SYNCS.ARRIVE` after the TMEM fence. Counting16 participating warps and electing one arrival per warp could reduce barrier traffic. This requires a careful warp-wide completion/ordering proof and matching arrival counts, so it is more invasive than store-width/predecode and should be tested only if simpler changes fail. Preserve independent weight/activation completion rings; do not resurrect the historically rejected coupled-ring design.

The uninstrumented performance control must be freshly collected. The older323.744µs hot native tuner score is neither a cold-CUPTI control nor an elapsed hardware trace baseline. Fine markers add eight endpoints per transform warp per K (62,464 transform subrange endpoints in this cluster); their scheduling and register effects are a reason to use traces for hypotheses and separately benchmark the optimized production launch.
