# FC2 TMEM overlap audit

Frozen host/source7829fc00. Candidate control is the exact padded STSM snapshot
from ../bulk_r2s_experiment; no production edits. GPU2/GPU5 on c1 B200, image
nvcr.io/nvidia/pytorch:26.05-py3, CUDA13.2, CuTe4.7.1. Only bounded phase
probes and paired exact comparisons; no primary baseline rerun.

## Existing baseline contract

Read-only a65 FC2 source preserves original TMEM partial-overlap protocol:
accumulator windows [0,256) and [256-SFcols,512-SFcols), SF disjoint above
those windows. Producer phase^1 and consumer phase select matching windows.
Alternating epilogue direction drains the overlap region first, fences the
TMEM loads, then releases the one-stage accumulator barrier before the rest
of the epilogue. Current7829 N256 uses one fixed accumulator and releases
only after its full bulk output drain.

A65 gives each CTA128 tokens×256 channels, issuing512-byte bulk rows;
current transposed two-CTA geometry gives each CTA256 tokens×128 channels,
issuing twice as many256-byte row copies. M256 is the supported group-2
MMA shape: its fixed128 TMEM rows per CTA cannot simply become256 channels
without repeating the M instruction tile. DSM staging would need additional
cross-CTA data movement and synchronization; not prototyped before checking
accumulator serialization.

## Current padded-STSM profile

One native NVFP4 T16384 M256N256/two-CTA call profiled with NCU LaunchStats,
Occupancy, SpeedOfLight, WarpStateStats, SourceCounters, MemoryWorkloadAnalysis.
Native input creation and full-byte exact comparison occur before profiling.
The18 replay passes are diagnostic; no new benchmark baseline is recorded.

Profile184.64us, tensor active31.90%, DRAM2.618TB/s (~34.13%peak), registers126,
SMEM229888 bytes. Long-scoreboard samples total7141: loader AB-empty wait3608,
epilogue acc-full wait2130, other MMA-stage waits361/223. Shared-store stalls
are small after padding. Bulk row instructions compile to warp-uniform UBLKCP
loops over the active per-lane row addresses. Detailed per-PC counts are in
stmatrixpad-source.csv and profile-summary.json.

## Isolated overlap prototype

For FC2 N256 with the existing bulk-output capability, use windows [0,256)
and [192,448), with SFA[448,464), SFB[464,496). This keeps32-column aligned
window addresses and512-column allocation. The64-column overlap is read
first: reverse token slabs for phase0, forward slabs for phase1. After64
columns have been read (or are known invalid), execute the TMEM-load fence
and the single accumulator consumer release. Output commits/drains and
per-tile synchronization remain unchanged; the consumer state advances
only after the epilogue returns. Both CTAs release, including an inactive
channel-tail CTA that has no TMEM output reads. One accumulator barrier
stage prevents the producer from advancing two tiles ahead.

Smaller N, unsupported output modes and insufficient bulk-scratch cases
retain their original ownership. Operand stages, input layouts, dynamic N,
final-scale rounding, output scatter, and API stay unchanged. Metadata
register indices and slab order are constexpr; two runtime phase branches
instantiate explicit forward/reverse paths.

The first sync exceeded shell argument length because the source CSV was
included in the payload; the attempted probe therefore exited before GPU
execution with a missing script. Sync now excludes CSV and read-only a65
source. Successful GPU runs use the -v2 suffix. Preserve these failures as
harness evidence, not kernel failures.


## Selected variant and exact checks

`overlap_early` releases immediately after the last TMEM load of the overlap
region, before conversion, matrix stores or bulk output issue. Each live
slab has exactly one such release; a skipped slab releases through its
explicit invalid-row branch. The initial `overlap` variant released after
that slab's output commit and is preserved as an intermediate control.

Both variants pass98 paired exact cases:50 output/metadata contract cases,
24 six-format partial-route cases, and24 M384 channel-tail cases including
untouched output rows and a trailing sentinel. Coverage includes N16/32/64/
128/256; BF16/F16/F32/E4M3/E5M2 outputs; FP32/BF16/F16 metadata; per-token
scaling on/off; NVFP4, FP4/E8M0/SF16, MXFP4/SF32, MXFP8 E4M3/E5M2, mixed
W4A8. Every timed native call also passes a complete output-byte comparison.
No broad correctness or sanitizer campaign was run.

## Native fixed-tactic FC2 medians

Actual DeepSeek T16384 routing, H7168/I2048,256 global/32 local experts,
topk8, unfused finalize; per-tensor NVFP4.10 warmups/100 cold-L2 CUDA-graph
CUPTI samples, fallback fatal. Each process reuses captured native FC2 inputs
and the same preallocated output. Values are microseconds. The control is
padded STSM on frozen7829, not the original upstream baseline.

| Mode | Geometry | Order | Control | Initial overlap | Selected early release |
| --- | --- | --- | ---: | ---: | ---: |
| NVFP4 | M256 N256,2 CTA | forward | 177.649 | 138.368 | — |
| NVFP4 | M256 N256,2 CTA | reverse | 178.096 | 138.336 | — |
| NVFP4 | M128 N256,1 CTA | forward | 191.777 | 169.760 | — |
| MXFP8 | M256 N256,2 CTA | forward | 254.0005 | 212.0325 | — |
| Mixed W4A8 | M256 N256,2 CTA | forward | 242.720 | 198.944 | — |
| NVFP4 | M256 N256,2 CTA | forward | 177.600 | 138.2405 | 135.265 |
| NVFP4 | M256 N256,2 CTA | reverse | 177.776 | — | 134.560 |
| MXFP8 | M256 N256,2 CTA | forward | 253.985 | — | 199.536 |
| Mixed W4A8 | M256 N256,2 CTA | forward | 242.576 | — | 186.224 |

Selected two-CTA phase latency decreases23.8–24.3% for NVFP4,21.4% for MXFP8,
and23.2% for mixed W4A8. The initial one-CTA variant also improves11.5%; the
selected earlier release has exact one-CTA coverage but no separate one-CTA
native timing in this bounded run. No full-MoE speedup is inferred from the
phase numbers; AUTO may select N128, whose existing two-bank policy remains.

Small-token NVFP4 fixed M256N256/two-CTA native medians, all full-byte exact:

| Tokens | Control | Selected early release |
| ---: | ---: | ---: |
| 1 | 9.4395 | 9.376 |
| 2 | 13.808 | 13.440 |
| 4 | 18.592 | 18.128 |
| 16 | 28.512 | 27.5685 |
| 64 | 53.888 | 52.976 |
| 128 | 56.6725 | 55.4085 |
| 512 | 61.328 | 59.1045 |

These are diagnostic fixed-tactic checks;1/2 tokens remain excluded from
full-benchmark retention decisions. No primary baseline was rerun.

## Integration handoff and reproduction

Selected snapshots:
- `chain_trial/overlap_early_core.py`: SHA256
  `29157f7b206e6adaab7d55d9def23f3303fccfa2c7df1aa5625e2c3e41d5045a`.
- `chain_trial/overlap_early_utils.py`: SHA256
  `e7b2cfaacf11f43763f315b624b73d11f7fcad2a870c50a033350e06f81d676a`.

`overlap-early-on-285bae77.patch` and `integration/` target the parent's local
285bae770c688328f0da82660c307a5be7417375 checkpoint. They preserve its wider-K
FC1 and stage-policy changes. The overlap capability additionally asserts
SF footprint≤64 before using the fixed windows; all currently eligible FC2
configurations have48 SF columns. The parent owns applying, committing and
combined AUTO benchmarking. Experiment modules and raw evidence remain
immutable independently of integration formatting.

From the frozen remote checkout with task-local scripts synced:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
CUDA_VISIBLE_DEVICES=2 OMP_NUM_THREADS=1 PYTHONPATH=. ../.venv/bin/python \
  ../scripts/fc2_chain_audit/probe_native.py \
  --repo . --expected-head 7829fc00dc7121341cc40cd4190660507e006490 \
  --output ../logs/fc2-chain/new-native-pair.json --tokens 16384 \
  --tactic '[256,[[256,256],[2,1],false],[[256,256],[2,1],false]]' \
  --variants baseline,overlap_early --phase fc2
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python \
  ../scripts/fc2_chain_audit/run_paired.py \
  --variant overlap_early --script probe_fc2_tail_formats.py
```

Use `probe_native_modes.py --mode mxfp8` or `--mode w4a8` for other native
formats, preserving the fixed tactic/timing flags. `collect.py` archives
raw100-sample arrays, source hashes, exact logs, generated PTX/CUBIN and
resource usage plus the padded-control NCU report and SASS source counters.
