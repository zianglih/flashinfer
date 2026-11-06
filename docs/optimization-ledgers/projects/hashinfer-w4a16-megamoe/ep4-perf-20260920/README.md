# EP4 MegaMoE performance iteration

## Current status — September 19

- **Retained and pushed:** eight-tactic group-size product at `ec42ba07`, followed by README-only `66b6df6`. Canonical PR8 checkout is clean. FlashInfer `799a7f2` remains unchanged.
- **Published evidence:** complete native main-to-PR EP4 and EP8 tables are in PR8. Decode 4–512 geometric speedups are 1.0795× / 1.0931×. The body explicitly preserves remaining prefill regressions; see `comparisons/whole-pr-final-ep{4,8}.json` and `pr8-after-group-extension-final-tables.json`.
- **Qualification:** eight focused numerical cases cover both EP sizes and routing-weight placements, all eight tactics, O2/O3 and eager/graph: 256 combinations with zero bit mismatches. Full-matrix and sanitizer reruns remain deferred.
- **Completed without retention:** scheduler S3, M128/C1, static epilogue scheduling and initial-idle pull skipping. Detailed evidence and failed attempts below are historical, not current pending work.
- **Current experiments:** immediate dispatch publication `a96c431` completed both EP sizes and remains unpromoted; coalesced paired-slab combine `4484279` also completed EP4 without retention. Neither is promoted; both devboxes are idle after verified process/GPU closure. Both use each node's matched `ec42ba07` control, ordinary ABI preparation and the deferred-CUPTI lifecycle.

Primary source: HashInfer PR8, `7e6e977f4788f91eaf5988fd4ffea93fc4f1eed5` (kernel/host same as `58e9112`). Public FlashInfer port remains unchanged until the next agreed sync.

## Decision method

Use real EP4 and EP8 on separate exclusive B300 devboxes, CUDA 13.2. Global token counts: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 4096, 8192, 16384. H7168/I2048/E256/top-k8. Precomputed routing, default FC2 routing-weight placement, deterministic FP32 combine. Native HashInfer benchmark; three warmups, 100 cold-L2 CUDA graph CUPTI samples, median per-sample rank maximum. Fresh knob cache per sweep; compiled caches may be reused with source binding. Compare HashInfer before/after on the same node, not previous FlashInfer latencies or cross-node ratios.

Prioritize decode 4–512; display 1/2 but exclude them from retention. Check prefill separately and confirm EP8 before promotion. Use benchmark first, targeted strict bit-exact numerics for promising changes. No Split-vs-Mega numerical gate; no sanitizer during iteration. Preserve all samples and unsuccessful experiments.

## Hypotheses

- Fixed global tokens give EP4 twice the owned experts and source tokens per rank. Communication savings alone do not isolate the cause of its smaller gain.
- Existing `group_hint` counts FC1 work tiles. With 64 local experts, EP4 can cross the current 512-tile FC1 group budget where EP8 ends within it. Larger groups may reduce phase transitions but can delay FC2 and worsen activation locality. Test existing group1024 with the same four AUTO tactics before adding any tuning dimension.
- Dispatch warps may waste work traversing exhausted expert ranges; EP4 doubles the local expert count. Inspect a warp-uniform exhausted-work bound with unchanged transfer and flag lifetimes.
- Scheduler/activation/raw/decode stage depth must be evaluated against available shared memory and TMEM. Prior EP8 failures are evidence to prioritize, not proof of an EP4 result. Keep one CTA per SM, five warp groups, exactly two dequantization warp groups.

## Experiments

1. `group1024/hashinfer`, local commit `62c3ba1c5d0a20d69ab1ed96cb0379f31269defb`: one literal in owned autotune catalog, 512 → 1024. Manual/default profile unchanged. Pending benchmark.
2. Pull exhaustion bound: source audit in progress; no shared upstream-drop modification will be promoted without resolving ownership.

Source worktrees have their common Git directory inside this project. Canonical PR8 checkout remains clean until a candidate passes retention and targeted validation.

## Baseline and trial progress

- Retained hu6 (`fi-mega-sync-0919`, c2/ziangli) provides lane1. Fresh hu9 (`hashinfer-ep4-perf-0920`, c2/infra) provides lane2. The previous hu115 box no longer exists. Both use explicit `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, B300 and driver590.48.01. The first quota-limited pending ziangli request was canceled before the successful infra request; existing boxes were preserved.
- Lane1 Hash7e6e977 baseline EP4 is complete: 13 rows/1300 samples, all finite repeatable outputs and actual-fixture T4 independent strict oracle pass. Root `compare.read_arm` independently parsed the raw logs. All decode selects N64/epilogue; all prefill selects N128/dispatch.
- Group1024 `62c3ba1` runs after that baseline on lane1. Scheduler3 `aec91ab6` is prepared for lane2's separate same-node EP4 control. Both retain four candidates.
- M128/C1 extension `9bc743e2` is queued: three supported geometry/cluster pairs × return mode = six candidates; the original four are unchanged. Potential final expansion will require removing test cardinality assumptions while retaining deterministic-mode assertions.
- Pull-bound prototype `14af48e` changes the copied shared transport only for an isolated measurement. A separate owned wrapper is prepared to avoid that ownership issue if the direction merits retention; do not conflate their performance.

No candidate has been promoted, no public FlashInfer file changed, and sanitizer remains deferred. `compare.py` validates raw samples, fixtures, per-rank output hashes and same-node provenance before generating each table. Independent strict-reference coverage is reported separately from paired output equality.

## S3 comparison and CUPTI lifecycle diagnosis

S3 EP4 completed on hu9 with the original per-session CUPTI lifecycle, matching that node's baseline. Root independently reconstructed every row from 1300 samples/arm and verified all 52 paired rank-output hashes. Decode4–512 geometric speedup is 1.00123045; individual rows are mixed. Matched hot N64/epilogue scores show T8 140.2→139.9us and T16 193.7→193.7us, so the larger cold-row differences are not clear evidence of a scheduler gain. N128/dispatch hot prefill changes are also small/mixed. S3 is held, not promoted; no additional numerical matrix or EP8 performance run is justified by this flat EP4 result yet. See `comparisons/sched3-ep4.{md,json}`.

The hu6 group1024 full run failed twice in host `cupti.finalize()`, after successful kernel/autotune work. Isolated T4 with the same source passed all four tactics, 100 samples, repeat bits and strict independent reference. Original partial runs remain excluded. A benchmark-only deferred-finalize shim retains callback lifetimes and executes a single original finalize after the full workload/process-group drain. Native activity enable/flush/disable, sample computation and timed kernel remain unchanged. Fresh baseline and candidate must use matching lifecycle; `compare.py` rejects mixed protocols. No package timer or kernel source was modified for this workaround.

Installed CuTe4.7.1 explicitly disables disk caching in `cute.compile`, despite recognizing the configured cache directory. Earlier cache-path existence is not proof of a CuTe persistent hit. Timings comprise less than10seconds of a415–461second baseline, so reducing100 samples is not worthwhile. A separate benchmark-only unused-staging-ABI pruning investigation is held until codegen/resource/output parity can be checked. Normal API warmup stays unchanged.

## M128/C1 catalog result

The six-candidate EP4 sweep at `9bc743e2` completed on hu9 against its baseline at `7e6e977`, using the original CUPTI lifecycle: all 13 rows and 1300 samples, 52 exact paired rank-output hashes, stable source/helpers and clean CPU/GPU closure. No M128 tactic was selected. Every winner matches the baseline M256 geometry and return mode. The cold decode ratio of 1.00566736 is therefore unchanged-path variation, not demonstrated M128 benefit. Do not retain this expansion or spend EP8/all-tactic qualification on it.

Within-sweep hot autotune scores independently disfavor M128: its best tactic is 1.93% slower at T4, 11.67% at T8, 5.83–11.27% at T16–512 and 16.12–24.59% at prefill. T1/T2 also do not select it and are outside retention. Complete scores are in `comparisons/m128c1-autotune-scores.json`; the cold table and raw sample derivation are in `comparisons/m128c1-ep4.{md,json}`. This is a no-selection decision for the measured workload, not proof that M128 can never help another workload.

## Existing static scheduler tactic trial

Prepared `static-epi/hashinfer` at `f9e8e591`: only the owned candidate factory changes. The original four deterministic and six IKR-permitted atomic-counter dictionaries remain unchanged; two static-scheduler epilogue-return dictionaries extend those catalogs to six/eight. Dispatch-return scheduling is unchanged. Native compilation, performance and numerics remain pending.

The upstream BF16/MXFP8 catalog uses static load balancing (`shim/autotune.py:183–198`). Our existing compile-time static path strides by persistent clusters and avoids the atomic plus DSMEM broadcast in `fc1_fc2_fuse_sched.py:550–658`. EP4 has more expert/tile work per rank, so static assignment may be better amortized; imbalance and delayed readiness may still erase that advantage. No new public knob or pipeline mechanism is introduced.

Independent source audit passed: all six/eight candidates are accepted by the current tuner and actual frontend dataclass for EP4/EP8, remain unique, and preserve the atomic catalog. Static storage/initialization are already handled by the kernel; no pipeline changes are needed. Evidence: `static-epi/SOURCE_AUDIT.json`.

## G1024 result and group-size product

Matched deferred-CUPTI EP4 sweeps on hu6 completed at baseline `7e6e977` and G1024 `62c3ba1`. Both have 13 rows/1300 raw samples, exit zero, stable source/helpers and clean CPU/GPU closure. All 52 paired rank-output hashes match; the baseline additionally passed the actual H7168 T4 independent reference on all ranks. The candidate did not repeat that oracle in its full sweep (separate T4 diagnostics did). Raw-derived table: `comparisons/group1024-ep4.{md,json}`.

Cold decode geometric speedup is 1.03235715, with individual T4/T8 variations that cannot be credited to phase grouping: their exact workload groups are unchanged. Hot autotune scores are flat for T1–8, improve T16 from 190.7 to 183.6us, and improve T32–512 by only about 0.2–0.6%. Prefill hot scores improve 4096 from 800.0 to 778.6us and 8192 from 1352.3 to 1334.5us, but regress 16384 from 2472.3 to 2548.0us. Cold prefill improves 5.34%, 1.59% and 0.18%, respectively. Keep hot tuning and cold timing distinct; no claim that G1024 is universally faster. Complete hot score summary: `comparisons/group1024-hot-scores.json`.

Prepared `group-tactics/hashinfer` at `ec42ba07e2ebc164d1ba2796152f54e0ac821935`: existing geometry × return-mode product now also crosses group sizes 512/1024. Eight deterministic / twelve IKR-permitted candidates; original four remain the prefix, and all original dictionaries are preserved. Existing numerical and sanitizer scans now require a nonempty deterministic catalog instead of hardcoding four; the cache test checks IKR partition semantics rather than cardinality. Scoped pre-commit and CPU catalog checks passed. No kernel source or arithmetic changed. Fresh same-node EP8 baseline and full eight-tactic EP8/EP4 evaluation are next, with focused strict qualification if the extension is retained.

## Immediate dispatch publication candidate

Prepared lower-priority `dispatch-publish/hashinfer` at `57d157ec5873969fb778038c7ca9f04f256f6236`: retain the original four and add two dispatch-return entries with `epi_flag_batch=(1,1)`. This mirrors BF16/MXFP8's existing candidate policy. It uses the current compile-time flag tracker, release scopes and atomics; no new barrier or core change. The tracker normally carries final-expert publications across later tiles, so immediate publication might expose completed FC2 returns sooner on EP4. Six deterministic / ten IKR-permitted candidates; CPU catalog and scoped pre-commit checks pass. Native compilation and performance remain untested. This is separate from dispatch `flag_batch` experiments.

## Eight-tactic EP8 result

The full product `ec42ba07` passed its paired EP8 sweep against `7e6e977` on hu6 with the same deferred CUPTI lifecycle: 13 rows/1300 samples and 104 exact rank-output matches. The baseline has the independent T4 reference check on all eight ranks; candidate strict qualification is still pending. Decode 4–512 geometric speedup is 0.99572137. The largest dip is T4 (0.9624×), where the unchanged original G512 tactic is selected. Other decode rows are within roughly 1%; EP8's small-token phase grouping is unchanged for either hint. Prefill speedups at 4096/8192/16384 are 1.0276× / 1.0043× / 0.9951×, with G1024 selected in all three. These are acceptable EP8 guard results if the combined catalog establishes useful EP4 gains; they do not alone justify promotion. See `comparisons/group-tactics-ep8.{md,json}`. The matching EP4 product sweep is running next.

## Eight-tactic EP4 result and retention decision

The combined catalog's EP4 sweep is complete on hu6: all 13 rows/1300 samples, 52 exact paired rank-output hashes, stable source/helpers and clean CPU/GPU closure. `comparisons/group-tactics-ep4.{md,json}` independently reconstructs medians and checks matching fixtures, host/boot, native timer and deferred CUPTI lifecycle. Decode geometric speedup is 1.00625017. Individual useful gains are T16 1.0465×, T32 1.0356×, T128 1.0150×, T256 1.0220× and T512 1.0115×. Prefill is 1.0545× / 1.0271× / 0.9990× at 4K/8K/16K. T4 and T8 regress in this serial sweep. T4 selects the unchanged G512 tactic; T8 selects G1024, but the two hints produce the same groups there and have tied hot scores within the eight-tactic sweep. This supports run variation as an explanation for T8, without proving identical generated code for different compile-time constants. Do not claim that the larger fixed-group sweep's 3.2% decode aggregate carried through to the expanded catalog.

Provisionally retain the group-size product: it changes an existing compile-time scheduling choice, helps EP4 and 4K on EP8, preserves all original tactics, and requires no kernel implementation change. Promotion waits for native focused EP4/EP8 all-eight-tactic bit-exact qualification at both O2/O3 and eager/graph, with both routing-weight placements. No sanitizer during this iteration. Canonical PR8 and public FlashInfer are still unchanged at this decision point. The next separate candidates are static scheduling for epilogue return and immediate publication for dispatch return, each based on the eight-tactic catalog rather than conflating the two changes.

The local comparator also recognizes the proposed benchmark-only restricted staging-ABI preparation and rejects mixed protocols. That helper is not in any reported timing or numerical run and will not be deployed before code-generation/resource/output parity is established. Actual timing still uses 100 samples; compilation dominates wall time.

## Cache and specialization audit

`knobs="auto"` sets `_autotune_pending` and runs the current candidate factory on the first forward even when a cache file exists. Normal `knobs=None` uses the existing cached winner/default behavior. Old G512 winners remain valid, so no cache format/key or shared shim edit is needed. Integrators should run AUTO once outside graph capture to refresh their offline tuning cache after this catalog upgrade. The benchmark uses a fresh file per arm; there is no stale winner reuse.

`GROUP_HINT_SOURCE_AUDIT.md` traces the only direct device use to the scheduler threshold. Equal runtime groups do not prove equal generated code for G512/G1024; the retention rationale uses observed within-sweep hot scores and the full cold tables, not a binary-identity claim.

## T8 retention follow-up

Before promotion, investigate the repeated cold EP4 T8 difference:7e control144.130us, fixedG1024 152.385us, eight-tactic catalog151.073us. The new catalog's same-sweep hotG512/G1024 scores both round to136.5us, and both hints produce the same high-level phase groups. This is insufficient to prove equal machine code or dismiss two same-direction cold differences. Hu9 will therefore run a fresh ordinary-ABI/deferred-CUPTI7e four-tactic control before its already planned ec42 eight-tactic control, then pause for root analysis before static. This adds one control sweep and independently repeats the complete comparison on a second node; never compare raw latencies across nodes.

An untimed H7168/T8/EP4 N64-epilogue G512/G1024 binary/output diagnostic is prepared for hu6 after native qualification and staging-ABI parity if hu9 remains busy. It retains production O3 options, enabling only PTX/CUBIN preservation, and should inspect all raw SASS differences, resources and local spills before applying narrow threshold-immediate normalization. It is not a new timing criterion.

The unchanged native CUPTI loop locally flushes L2, synchronizes, launches one graph, and synchronizes per sample; it does not add a cross-rank launch barrier inside every measured iteration. Collective kernel durations can therefore include waiting for a later peer launch. This source fact is a possible source of small-shape variation, not a causal explanation of this particular T8 result. Keep the established measurement protocol and all100 samples.

## Focused group8 numerical qualification complete

Exact ec42 source passed native EP4 and EP8: T128/random and T1/skewed, each with both FC1/FC2 routing-weight placements, all8 deterministic tactics, O2/O3 and eager/graph. Total8cases,256combinations,768 reference checks and3968 pair comparisons;1,876,819,968 finite BF16 bit comparisons, zero mismatches/nonfinite values. Eleven knob-cache tests passed. Root independently verified every report, rank set/element sum, all104 source files, helper hashes, collected members and process/GPU closure; receipts are `group-tactics/ep{4,8}-evidence/root-audit.json`. Durations889.2s/1010.9s. This is focused qualification, not the full120-case matrix or sanitizer. Promotion still waits for the matched T8 performance follow-up.


## Preparation parity and profiling closeout

Benchmark-only staging ABI preparation was checked at EP4/T256 N64-epi and T4096 N128-dispatch. Across eight rank/case pairs, selected native CUBIN binaries, fixtures, repeated eager/graph output bytes and all resource attributes match exactly. Ordinary preparation made eight compile calls/rank across the two cases; restricted preparation made two. One raw PTX file differs only in typed virtual-register naming, while its CUBIN is byte-identical. The initial strict PTX comparator failure remains preserved rather than rewritten. Root independently checked all284 collected artifact hashes and selected binaries (`cache-audit/ep4-parity-evidence/root-audit.json`). This permits a benchmark-only preparation shortcut for future matched experiments; no API or accuracy-suite change. The active hu9 before/after and follow-up static trial retain ordinary preparation so their controls remain comparable.

Accepted Nsys T256/T4096 traces contain the expected five fused launches per rank. Full NCU T256 reports import successfully, and all160 replay outputs are finite and baseline-bit-exact. The profiler teardown hung after writing its reports; owned profiler processes were terminated, launcher exit1 and forced teardown remain explicit. Aggregate counters include impossible occupancy/throughput percentages and cannot support production utilization claims. Source-correlated samples identify scheduler-publication waits, initial transport publication and tail handoffs; they motivate the existing static-scheduler experiment but do not justify deleting barriers. No spill problem was found. Detailed limitations and exact evidence: `profiling/INTERPRETATION.md`.


## T8 generated-code diagnostic

An untimed native ec42 EP4/T8/H7168/I2048 capture compared fixed N64-epi G512/G1024 under production O3, with normal preparation and only PTX/CUBIN preservation enabled. Both have5176 SASS instructions, identical register operands/order/branch targets, REG96/STACK0/LOCAL0, and identical role redistribution. Exactly four instruction immediates differ: two group-threshold additions and the corresponding two signed-overflow bounds. No local-memory load/store instructions occur. All four ranks match fixtures and repeated eager/graph output bits. Raw PTX/CUBIN differ as expected; this is not binary identity or a timing result. Root checked all162 collected hashes and derived summaries (`cache-audit/ep4-group-t8-evidence/root-audit.json`). This removes instruction-count/allocation/spill differences as an explanation of the earlier cold T8 result; it does not prove a latency conclusion. The independent full hu9 benchmark pair remains decisive alongside the original hu6 evidence.


## Group-size product retained and pushed

Fresh hu9 ordinary/deferred sweeps at7e6→ec42 independently reproduce useful changed-path gains: T16 1.0552×, T32 1.0325×, T512 1.0087×,4K1.0486×,8K1.0219×. T16/T32 and4K/8K agree in direction and approximate size with hu6. T8 instead becomes1.0908× with the unchangedG512 winner; it is run variation, not an earned group-size speedup. T4's group boundaries are also unchanged. Overall decode GM is1.0294× onhu9 versus1.0063× onhu6; do not present either as a universal causal gain or pool node timings. T128/T256/16K choose unchangedG512 on this repeat. Full table/raw verification: `comparisons/group-tactics-ep4-repeat.{md,json}`.

Retain ec42's eight-candidate product based on repeatable T16/T32/4K/8K EP4 gains, EP8's4K gain with otherwise roughly flat guard, preservation of every old tactic, strict focused numerics and the T8 codegen audit. Canonical branch fast-forwarded toec42 and README-only66b6df6 records the catalog adaptation/cache refresh without hardcoded test cardinalities. Scoped pre-commit passed. Public FlashInfer799 remains unchanged. Static-epi extension cdf7aff is the next separate hu9 trial against this fresh ec42 control. Same-source full-PR external-script controls/final arms onhu6 will replace historical PRbody timings; no incremental performance history will be published in that body.


## Static epilogue scheduling not retained

Candidatecdf7aff completed its full EP4 hu9 sweep:13rows/1300samples,52 finite paired rank-output hashes, clean source/helper/process/GPU closure. None of the four new static choices wins any retention case; only excludedT1 selects static. Best-static versus best-atomic hot times at T4/8/16/32/64/128/256/512 are109.5/148.2/193.4/252.9/288.2/316.3/326.1/347.3us versus101.4/140.2/187.5/248.6/283.1/310.1/319.0/340.3us. Static is1.7–8.0% slower there. All prefills select existing atomic/dispatch choices. The cold decodeGM0.9860× is not attributed to new static code because no static tactic wins those rows; unchanged-path and group-selection variation remains visible. Complete cold table and all156 hot scores are preserved in `comparisons/static-group8-ep4.{md,json}` and `comparisons/static-group8-ep4-hot-scores.json`.

Do not promote this catalog extension or spend EP8/strict qualification on it. Existing manual static scheduling remains supported; only its automatic catalog trial is rejected for this measured workload. The next independent candidate is owned idle-pull skip8a286379 on retainedec42. It is running onhu9 with the same ordinary/deferred protocol and group8 control, while hu6 finishes final whole-PR tables. No shared drop modification or sanitizer run.


## Initial idle-pull skip not retained

Owned candidate8a286379 compiled natively across all8 tactics and completed full EP4 hu9 timing with clean source/helper/process closure and52 finite paired bit-exact rank-output signatures. Cold decodeGM0.982554×; prefill4K/8K/16K0.9665×/0.9945×/0.9941×. Same-tactic hot decode T4–512 ratios are1.0019/0.9971/0.9979/0.9968/1.0028/1.0019/1.0016/1.0021×: no useful targeted gain. Those hot results do not support attributing the entire cold slowdown to the guard. T16K's different hot G1024 score is not an idle-skip benefit: every dispatch warp has input work there. All scores and raw cold results remain under `comparisons/pull-skip-group8-*`.

Do not retain70 added lines or run EP8/strict qualification for this flat result. This tests skipping the initial empty/exhausted scan in idle warps; active warps still execute the inherited scan, including its final exhaustion traversal. It does not reject every possible bound or metadata refactor. Native compilation and output evidence showed no implementation failure to fix. A broader owned transport refactor would need stronger evidence of exposed work before adding that scope.

Next hu9 trial: a96c431 dispatch-only immediate epilogue publication, extending the existing group8 catalog with four(1,1) FC1/FC2 flag-batch choices. Source/lifecycle audit is in `DISPATCH_PUBLICATION_AUDIT.md`; no new fences, barriers, arithmetic or shared-drop edits. FullEP4 retention/selection evidence comes before EP8 or qualification.

The additional raw T8 encoding audit confirms that every selected G512/G1024 CUBIN differs in only four immediate-field bytes across its entire ELF. All scheduling/control bits, other code bytes and non-code sections match; this strengthens the earlier instruction/resource audit without claiming equal runtime. Evidence: `cache-audit/ep4-group-t8-evidence/RAW_ENCODING_AUDIT.md`.


## Final whole-PR tables published

PR8's body was refreshed and read back at pushed head66b6df6 (README-only after measured implementationec42). Both complete comparisons use pre-fusion HashInfer main68eb1, the byte-identical external native benchmark, ordinary ABI preparation, deferred CUPTI lifecycle, and the same hu6 host/boot. All13 rows/100 samples per arm,156 paired rank-output hashes, source/helper identities and process/GPU closure pass. Root independently regenerated the final tables with `refresh_pr8_body.py`; live readback is `pr8-after-group-extension-final-tables.json`.

Decode4–512 geometric speedups are1.079505× EP4 and1.093124× EP8. Every retained decode row is faster. EP4 prefill4K/8K/16K ratios are0.9798/1.0040/0.9776; EP8 ratios1.0195/1.0066/0.9699. The PR explicitly records remaining latency increases of2.1% at EP4/4K,2.3% at EP4/16K and3.1% at EP8/16K. These are complete-PR numbers, not group8-only gains. Focused qualification remains256 combinations; no full120-case or sanitizer claim was added. Public FlashInfer remains unchanged.

The a96 immediate-dispatch-publication trial now runs EP4 and EP8 on separate nodes concurrently. EP4 completed with exit0; artifact/selection audit is pending. EP8 remains with its assigned lane owner. Both use in-tree native benchmark harness34ac and each node's matching ec42 control; do not use the external whole-PR helper for these incremental ratios. Comparator labels now include the full epilogue flag pair so retained and new selections are distinguishable. No additional candidate is promoted.


## Immediate publication EP4 result, awaiting EP8

Candidatea96 completed13×100 onhu9 with52 paired finite exact outputs and clean closure; archiveb69b00dfc491712aae94fac2979d7d238d96756342c519cf318ee605acd41ae0. Original8 choices remain selected throughout decode. The cold decodeGM0.971694× therefore is not evidence that immediate publication slows decode; unchanged selection plus serial variation dominates that comparison. At4K/8K, newG1024/N128/dispatch(1,1) wins: same-sweep best original/new hot times790.8→786.4us and1341.9→1327.2us, gains0.56%/1.11%. Cold ratios are0.976757/1.026532;16K0.999488 with originalflags. The complete156 hot scores and paired cold table are preserved. The large4K/8K within-sweep trends limit causal interpretation of these small gains. No promotion yet; EP8 guard continues.

Next independent candidate is the historical whole-path coalesced16 reducer port ontoec42, preserving original8 tactics and current optional-score contract. EP4T512 has114688 width8 workers versus75776 worker capacity, while width16 reduces the work count to57344. EP8T512 already fits one stride. Root inspected the source port: slab mappingtile=qG+r selects8-element slabs2qG+r and2qG+r+G, a bijection covering every acceptedH%32; all loads/stores remain128-bit with16-byte alignment. Ordered FP32 multiply/FMA/add branches and finalBF16 cast are unchanged. Generated resources, native outputs and actual gains remain unvalidated until the benchmark. No fifth-WG experiment or sanitizer added.


## Immediate publication complete; keep the automatic catalog at eight

The EP8 guard completed all 13×100 samples on hu6 with exit zero, matching host/boot, unchanged source/helpers, clean process/GPU closure, and 104 paired finite output hashes. Root independently reran the comparator. Archive SHA256: `9ce2a33e9d6e36c6302184309b125895e5ab34db94a10bbe9950c79c7b8bb7a6`.

New immediate-publication tactics win all three EP8 prefills. Cold 4K/8K/16K ratios are **1.0280× / 0.9701× / 1.0149×**. Corresponding same-sweep hot ratios are **1.0131× / 1.0296× / 1.0021×**. Decode keeps original tactics, so its 1.0019× aggregate is not evidence of a new-path gain. EP8/8K also changes the selected group hint from 1024 to 512; its hot gain does not establish a cold-cache gain.

Keep `a96c431` unpromoted. The extension has useful hot prefill selections on both EP sizes, but EP4/4K and EP8/8K cold medians regress and there is no new decode winner. Preserve the complete source and both result sets for further investigation; do not assume those losses are noise or claim the direction disproved. No additional numerical qualification or sanitizer was run. The retained PR8 catalog remains eight tactics. Hu6 is held idle for a coalesced16 EP8 guard only if its EP4 result warrants one.


## Coalesced paired-slab combine not retained

Candidate `44842792` compiled natively across the original eight tactics and completed the full EP4 sweep in 625 seconds. All 52 paired output hashes are finite, repeatable and bit-identical to the control. The 104-file source, helpers and process/GPU closure are verified. Archive SHA256: `252e26bec587ccd24df690ae609a0c9869c18e7e7e9045711145f915bb8992db`.

Cold decode geometric speedup is **0.974304×**; the targeted T512 row is **0.9947×**. Prefill 4K/8K/16K ratios are **0.9796× / 1.0055× / 1.0037×**. This is insufficient for decode-prioritized retention. Matched hot timings reinforce the decision: every decode row is slower than the same tactic in both the original ec42 control and the recent publication trial's unchanged original paths. Against the latter, T4 is 101.8→104.7 µs, T8 138.9→142.6 µs, and T512 341.0→341.8 µs. Do not attribute the whole cold slowdown to the reducer without stronger causal evidence, but the structural one-stride advantage did not yield a measured decode improvement.

Preserve the high-quality mapping port and all evidence; no native compilation or output failure needs repair. No EP8 guard, strict numerical expansion, resource capture or sanitizer is justified for this result. The resource-inspection plan remains available for future work. See `comparisons/coalesced16-group8-ep4.{md,json}`, all104 hot scores, `...-hot-matched.json`, and `coalesced16-group8/ROOT_SOURCE_AUDIT.json`.

Both nodes are idle after verified closure. Canonical PR8 remains `66b6df6`, with the retained group-size catalog at ec42 and the published final whole-PR EP4/EP8 tables. No rejected candidate changed canonical or public FlashInfer source.
