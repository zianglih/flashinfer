# Peer TMA residency experiment

`peer_tma_cache_probe.py` isolates the same descriptor-free
`cp.async.bulk.shared::cluster.global.mbarrier::complete_tx::bytes.L2::cache_hint`
used by MegaMoE's peer pulls. It uses two NVSHMEM ranks and an immutable int32
buffer, times rank 0 reading rank 1, and varies first/normal/last eviction hints.
One thread per CTA issues and waits for each tile. A checksum consumes one word
per transfer; this is a probe validity check, not a MegaMoE correctness suite.
It measures repeated-read latency and residency, not peak NVLink bandwidth.

The helper loads `shim/comm.py` and `src/src/bootstrap.py` directly from the
provided `--repo`, bypassing HashInfer package initialization. It reuses their
NVSHMEM bootstrap, symmetric allocation and peer offset computation. No source
repository files are patched. The PTX wrapper is local to this experiment.

## Smoke and sweep

Run from the experiment's parent directory with the campaign's installed
CuTe DSL, PyTorch, cuda-python and nvshmem4py environment:

```sh
CUDA_VISIBLE_DEVICES=0,1 torchrun --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29630 --nproc-per-node=2 \
  experiments/peer_tma_cache_probe.py --repo ./hashinfer \
  --sizes 64k --policies first,normal,last --prepare owner,requester \
  --repeats 2 --samples 1 --output results/peer_tma_smoke.jsonl

CUDA_VISIBLE_DEVICES=0,1 torchrun --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29630 --nproc-per-node=2 \
  experiments/peer_tma_cache_probe.py --repo ./hashinfer \
  --sizes 64k,1m,16m,256m --policies first,normal,last \
  --prepare owner,requester --repeats 16 --samples 3 \
  --output results/peer_tma_sweep.jsonl
```

Each working set must be divisible by `--tile-bytes * --blocks`. The default
tile is 4096 bytes. For MegaMoE's exact token size, supply its byte count and
matching working sets in raw bytes. `--blocks 1` isolates serial reuse; a wider
CTA grid can be an additional run, with the same total logical bytes.

`owner` first scans the buffer locally on rank 1 using the normal TMA policy.
`requester` first scans it through the peer pointer using the measured policy.
`none` skips explicit preparation and is **not a cold-cache condition**: initial
fill and previous cases may already have warmed caches. Both ranks rendezvous
using CPU/Gloo barriers outside the timed and NVTX-marked regions. All warm
operations and policy compilation are outside those regions.
The explicit loopback rendezvous avoids hostname-resolution failures observed
with `--standalone` in the campaign container. Run these commands sequentially
so their rendezvous port is free.

## Counter discovery and one profiling case

```sh
python experiments/query_peer_metrics.py --out-dir results/peer_metrics
```

Review `peer_metric_candidates.json` and `peer_metrics.txt`. The query saves the
complete metric inventory and selects existing SysL2 peer hit/miss or sector
counters plus NVLink response/data bytes; names differ by GPU and NCU version.
For a compact case after the smoke succeeds:

```sh
CUDA_VISIBLE_DEVICES=0,1 ncu --target-processes all \
  --nvtx --nvtx-include 'peer_tma_measure/' \
  --kernel-name regex:peer_tma_kernel --launch-count 1 \
  --cache-control none --clock-control none --replay-mode application \
  --metrics "$(cat results/peer_metrics/peer_metrics.txt)" \
  --csv --page raw --log-file results/peer_tma_ncu_%p.csv \
  torchrun --nnodes=1 --master-addr=127.0.0.1 \
  --master-port=29630 --nproc-per-node=2 \
  experiments/peer_tma_cache_probe.py --repo ./hashinfer \
  --sizes 64k --policies normal --prepare owner --repeats 64 --samples 1 \
  --output results/peer_tma_profile.jsonl
```

Only rank 0 pushes `peer_tma_measure`; owner preparation kernels are excluded.
The measured kernel has no cross-rank barriers, writes only requester output,
and reads immutable peer memory. Use application replay: kernel replay failed
with `ContextSaveFailed` while NCU tried to save accessible NVSHMEM memory.
Application replay reruns the whole two-rank program for metric collection
passes, including symmetric allocation, initialization, compilation/local
launch warmup, and owner preparation. Compilation/launch warmup uses a separate
local buffer; owner preparation reads the measured source locally on rank 1.
`--cache-control none` preserves the application's preparation within each
pass. Do not assume requester cache warming accumulates across application
passes: each invocation recreates its allocation and preparation. Compare arms
with the same replay and preparation settings; these remain prepared-cache,
not cold-cache, measurements. See the [NCU replay documentation](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#replay).

Run the same case with `--repeats 1` and `--repeats 64`. For 64 KiB, their logical
read amounts are 64 KiB and 4 MiB. If requester caching serves the extra passes,
requester NVLink response data should grow much less than 64x and SysL2 hits
should corroborate it. If response traffic scales with requested bytes while
latency improves after owner warming, that supports owner-side L2 reuse. Packet
byte counters can include protocol overhead; identify whether the chosen
counter measures response payload or whole packets before comparing bytes.

Do not infer owner HBM/L2 traffic from rank-0 DRAM counters: they observe the
requester's GPU. Owner counters need a separate device-wide sampling experiment.
No explicit eviction/cold-cache claim, coherence experiment, or SysL2 capacity
claim is made by this helper. The immutable source avoids synchronization and
staleness questions; the result applies to the exact recorded hardware/driver.

## Bounded six-arm profiling cohort

After the native timing cohort is idle, NCU 2026.1.1 can profile the confirmed
counter set directly:

```sh
python experiments/run_peer_profiles.py --repo ./hashinfer \
  --out-dir results/peer_profiles --gpus 0,1 --timeout 180
```

This runs first/normal/last crossed with one or 64 complete passes over 64 KiB,
with owner preparation and one measured sample per arm. Every arm has its own
command, launcher log, CSV metrics, NCU report, probe JSONL and parsed metric
records. The top-level manifest records completion and fails fast if an arm
times out, exits nonzero or omits requested counters. A timeout terminates the
entire NCU/torchrun process group. Existing results are protected by requiring
a fresh output directory. Add `--dry-run` to save commands without launching.

The only profiled range is requester rank 0's `peer_tma_measure/`. Application
replay relaunches both ranks for each collection pass; rank 1 waits on the host
while rank 0 executes the measured kernel. NVSHMEM/distributed bootstrap and all
preparation kernels are outside the NVTX range but run again in each application
invocation. Cache flushing and clock control are disabled. Use raw counters
for this cohort; CUDA-event timings under NCU are not native timing evidence.
The selected counters include total peer requests and
first/normal/last request totals, their lookup hit/miss counts, and requester
NVLink RX/TX user-response payload bytes. Requests not accounted for by lookup
hit/miss must not automatically be labeled misses; retain the raw totals and
use NVLink byte scaling to evaluate whether remote transfers were eliminated.
These SysL2 counters count requests, not sectors. Retain signed residuals such
as total minus hit minus miss without clamping or treating them as proven
bypass counts. Metrics can be collected in different application passes, and
their arithmetic also depends on counter definitions and reproducibility of
the recreated workload. Do not divide exported counter values by the number
of replay passes.

Each invocation opens `probe.jsonl` with write mode, so that file retains only
the last invocation's metadata, sample and summary. The runner's `launcher.log`
captures stdout/stderr across the entire NCU invocation and retains the JSONL
records printed by every application pass. Inspect that log when checking
sentinels and setup consistency across passes. NCU CSV/report files hold the
collected metric results; preserve their raw counts, units and replay-pass
evidence. `summarize_peer_profiles.py` reads both long and wide NCU CSV layouts,
including the aligned units row in wide output. Its JSON output retains the
last-pass `probe.jsonl` under `raw_probe_records` and every JSONL record found
in `launcher.log` under `launcher_probe_records`, with source line numbers.

The campaign preserves its failed attempts separately: `peer_profiles-v1` and
`peer_profiles-v2` failed during hostname-based rendezvous before the measured
kernel; `peer_profiles-v3` failed during kernel-replay context saving. The
application-replay cohort uses `peer_profiles-v4`. Receipt `peer-profile-v5`
completed its first arm, but the launcher's long-CSV-only parser incorrectly
rejected the valid wide report. Receipt `peer-profile-v6` resumes that cohort
after adding wide-CSV parsing, reusing the first arm's report and preserving
the earlier manifest. The v1/v2/v3 failures supply no caching or performance
conclusion; the v4 cohort is only complete when its manifest confirms all six
arms.
