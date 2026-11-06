# PDL graph timeline audit

**Early triggers produce real kernel-lifetime overlap. They do not explain the prefill regression as slower preparation.** In the one T16384 replay, preparation remains25.4–25.5µs, whereas FC1 grows200.705→263.744µs and its generated register count changes80→88. Much of that extra FC1 lifetime occurs before FC2 launches. This directs the next source/codegen investigation toward FC1; it does not prove a register-count cause.

This is a diagnostic audit of one warmed CUDA-graph replay per arm at T128/N16 and T16384/N256. **These are Nsight timestamps, not benchmark medians or a replacement performance campaign.** All four traced graph outputs match the current corrected control byte-for-byte, pre/post input hashes match, and source hashes remain unchanged.

## Frozen sources and execution

Control `profile-aab93f`, HEAD `aab93f854054de834447bdd8985b8bbd653fb3c8`. Candidate `pdl-startup-review`, same base and only two unstaged source changes: core SHA256 `bbb0482387f0862f0e21fc27c93b08a76e825c38cbda1872184ccd20b7a6f1b2`, preparation `a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`. Utils/finalizer are byte-identical. Actual source copies are in [source-snapshots](source-snapshots); [source-manifest.json](source-manifest.json) pins all related files. The source owner's PDL-on exact gate was verified before the first trace. [Owner codegen review](../pdl_startup_experiment/PDL_CODEGEN_REVIEW_bbb04823.json) records wait/trigger and FC2 release-fence order.

GPU3 on c1 `fi-w4a4-narrow-1025`, B200 UUID `GPU-8f15506e-8209-ef53-6b00-b04ece9e69d3`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78, CuTe4.7.1. Native `bench_moe_deepseek` inputs,32 local experts, H7168/I2048/top-k8, NVFP4, unfused finalize. T128 uses M128/N16/1CTA for both GEMMs; T16384 uses M256/N256/2CTA for both. The persistent grid is148 physical CTAs; the group2 case uses74 clusters. Target occupancy remains one resident CTA per SM.

The helper inherits the owner's actual-module dispatch: each arm binds its real core, utils, preparation and finalizer with independent caches. It disables observers and releases their intermediates before graph capture. After10 warm calls, it captures `CUDAGraph(keep_graph=True)`, explicitly instantiates, replays10 times, checks output bytes, exports graph metadata/DOT, then profiles exactly one replay and rechecks bytes. Inputs/routing are identical between arms within each shape process. No cold-L2 fill or benchmark timer is part of this warmed timeline.

## Observed node intervals

Times are relative to each replay's first route-kernel start. Kernel lifetimes include setup and dependency waits. Larger overlapping bars do not imply simultaneous useful computation.

### T128, route N16

|Kernel|Control start→end, µs|Candidate start→end, µs|Control/candidate duration, µs|
|---|---:|---:|---:|
|route|0.000→2.848|0.000→2.720|2.848 / 2.720|
|sort|1.792→6.272|1.728→6.016|4.480 / 4.288|
|prep|6.048→9.536|5.824→8.992|3.488 / 3.168|
|FC1|9.312→84.928|7.808→83.136|75.616 / 75.328|
|FC2|84.480→126.880|71.968→122.464|42.400 / 50.496|
|combine|126.400→129.568|84.064→125.120|3.168 / 41.056|

### T16384, route N256

|Kernel|Control start→end, µs|Candidate start→end, µs|Control/candidate duration, µs|
|---|---:|---:|---:|
|route|0.000→25.376|0.000→25.184|25.376 / 25.184|
|sort_init|24.416→25.855|24.224→25.663|1.439 / 1.439|
|sort|25.856→33.792|25.664→33.952|7.936 / 8.288|
|prep|33.568→58.976|33.760→59.296|25.408 / 25.536|
|FC1|58.752→259.457|55.872→319.616|200.705 / 263.744|
|FC2|258.881→403.777|286.304→464.032|144.896 / 177.728|
|combine|403.201→484.129|320.672→551.616|80.928 / 230.944|

|Shape|Boundary|Control overlap, µs|Candidate overlap, µs|
|---|---|---:|---:|
|T128|prep→FC1|0.224|1.184|
|T128|FC1→FC2|0.448|11.168|
|T128|FC2→combine|0.480|38.400|
|T16384|prep→FC1|0.224|3.424|
|T16384|FC1→FC2|0.576|33.312|
|T16384|FC2→combine|0.576|143.360|

At T128, the candidate gives FC2 and combine much larger execution windows. Each GEMM uses197504B dynamic SMEM (reported allocation200704B), so FC1 and FC2 CTAs cannot coexist on one233472B SM. Earlier FC2 admission on SMs vacated by FC1 tails is consistent with these resource constraints and intervals. This trace does not identify individual SMs/CTAs or separate startup from time blocked in `griddepcontrol.wait`. Combine has no shared memory and can coexist subject to thread/register admission.

At T16384, preparation's grid2368, block128 and32 registers are unchanged, and its lifetime barely changes. FC1 starts2.880µs earlier yet ends60.159µs later. Candidate FC2 starts230.432µs after FC1 starts, already29.727µs beyond the entire control FC1 lifetime; a substantial portion of the extra FC1 time therefore predates that downstream launch. Prep scheduling interference alone is not supported by this trace's nearly unchanged prep duration. Early admission or device-wide effects are not completely excluded.

The FC2 lifetime increase32.832µs nearly equals the increase32.736µs in its overlap with FC1. Its interval after FC1 ends is144.416µs versus144.320µs in control. This is consistent with extra dependency waiting; it is not a measurement of FC2's isolated compute time and does not override the owner's separate phase benchmarks. Combine similarly includes a long prerequisite wait. No per-warp wait counter or per-CTA timeline was collected.

## Resource/codegen difference

|T16384 kernel|Registers control→candidate|Dynamic SMEM|Reported executed SMEM|Threads|Local bytes/thread|
|---|---:|---:|---:|---:|---:|
|FC1|80→88|195584|200704|288|0→0|
|FC2|120→122|229888|233472|288|0→0|
|Preparation|32→32|0|0|128|0→0|

The changes to register counts prove that moving the trigger changed generated code beyond the launch timestamp. Shared allocation, geometry, cluster limits and reported local bytes/thread are unchanged. A higher register count does not establish a performance cause or an occupancy drop. Source/SASS scheduling needs separate examination; no new variant or GPU profile was launched here. [kernel-resources.json](kernel-resources.json) preserves every relevant reported field. `localMemoryTotal` is retained raw and is not interpreted as spilled bytes. All three QMD timestamps (`qmdBulkReleaseDone`, `qmdPreexitDone`, `qmdLastCtaDone`) are NULL, so they provide no timing evidence.

## Graph metadata limitation — correction to raw receipts

Both graph captures have the expected actual source kernel identities and six/seven nodes. The installed cuda-bindings13.2 `cuGraphGetEdges` returns type/port data, and all records after the first read as type1/programmatic, from_port1/programmatic, to_port0. **The first record contains impossible enum/port values in each arm. The raw helper's `complete:true` flag is therefore invalid and is explicitly superseded by `PARTIAL_INVALID_EDGE_DATA` in [summary.json](summary.json).** Do not present this as a completely verified dependency-edge dump.

The frozen helper did not validate type/port ranges. A returned-struct lifetime issue is plausible but unconfirmed because the installed binding implementation source is unavailable. DOT confirms edge endpoints and target port0, not source port or dependency type. No raw file or executed helper was rewritten. [Graph API receipt](GRAPH_METADATA_API.md) distinguishes launch-only attribute6 from captured-edge metadata; no unsupported attribute query was used. The observed Nsight kernel overlap remains independent evidence that secondary launches occur early. A future metadata-only repair should use validated caller-owned buffers with the exported C `cuGraphGetEdges_v2` API rather than assuming an immediate Python field snapshot repairs ownership.

## Reproduction and durable evidence

[run_remote.py](run_remote.py) and [prefill-remote-program.py](prefill-remote-program.py) preserve complete commands and guards. The core invocation is:

```bash
source scripts/recovery442/env_candidate.sh
CUDA_VISIBLE_DEVICES=3 \
CUTE_DSL_CACHE_DIR=$PWD/cache/pdl-timeline-aab/cute_dsl \
nsys profile --trace=cuda,nvtx --capture-range=cudaProfilerApi \
  --capture-range-end=repeat:2 --sample=none --cpuctxsw=none \
  --cuda-graph-trace=node --output <fresh-prefix> \
  .venv/bin/python scripts/pdl_timeline_audit/probe_graph.py \
  --control profile-aab93f --candidate pdl-startup-review --tokens 128 \
  --tactic '[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]' \
  --output <fresh-result.json>
```

The T16384 run uses `probe_graph_prefill.py`, `--tokens 16384`, and the M256/N256/2CTA tuple above. Fresh output paths are mandatory. These commands are a record, not a request for additional execution.

- [Decode archive](decode/raw.tar.gz), SHA256 `130dfe313bfa2c7d7d636c36cea66933b867456baa53115ce7c928005e761f7c`.
- [Prefill archive](prefill/raw.tar.gz), SHA256 `390eddf5ac3a7886e8f939773817cc44c751866c7598e2568d90d679f360f102`.
- Each archive contains two `.nsys-rep` files, two SQLite exports, graph DOTs, exact output/source receipts, and commands. `fetch-receipt.json` validates every member hash.
- [summary.json](summary.json) is regenerated by [summarize.py](summarize.py) from the raw SQLite/results and rejects invalid edge metadata. Profiling was confined to GPU3; all jobs finished and GPU3 is released.
