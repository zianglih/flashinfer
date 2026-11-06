# V3 T16 mixed-MX metadata-depth diagnosis

All three sources are frozen at b85eff41 plus the identical six-field all-CLC policy. Depth1 uses control patch97cf417d; depth2 uses5920de4f; depth3 usesab24777c. Exact source/cache pin checks pass before and after every profile. Geometry is the saved full-run V3EP8 T16 mixed MXFP4x8 choice, N16/M128/1CTA/K8 in both phases, with both scheduler flags explicitly enabled in a private cache copy. The public benchmark, routing hashes and saved hits are unchanged across arms. There is no AUTO fallback and no production source modification.

GPU7 B300/SM103, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe4.7.1. Public nonfused-finalize MX graph, initial activation quantization excluded as in the MX family contract. Nsight Systems captures three cold-L2 graph replays per arm. Nsight Compute captures only selected FC1/FC2 kernels, six replay passes and27requested metrics. **All durations below are diagnostic; the100sample public CUPTI CAAC records remain the performance evidence.** Selected-kernel replay serializes PDL and resets caches.

## Generated code and resources

|Depth|FC1 instructions|FC2 instructions|Registers/phase|Dynamic SMEM/phase|Occupancy|Operand/acc stages|
|---|---:|---:|---:|---:|---:|---|
|1|1512|1352|76|215936B|1CTA/SM|5/2|
|2|1552|1392|76|215936B|1CTA/SM|5/2|
|3|1568|1408|76|216064B|1CTA/SM|5/2|

No spills or operand-stage reductions occur. Relative to depth1, depth2 adds40static instruction sites per phase, depth3 adds56. The non-NOP deltas are39/38 and55/54 for FC1/FC2. Most extra sites are metadata-index address/wrap work (`LEA`, `SEL`, integer increment/predicate) plus extra barrier initialization and tail waits. Depth1 makes metadata addresses constant, while a deeper ring requires runtime index maintenance. Static instruction sites are not executed-instruction counts.

## Three-replay graph trace

|Depth|FC1 median us|FC2 median us|FC1→FC2 overlap median us|Exposed through FC1 mean us|FC2 extension mean us|Combine tail mean us|
|---|---:|---:|---:|---:|---:|---:|
|1|40.992|30.144|11.936|48.118|18.059|1.792|
|2|44.544|42.176|24.128|52.118|18.261|1.792|
|3|45.312|35.264|17.216|53.099|18.123|1.792|

The graph penalty is exposed in FC1: roughly+4us for depth2 and+5us for depth3. FC2 extension and combine tail are nearly unchanged. FC1→FC2 overlap increases, so reduced dependent overlap does not explain this particular decode loss. Earlier FC2 startup/weight-prefetch competition remains a possible contributor. Plain graph traces do not identify individual cancellation or publication timestamps, so they cannot prove the physical-CTA PDL eligibility mechanism.

## Serialized NCU counters

|Phase/depth|Duration us|Executed instructions|DRAM read MB|DRAM throughput %peak|Long scoreboard %|
|---|---:|---:|---:|---:|---:|
|fc1/depth1|51.680|3736908|204.319|52.44|73.71|
|fc2/depth1|31.456|2410026|101.847|43.42|66.21|
|fc1/depth3|53.792|3768056|204.328|50.36|73.24|
|fc2/depth3|32.256|2460133|101.849|42.32|66.12|

Depth3 is slower even under serialized profiling: FC1+4.09%, FC2+2.54%. Its executed instructions grow0.83%/2.08%, while DRAM read bytes are essentially identical. Long-scoreboard stalls dominate at~74%/~66%, with lower achieved bandwidth. This establishes a kernel-local scheduler/codegen cost in addition to possible overlap competition. It does not isolate work reservation/hoarding as the sole cause.

Both automatic-depth policies are unretained because the matched public V3T16 CAAC shows repeatable decode regressions. The prefill gains and diagnostics motivate simpler metadata indexing or reservation mechanics if revisited; they do not justify model/dtype/token thresholds. GPU7 was released after these captures. Exact correctness gates and full raw100sample records remain in sibling `clc-info-depth` and `clc-info-lookahead` ledgers.

Helpers: `scripts/clc_metadata_decode_profile_20261027/{observe_profile,nsys_campaign,ncu_campaign,analyze_nsys,analyze_ncu,analyze_codegen,collect}.py`. `collection.json` binds every raw artifact; source receipts, saved tactic/histogram hashes, public CLI, codegen hashes, Nsight reports and raw CSV are retained beside this note. No new upstream tests or PR edits.

## Final policy decision

Keep the single-stage metadata queue and the180-tactic, four-field all-CLC search. Both universal deeper defaults are rejected by the decode evidence. No metadata-depth autotune axis is pursued: adding one would defeat the requested reduction in search space. Further work, if justified, must simplify the single policy rather than add model/dtype dispatch or more tuning dimensions. No additional GPU runs or cancellation-timeline captures are scheduled.
