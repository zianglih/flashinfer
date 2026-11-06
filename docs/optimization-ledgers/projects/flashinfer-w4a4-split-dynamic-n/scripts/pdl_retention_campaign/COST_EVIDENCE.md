# Prior full-grid elapsed-cost evidence

CPU-only audit on 2026-10-25. No benchmarks, GPU work, source edits, or frozen-helper changes. These are actual historical observer/launcher intervals, not promises for a new candidate. All listed sweeps completed the same 13-token grid `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`, with 10 warmups and 100 cold-L2 CUDA-graph CUPTI iterations per point.

The useful planning evidence is **roughly 15–22 seconds per previously exercised CuTe format sweep**, and **41.750 seconds for the historical native-TRT repeat with existing native artifacts**. Native TRT's first sweep took **405.567 seconds** with JIT/build/download setup. There is no isolated full-grid cold-CuTe compilation measurement in the audited records, and no measured three-GPU parallel schedule for the proposed campaign.

## What the clocks include

The observers set `started_utc` after imports/source checks, then start `wall_seconds` immediately before the ascending token loop. That loop includes native input preparation, any lazy compilation/loading/downloads, AUTO tuning, graph measurement, cache-snapshot writes, synchronization and cleanup. Imports and some provenance collection precede the timer; later source verification is also outside it. Thus neither field is full process lifetime or compilation-only time. See `scripts/fc1_regular_tma_auto/run_nvfp4_experiment.py:105,159–212`, `run_mx_experiment.py:161,219–276`, and `scripts/trtllm_nvfp4_reference/run_trtllm_benchmark.py:163–215`.

Compiler/native caches, fresh AUTO selection, and cold hardware L2 are separate states. Every sweep below has `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0`, uses normal AUTO, and saves winners only as evidence. In-process winners persist across ascending token counts. Cold-L2 timing does not imply cold compiler or native-artifact caches.

## CuTe final regular-TMA campaign

Let **F** be `evidence/regular-tma-final-review/raw/results/regular-tma-final-review/`. A1 and A2 are the same reviewed regular-TMA source based on442; B2 is the original a65 source. They are historical source/node epochs, not current aab controls. Each JSON below has 13 complete rows. Values are derived directly from its `wall_seconds` and UTC endpoints:

|Sweep / file below F|Observer loop seconds|UTC start→finish seconds|JSON anchors: start; wall/end|
|---|---:|---:|---|
|`A1/A1-nvfp4.json`|17.882|18.553|4;23619–23620|
|`A1/A1-mxfp8.json`|17.672|18.335|4;23629–23630|
|`A1/A1-mxfp4.json`|15.716|16.244|4;23629–23630|
|`A2/A1-nvfp4.json`|20.052|20.620|4;23619–23620|
|`A2/A1-mxfp8.json`|21.112|21.634|4;23629–23630|
|`A2/A1-mxfp4.json`|14.921|15.491|4;23629–23630|
|`B2/B2-nvfp4.json`|14.613|17.358|4;10045–10046|
|`B2/B2-mxfp8.json`|14.178|17.061|4;10053–10054|
|`B2/B2-mxfp4.json`|17.818|20.275|4;10053–10054|

The observed schedule ran NVFP4 on GPU0 concurrently with MXFP8 then mixed on GPU1 (`scripts/regular_tma_final_campaign/run_candidate_arm.sh:22–31`). Across all three formats, earliest observer `started_utc` to latest `finished_utc` was **42.566 s A1**, **44.832 s A2**, and **41.384 s B2**. These include the gap before the second GPU1 process's observer starts, but omit initial preflight/import time and final validation. They are not a measurement of running all three formats simultaneously.

B2 additionally has outer process boundaries in `scripts/regular_tma_final_campaign/launch-B2-v2.log:4–9`: MXFP8 **21.236 s**, NVFP4 **21.583 s**, mixed **23.908 s**, and **45.503 s** earliest START→latest END. Those include child startup and per-mode validation (`run_baseline_v2.py:80–91`). Its broader command receipt→complete receipt interval is **56.952 s** (`F/B2/commands.json` `started_utc=11:36:20.622188`; `complete.json` `finished_utc=11:37:17.573928`, UTC). Even that starts after earlier preparation checks.

Cache qualification: the launcher uses the same manifest-specific per-format CuTe cache path for A1 and A2, and does not clear it (`run_candidate_arm.sh:12,22–26`). Native extensions use the existing `cache/candidate-442` epoch (`scripts/recovery442/env_candidate.sh:1–4`). B2 uses the separate existing a65 epoch. A2 therefore reuses the A1 compiler-cache namespace, but no cache-entry inventory or compiler hit/miss counters were recorded. A1's initially-empty state is not proved. Do not label either a controlled cold-compile measurement.

The corresponding `.log` files contain 13 AUTO start/end pairs. Summing those logged windows gives A1 **12.267/11.943/9.757 s** and A2 **12.405/15.070/9.591 s** for NV/MX/mixed. For example, A1 NV's first window is11:28:46.713→11:28:54.530 (`F/A1/A1-nvfp4.log:1–3`). These windows include lazy setup/compilation as well as tuning and cannot isolate compiler cost. A2 still performs AUTO despite reusing the cache namespace.

An older setup-bearing CuTe NV sweep is also preserved: `evidence/regular-tma-final-review/raw/results/baseline-r1.json:10041–10042` records **274.425 s** for13 points. Its `.log:1–3` announces native quantization/routing JIT builds before AUTO, followed by native header/cubin downloads. This demonstrates setup contamination in that historical first sweep; it does not measure just CuTe compilation and is not a current-candidate forecast.

## Native TRT NVFP4 campaign

Let **R** be `evidence/trtllm-nvfp4-reference-98fd/raw/results/trtllm-nvfp4-reference-98fd/`. These are the completed98fd/B200-83 reference sweeps, not aab/B200-92 results. The retention plan explicitly preserves that boundary (`scripts/pdl_retention_plan/README.md:13`).

|Sweep / file below R|Observer loop seconds|UTC start→finish seconds|First AUTO window seconds|
|---|---:|---:|---:|
|`T1/T1-nvfp4.json`|405.567|407.232|400.888|
|`T2/T2-nvfp4.json`|41.750|43.508|37.004|

JSON anchors are `:4,10048–10049` for both. T1 UTC is12:02:24.318640→12:09:11.550183; T2 is12:09:20.326072→12:10:03.834148. Each sweep is a fresh subprocess (`scripts/trtllm_nvfp4_reference/run_reference.py:153–157`).

- T1 incurred native setup: `R/T1/T1-nvfp4.log:5` announces `fused_moe_trtllm_sm100` JIT at12:02:29.462. The next cubin-fetch entry is12:07:49.996 at`:6`. The log contains **181 successful downloads:180 cubins plus one metadata file**; the final download is`:556`, at12:08:59.803. The first AUTO window ends at`:571`,12:09:07.521.
- T2 has **zero build/download announcements**, reuses the same native workspace cache, and freshly tunes21 buckets from12:09:22.712 to12:09:59.716 (`R/T2/T2-nvfp4.log:1–27`). Both JSONs record `FLASHINFER_AUTOTUNER_LOAD_FROM_FILE=0` and the shared native cache around`:9840–9843`; the helper passes `do_autotune=True` and `autotune_cache=None` (`run_trtllm_benchmark.py:176–183`).
- The **320.534 s** between T1's build announcement and next fetch entry is an observed log gap, not a compiler-only duration. Subtracting T2 from T1 also mixes JIT, downloads, filesystem/network state and other work. Neither subtraction is a valid pure compilation estimate.

## Bound for the proposed campaign

Use the reused-artifact sweeps as historical execution-cost context, not as a guarantee. A new source-specific CuTe cache can add unmeasured compilation; current native artifact reuse must be verified independently. Exact-source experimental-module aliases also need not hit canonical-module cache keys. The proposed stable three-GPU dtype assignment has not been timed here, and CPU compiler contention across processes is not quantified. No honest compilation-only or full new-campaign wall-time estimate can be extracted from these logs without additional instrumentation; the existing observers can preserve actual elapsed cost without changing their measured loop.

## Measured final retention campaign cost

The final frozen8c1a campaign completed on B200-92 with the unchanged three-format parallel outer runner. These child wall times include import, fresh AUTO and the unchanged observer loop; they are not isolated compiler measurements.

|Arm|NVFP4 seconds|MXFP8 seconds|Mixed seconds|TRT seconds|
|---|---:|---:|---:|---:|
|C1|27.792|27.516|24.821|—|
|T1|—|—|—|47.494|
|A1|26.765|26.320|24.003|—|
|A2|24.484|24.665|21.568|—|
|T2|—|—|—|56.027|
|C2|24.636|24.820|21.687|—|

All182 rows completed. Exact receipts live under `evidence/pdl-retention-8c1a/full/raw/results/pdl-behavior-retention/<arm>/execution.json`. Native cache remained candidate-442, CuTe cache used exact commit+mode namespaces, AUTO loading was off, and KEEP/DUMP were unset. No separate compilation-only duration is available.
