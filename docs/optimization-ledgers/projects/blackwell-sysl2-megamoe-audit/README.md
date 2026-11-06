# Blackwell SysL2 / W4A16 MegaMoE cache-hint experiments

This effort measures isolated TMA L2 eviction-policy changes in HashInfer W4A16 MegaMoE and keeps a separate peer-TMA diagnostic for hardware attribution. The production benchmark follows merged HashInfer PR11, Runtime alpha batching performance [private repository link omitted]. The baseline is the later merged PR13 [private repository link omitted] source, `a4b2d9a690e302deb0feac8b7cc872ab0b31a766`; PR13's tracing additions are retained but IKET instrumentation is disabled for timing. All eight native sweeps completed; none of the three hint changes provides a consistent EP4/EP8 performance gain. The peer-counter experiment is recorded separately below.

## Execution record

Both native baselines completed once and are frozen in [frozen-baselines.tar.gz](frozen-baselines.tar.gz), with per-file hashes in [frozen-baseline-manifest.json](frozen-baseline-manifest.json). The first `dispatch-normal` attempt completed T1/T2, then rank 3 segfaulted in `cupti.finalize()` at `hashinfer/testing/utils.py:516` during T4 timer teardown. Its partial records are retained and excluded from every comparison. A full, unchanged fresh-process retry uses run label `dispatch-normal-r1` and the same `sources/dispatch-normal` export; both retry topologies completed. No baseline was rerun and no deferred-finalize workaround was applied.

`continue_after_retry.py` waits for both retry topologies, then runs the remaining candidates. It records `continuation-v2-*` separately from the failed original queue. The profiler is queued with `--upstream-state continuation-v2-state.json --receipt-prefix peer-profile-v2`; the first profiler controller correctly aborted without launching GPU work when the original timing queue failed. Final provenance auditing maps the retry label explicitly with `--arm-source dispatch-normal-r1=dispatch-normal`.

Profiler recovery records are preserved separately. `peer_profiles-v1` and `v2` stopped before a measured kernel because torchrun's standalone rendezvous selected an unresolvable node hostname; the first deployment of the loopback fix landed at the wrong remote path, which was corrected and verified. `v3` reached the kernel but NCU kernel replay failed with `ContextSaveFailed` while saving memory. `v4` uses explicit `127.0.0.1` rendezvous and application replay. Its first capture exited successfully, but the wrapper initially expected a long CSV rather than NCU's wide raw CSV. The parser repair reused that successful capture without a GPU rerun, preserving `run_manifest.before-parser-repair.json`; `peer-profile-v6` resumes the remaining five arms under the campaign lock. None of these profiler recoveries changed the native timing or baseline evidence.

## Native performance result

| Candidate | EP | Decode T4–512 GM | Prefill 4K | Prefill 8K | Prefill 16K |
|---|---:|---:|---:|---:|---:|
| dispatch-normal-r1 | 4 | 1.0031× | 1.0011× | 1.0280× | 1.0061× |
| dispatch-last | 4 | 0.9974× | 0.9971× | 1.0368× | 1.0038× |
| local-pool-last | 4 | 0.9921× | 1.0300× | 1.0510× | 1.0016× |
| dispatch-normal-r1 | 8 | 0.9967× | 0.9868× | 0.9930× | 0.9815× |
| dispatch-last | 8 | 1.0243× | 0.9771× | 0.9859× | 1.0024× |
| local-pool-last | 8 | 1.0017× | 0.9756× | 0.9716× | 0.9990× |

Speedup is frozen-baseline median divided by candidate median. EP4 is primary. No candidate is recommended for retention from this campaign: dispatch LAST improves the EP8 decode aggregate but is flat on EP4 and slower at EP8 4K/8K prefill; local-pool LAST has no decode benefit and its EP4 8K median gain is sensitive to within-run drift. All patches remain isolated experiments; the source checkout is unchanged.

The [complete report](summary-v1/summary.md) contains all 13 rows per comparison, exact tactics and raw samples; [raw-evidence.json](summary-v1/raw-evidence.json) preserves the paired machine-readable records. There are 104 completed row records and 10,400 unique rank-MAX samples across the two once-only baselines and six candidate sweeps. [final-provenance-proof.json](final-provenance-proof.json) verifies all eight source closures. No MoE correctness tests were run, as requested.

## Peer traffic result

The two-rank probe uses the same descriptor-free bulk TMA load form and NVSHMEM peer-pointer bootstrap as MegaMoE. Rank 0 reads a 64 KiB immutable rank-1 buffer in sequential 4 KiB transfers, with a wait after each transfer. Rank 1 prepares its buffer locally. No requester warmup of that peer buffer is performed. All six captures completed with four NCU application-replay passes each, cache control disabled and clock control disabled.

| TMA load policy | Logical bytes, 1 pass | NVLink RX payload, 1 pass | Logical bytes, 64 passes | NVLink RX payload, 64 passes | RX growth |
|---|---:|---:|---:|---:|---:|
| FIRST | 65,536 | 65,536 | 4,194,304 | 4,194,304 | 64× |
| NORMAL | 65,536 | 65,536 | 4,194,304 | 4,194,304 | 64× |
| LAST | 65,536 | 65,536 | 4,194,304 | 4,194,304 | 64× |

Requester TX user-response payload is zero in every arm. Repeated reads receive the full logical demand over NVLink under every tested policy: there is no observable requester-side traffic elimination from cache reuse in this probe. The selected SysL2 peer request totals, lookup counts and policy buckets are all zero. This is **not** a 100% miss rate, evidence that the hints reached SysL2, or proof of a particular physical bypass path. Owner-side L2 versus HBM behavior was not measured.

The result applies to this B300/driver/NVSHMEM allocation and TMA instruction path. It does not rule out cacheable peer mappings through another allocation mechanism, coherent system-memory caching, concurrent in-flight request coalescing, or different launch geometry. The single-CTA sequential probe tests persistent reuse and is not a bandwidth benchmark. Event timings captured under NCU are excluded from performance claims. Application replay recreates allocation and preparation for each pass; the final `probe.jsonl` and all per-pass stdout records are retained.

[peer-profile-summary.md](peer-profile-summary.md) reports all request counters, payload counts and replay evidence; [peer-profile-summary.json](peer-profile-summary.json) retains every original metric, unit and probe record. Raw CSVs and NCU reports are in [results/peer_profiles-v4/](results/peer_profiles-v4/). The interpretation follows [NVIDIA's application-replay documentation](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#application-replay).

A bounded aggregate-counter follow-up used NORMAL with 64 passes and three application-replay passes. It again measured 4,194,304 RX bytes, with 67 aggregate SysL2 requests: 67 classified as system memory, zero as peer memory, and 3 lookup hits / 64 misses. Thus the aggregate counters are active, but the selected peer counters do not observe this traffic. The aggregate system-memory requests cannot be attributed to the peer TMA reads without a matched local/no-peer control; kernel/runtime system-memory activity may contribute. No SysL2 hit rate for MegaMoE is derived from them. Exact commands, same-boot/GPU identity, raw CSV/report and all six counters are in [results/peer_aperture-v1/](results/peer_aperture-v1/).

All profiling finished successfully. The node is left allocated and idle so the frozen native baselines can be reused in this runtime. The project source checkout remains clean; experimental patches and all failed-attempt evidence are preserved.

## Source and environment

| Item | Recorded value |
|---|---|
| Local effort | `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit` |
| Remote effort | `/workspace/hashinfer-sysl2-0930` |
| Devbox | `hashinfer-sysl2-0930`, one bare C2 node, namespace `infra` |
| Physical node | `hu-pdx-5`, 8× B300; EP4 and EP8 run serially |
| Image | `nvcr.io/nvidia/pytorch:26.05-py3` |
| Image digest | `sha256:222d8b18e671be5c3ef91cb41727a2572a0b23f59ded6c39f373a96946f6f2ba` |
| Baseline source | `a4b2d9a690e302deb0feac8b7cc872ab0b31a766` |
| Baseline export | Remote `sources/baseline`; local `baseline.tar` |
| Interpreter | Remote `venv/bin/python`; system-site-packages retains container Torch/CUDA13.2 |

[campaign-provenance.json](campaign-provenance.json) records the allocation and explicit user overrides. The `ziangli` namespace lacked quota; its queued request was deleted before requesting `infra`. Size was unspecified. Actual boot ID, GPU UUIDs, driver and source fingerprints are recorded per benchmark run, rather than inferred from this table.

[setup_runtime.sh](setup_runtime.sh) pins CuTe DSL4.8.0, CUDA Python13.2.0, nvshmem4py0.3.1, the NVIDIA NVSHMEM wheel3.8.0, cuda-core1.2.1, TVM FFI0.1.14.post1, cupti-python13.4.0, CUDA CUPTI13.4.92 and CCCL13.3.4.3.1. The loaded native NVSHMEM library prints version3.6.5; the wheel and runtime version strings are recorded separately. Remote `results/environment.json` and `results/environment-freeze.txt` preserve the installed environment. [merged-pr-contracts.json](merged-pr-contracts.json) and [pr11-body.md](pr11-body.md) retain the source PR records.

The active ranks' `/proc` mappings confirm the loaded library is `/usr/lib/x86_64-linux-gnu/nvshmem/13/libnvshmem_host.so.3.6.5`, SHA256 `5b2723d14aa9ff838088319adf0b5b8676b4f66e8c780aa658a2f6f03d7227fa`; see [nvshmem-loaded-library.json](results/nvshmem-loaded-library.json). The installed wheel version must not be substituted for this runtime evidence.

## Isolated candidates

Each candidate starts from the same baseline; candidates are not stacked. Diffs are in [patches/](patches/), immutable exports in [candidates/](candidates/), and their hashes/static scope checks in `candidates/manifest.json`, `candidates/manifest-local-pool.json` and [static-candidate-provenance.json](static-candidate-provenance.json).

| Arm | Changed operation | Baseline → candidate policy |
|---|---|---|
| `baseline` | Unmodified merged source | Dispatch input loads `EVICT_FIRST`; FC1 pool stores `EVICT_NORMAL` |
| `dispatch-normal` | Dispatch input TMA load, including peer and self-rank rows | `EVICT_FIRST` → `EVICT_NORMAL` (`0x1000000000000000`) |
| `dispatch-last` | Same dispatch input TMA load | `EVICT_FIRST` → `EVICT_LAST` (`0x14F0000000000000`) |
| `local-pool-last` | Dispatch store into the local FC1 activation pool | `EVICT_NORMAL` → `EVICT_LAST` (`0x14F0000000000000`) |

The dispatch-load arms preserve FC2 staging loads, stores and GEMM weight loads. The local-pool arm preserves loads and peer-return stores. The modified helper defaults preserve every other call site. These are cache-hint changes, not an allocator mapping or a SysL2 enable switch.

## SysL2 and the exposed controls

[NVIDIA's Nsight Compute unit reference](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#units) identifies `syslts` as the L2 cache for system and peer memory. Routing through that unit does not establish that a particular peer mapping allocates reusable cache lines. A requester cache hit can avoid an NVLink response; an owner-side L2 hit can avoid owner HBM while still transferring the data over NVLink. The two effects require different evidence.

The public NVIDIA driver source inspected at `61dcc93722ecb418bb5f2e00923f05b4b8051dd1` maps the default P2P cache attribute to uncached in [mem.c](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/61dcc93722ecb418bb5f2e00923f05b4b8051dd1/src/nvidia/src/kernel/mem_mgr/mem.c#L431-L450); [nv_gpu_ops.c](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/61dcc93722ecb418bb5f2e00923f05b4b8051dd1/src/nvidia/src/kernel/rmapi/nv_gpu_ops.c#L3753-L3773) derives peer mapping volatility from that attribute. This supports an uncached-default hypothesis, but it is not a readback of this allocation's PTE or a verified source match for the installed driver. The hardware probe tests the actual NVSHMEM allocation path.

[PTX](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#cache-eviction-priority-hints) exposes eviction priorities, cache operators, and policy operands such as `.L2::cache_hint`. `evict_first` is a retention priority, not a documented no-allocation command. [CuTe DSL's TMA copy implementation](https://github.com/NVIDIA/cutlass/blob/main/python/CuTeDSL/cutlass/cute/nvgpu/cpasync/copy.py) exposes an `Int64` `cache_policy` argument to `cute.copy`. This MegaMoE path already uses equivalent inline PTX in `ptx_helpers.py`: dispatch input loads default to FIRST and stores to NORMAL. The experiment changes those existing policy operands at individual call sites.

No public CuTe/PTX control was found that independently selects SysL2 or overrides an uncached peer mapping. `.sys` denotes memory-ordering scope. A different eviction hint alone is not a cacheability enable switch. The diagnostic retains request totals, lookup counts and NVLink user-response payload bytes separately to test reuse without equating every unclassified request with a cache miss.

## Generated-code evidence

[codegen-proof.json](codegen-proof.json) confirms that retained NORMAL code replaces the dispatch FIRST operand while keeping the FC2 staging and store policies. Four additional immediate changes are attributable to its different AUTO group hint. [codegen-proof-dispatch-last.json](codegen-proof-dispatch-last.json) compares the matching final EP8 T16384 tactic: the normalized PTX differs in exactly one policy-immediate line, and its 102,528-byte CUBIN text differs in one byte. Both policies retain REG96, STACK0, static SHARED1024, LOCAL0 and CONSTANT[0]2232. Static shared memory does not include dynamic shared allocation.

These retained dumps use the final Int64 contiguous warmup ABI, whereas the timed native input IDs are Int32. They demonstrate policy lowering in the retained specialization, not an exact binding to every timed rank's binary. No cache-residency conclusion follows from emitted PTX alone. The collection inventories, diffs, CUBINs and offline resource reports remain in [codegen/](codegen/).

[codegen-proof-local-pool-last.json](codegen-proof-local-pool-last.json) likewise confirms the local pool store's NORMAL→LAST change while keeping dispatch and return policies unchanged. Four other PTX immediate changes reflect AUTO group1024→512 selection; resource usage matches baseline. [frozen-baseline-verification.json](frozen-baseline-verification.json) verifies all eleven manifest entries, the archive payloads and the exact baseline records reused in the final summary.

## Measurement contract and user overrides

- Native entrypoint: `benchmarks/bench_cute_dsl_moe_distributed.py`, unchanged together with `hashinfer/testing/utils.py`.
- Workload: H7168/I2048/E256/top-k8, BF16 activations, canonical NVFP4 weights, runtime FP32 unit alphas, seeded precomputed DeepSeek routing and deterministic external combine. Default FC2 routing-weight placement and in-kernel reduction disabled.
- Global tokens: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`. Report all13 rows. Decode retention uses T4–512; T1/2 and each prefill row remain separately visible.
- Three public-forward warmups; 100 cold-L2 CUDA-graph CUPTI activity-span samples per row. Aggregate ranks with MAX for each iteration, then take the untrimmed median. EP4 is primary; report EP8 separately as a guard.
- The span includes runtime alpha copies, staging, communication, expert compute and output handling. Routing, weight preparation, compilation, tuning, graph capture and L2 flushing are excluded.
- Fresh native eight-candidate AUTO for every arm/topology, with new tactic/compiler/driver/Triton caches. Its hot CUDA-event scores select the tactic and are separate from final cold-CUPTI samples. Retuning means comparisons measure each cache policy with native AUTO selection; differing winners prevent attributing the entire change to the hint alone.
- **Explicit user override: run the baseline once per EP4/EP8 and reuse those exact raw samples for every candidate. No ABBA or baseline refresh.** The comparison retains temporal-drift uncertainty.
- **Explicit user override: skip all correctness tests, independent references and repeated-output checks for these cache-hint-only changes.** Input/weight fixture hashes, timing-record checks and static scope audits are provenance checks, not numerical correctness evidence.

The native cold-L2 timer zeros a local allocation sized at twice the device-reported L2 capacity. This preserves the PR11 method; it does **not** establish that SysL2 or peer-cached lines are cold. A benchmark speedup alone does not demonstrate SysL2 hits. The independent diagnostic is documented in [experiments/PEER_TMA_PROBE.md](experiments/PEER_TMA_PROBE.md); its smoke/profiler results must remain separate from native MegaMoE timing.

Within-run inspection also limits small performance claims. The largest sample is sample 0 in every completed row; the official metric retains it. EP4 8K medians decrease chronologically from baseline 1523.60 to NORMAL 1482.06, LAST 1469.55 and local-pool LAST 1449.60 µs, all with the same tactic. Their first-25 medians are almost identical (1345.58, 1347.85, 1346.54 and 1344.46 µs), while each row rises approximately 15–17% from its first to last quarter. Local-pool LAST's official 8K ratio is 1.0510×, but first/last-quarter ratios are 1.0008×/0.9976× and first/last-half ratios are 1.0074×/1.0064×. These are descriptive diagnostics, not alternative scores: the official 100-sample untrimmed median remains unchanged. The apparent median gain is sensitive to where that within-run rise occurs and does not establish a causal cache-hint improvement. Clocks and power were not sampled per iteration.

[benchmark-contract.json](benchmark-contract.json) is the machine-readable contract. Native timing uniformly uses `CUTE_DSL_KEEP=ptx,cubin`, disables `MEGA_USE_NCU` and unsets IKET compiler options. Retained generated code supports later hint inspection; this does not add profiler work to the measured span.

## Launch and summarize

The following commands run **on the prepared devbox**, after the sources and helpers have been transferred. The baseline command is a one-time launch record: do not rerun it once its output is reserved. `run_campaign.py` refuses existing per-EP state/log/cache paths and uses a shared campaign lock plus an idle-GPU preflight.

```bash
cd /workspace/hashinfer-sysl2-0930

# Once only: EP4, then EP8; detached process records its PID and logs.
venv/bin/python run_campaign.py \
  --arm baseline --source /workspace/hashinfer-sysl2-0930/sources/baseline \
  --ep both --detach

# Once only: wait for that baseline, then run the three candidates serially.
# Stops on any failed baseline/candidate; never retries the baseline.
venv/bin/python continue_campaign.py --detach
```

The continuation runs `dispatch-normal`, `dispatch-last`, then `local-pool-last`, each EP4→EP8, and creates `summary-v1` after all arms complete. Its equivalent single-arm launch is:

```bash
venv/bin/python run_campaign.py \
  --arm dispatch-normal \
  --source /workspace/hashinfer-sysl2-0930/sources/dispatch-normal --ep both
```

Use that manual form only when no continuation owns the queue and the arm has no reserved output. Failed attempts are preserved; inspect the failure before creating any separately named retry. Do not delete a completed baseline to bypass the once-only rule.

The actual recovery launch after the original normal arm's CUPTI teardown failure was:

```bash
venv/bin/python run_campaign.py \
  --arm dispatch-normal-r1 \
  --source /workspace/hashinfer-sysl2-0930/sources/dispatch-normal --ep both --detach
venv/bin/python continue_after_retry.py --detach
python3 profile_after_campaign.py --detach \
  --upstream-state continuation-v2-state.json --receipt-prefix peer-profile-v2
```

The recovery continuation waits for the unchanged normal retry, then serializes LAST EP4/EP8 and local-pool LAST EP4/EP8. It creates `summary-v1` using `dispatch-normal-r1`, without mixing the failed partial arm. The profiler acquires the same GPU lock after the continuation completes.

The continuation summarizes automatically. To generate a later read-only report from completed evidence, choose a **new** output directory:

```bash
venv/bin/python summarize_campaign.py \
  --baseline baseline --arms dispatch-normal-r1 dispatch-last local-pool-last \
  --ep both --output /workspace/hashinfer-sysl2-0930/summary-v2
```

This checks complete exit receipts, source closure, same node/boot/GPU identity, matching input/weight fixtures, 13 rows,100 finite positive samples per row, and agreement among rank winners. It reports baseline/candidate median ratios, separate EP decode geometric means, all row medians, tactics and raw samples. There is no output-correctness gate.

For a later authorized candidate, retain `results/baseline` and choose a new arm label and output directory. Reuse the existing environment and exact benchmark contract; `summarize_campaign.py` will reject a different node/boot/GPU identity or different fixtures. A new run label for unchanged source requires an explicit `--arm-source NEW_LABEL=CANONICAL_SOURCE` mapping in `audit_candidate_provenance.py`. Changing the source baseline or runtime would require a new comparison campaign rather than silently treating the frozen samples as a matched control. Do not execute the one-time baseline command again.

## Evidence locations

All remote paths below are under `/workspace/hashinfer-sysl2-0930` and are copied into the owning local effort when collected.

| Path | Contents |
|---|---|
| `results/ARM/ep4.log`, `ep8.log` | Complete native stdout/stderr, fixtures, AUTO winners, every timing sample |
| `results/ARM/ep4.state.json`, `ep8.state.json` | Atomic status, child exit, command, source/helper hashes, node/boot/GPU closure |
| `results/ARM/ep4.validated.json`, `ep8.validated.json` | Strictly parsed raw timing/fixture/tactic records and log digest |
| `results/ARM/ep4/`, `ep8/` | Separate compilation/tactic/driver/Triton caches and generated artifacts |
| `results/baseline/launch-epboth.json`, `driver-epboth.log` | Detached baseline launch receipt and orchestration log |
| `results/continuation-state.json`, `continuation.log` | Serialized candidate queue state and log |
| `summary-v1/{summary.md,summary.json,raw-evidence.json}` | Generated report and complete paired evidence after completion |
| `results/environment.json`, `environment-freeze.txt` | Actual runtime inventory |

The deployed baseline runner is preserved locally as `run_campaign.deployed.py`; each state records the actual driver hash. Keep raw logs, failed attempts, patches, source exports and helper scripts. The measured ratios and retention decision above use only successful completed runs.
