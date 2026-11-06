# EP4 baseline profiling findings

The useful result is a precise inventory of waiting instructions and resource
usage. It does **not** establish a new bandwidth/IPC bottleneck or justify
removing a barrier. The queued static-epi scheduling experiment is reasonable;
its before/after benchmark must decide retention. This T256 epi-return capture
cannot evaluate the dispatch-return publication tactic directly.

## Evidence and execution boundary

Frozen HashInfer `7e6e977f4788f91eaf5988fd4ffea93fc4f1eed5`, EP4 on four B300s,
H7168/I2048/E256/K8, O3, deterministic combine, routing weights in FC2. T256
uses N64/epi return, G512/S2/F4, atomic-counter scheduling; T4096 uses
N128/dispatch return with the same remaining knobs. Fixtures and outputs match
the original complete native EP4 baseline. `MEGA_USE_NCU=0` preserves production
barriers. The helpers and exact tool/environment versions are in README.md.

- Both accepted software-trace nsys captures contain five MegaMoE launches on
  each of four ranks and no standalone staging/combine kernel. Surrounding L2
  flush and NCCL rendezvous are intentionally captured. Generic boundary
  warnings remain recorded; the expected Mega launch counts are complete.
- Full NCU T256 executed40 application-replay epochs on each rank, then emitted
  four readable reports. All profiler parents subsequently hung without GPU
  processes or CPU progress. After read-only imports with unchanged hashes,
  only the recorded profiler groups were terminated. Launcher exit1 and forced
  teardown are preserved, including one group requiring KILL after TERM.
- `ncu-t256-audit.json` independently verifies all4079 collected file hashes,
  all160 rank/epoch records, source/tactic/input/weight pins and73,400,320 BF16
  output element checks. Saved tensor storage bytes are finite and match the
  baseline SHA256 on every rank/epoch. One selected CUBIN hash occurs throughout:
  `ff60db6d3f6c755437e70b61a8a1c3aaf3cd2893d7d3c0b6f0a2bf47c52b6a49`.
  The successful artifact audit is separate from the failed profiler teardown.
- The compact36.8MB archive preserves4079 original paths/hashes using394 unique
  files. Hu9 was handed back to the benchmark owner with empty GPU/process state
  and a read-only clock/power receipt. No settings were changed. No sanitizer or
  second full T4096 capture was run.

## Counter availability and limitations

`--set full` was requested. Raw reports have2418 columns on rank0 and2468 on
ranks1–3; the all-details export has23/29/28/28 nonempty section labels, including
aliases and rule sections. Rank0 lacks50 columns present on other ranks,
including several elapsed-cycle and warp-latency ratios. Each report has15
empty/NA fields:13 triage metrics, the unused start/stop range and
`launch__kernel_name` (the separate Kernel Name is present). Six requested CTC
NVLink byte/rate/peak counters are unavailable according to the driver log.
Missing counters are not zeros and full-set selection does not guarantee their
availability.

| Device rank | NCU duration (ms) | Reported active warps (%) | PC samples |
|---:|---:|---:|---:|
|0|15.007936|215.368052|91770|
|1|0.316704|0.548347|674941|
|2|2.004448|1.082990|233559|
|3|32.827968|31.328160|21466|

Rank0's active-warp percentage and rank2's453.565985% reported SM throughput are
physically implausible. Replay durations and rank sample counts also differ
substantially. These ratios cannot establish production occupancy, IPC,
bandwidth saturation or the amount of overlap available. NCU records zero
sampling overflow/dropped data, interval4096cycles and two aggregated sampling
passes; the one-pass CLI cap does not mean one aggregate pass. Source-correlated
long-scoreboard sample totals are below raw totals by17/8/17/10 samples; retain
that small unmatched remainder rather than forcing equality.

## Resource facts

Both selected launches use640threads and an initial96registers/thread. The
fixed role redistribution and one-CTA-per-SM design remain intact. T256 has
200064 dynamic shared bytes; T4096 has230784. The T256 NCU shared allocation is
201088bytes, equal to dynamic shared memory plus the cubin's1024 static bytes.
The nsys static field itself reports0, so it should not replace the cubin total.

The selected cubin reports STACK0/LOCAL0, and all four NCU devices report zero
local-memory requests and executed spill instructions. Launch `stack_size=1632`
is metadata, not evidence of a1632-byte spill frame. There is no measured spill
problem to justify a new register redistribution or removing a warpgroup.

## Waiting instruction regions

Offsets are relative to the kernel's first SASS instruction. Full source/SASS
exports and neighboring instructions are preserved in
`ncu-t256-source-inventory.json`. Every one of5176 SASS PCs has line metadata,
but some inherited transport methods point to a synthetic owned-file path with
out-of-range line numbers and cannot be opened. Other locations are coarse,
such as the kernel decorator. The mappings below use the actual instructions,
barrier IDs and the pinned source, not those synthetic paths alone.

- **Scheduler publication:** ranks0–2 place66.6–75.2% of their correlated
  long-scoreboard samples at `0x13f80` and `0x12e70`. Both are predicated
  `NANOSLEEP.SYNCS`, immediately after a phase check on the scheduler mbarrier
  at shared offset`0xd0`. The imported location is the shared
  `MoEWorkTileInfo.read_from_smem` path in `moe_persistent_scheduler.py:187`, whose
  `pipe.consumer_wait(state)` precedes reading the published work. These are
  scheduler-consumer waits, **not ordinary global-load or weight-cache misses**.
  They do not distinguish the initial dispatch dependency from repeated
  atomic-counter claim overhead. Static assignment can remove the latter but
  cannot remove the former.
- **Initial transport publication:** PC`0xabc0` follows
  `BAR.SYNC.DEFER_BLOCKING 0xa,0x80`, and accounts for55.0/71.7/66.8% of barrier
  samples on ranks0/1/2. PC`0xfd0` follows the dispatch-to-scheduler
  `BAR.SYNC 0x9,0xa0`, contributing18.5/24.1/22.4%. Shared transport assigns
  barrier10 to its four dispatch warps and barrier9 to dispatch plus scheduler
  (`src/src/token_comm.py:364-366,570-576,1612-1616`). The owned kernel waits at
  `megamoe_kernel.py:1184`. Publication/startup waits are visible; this does not
  quantify a removable critical interval. Earlier startup experiments should
  not be repeated solely because these required barriers collect samples.
- **Whole-CTA tail handoffs:** `0x10bd0` follows `BAR.SYNC 0x8,0x280` at`0x10bb0`;
  `0x11460` follows another at`0x11430`. These are the owned tail handoffs around
  drain and final combine (`megamoe_kernel.py:1494-1522`). They dominate rank3's
  barrier samples (79.0% and16.2%), while ranks0–2 emphasize earlier publication.
  The replay has no internal phase timing; this rank skew does not prove the
  final drain is the production bottleneck or permit deleting either handoff.
- Rank3 instead has substantial long-scoreboard samples at accumulator/raw
  readiness waits (for example`0x12ed0`, `0x66e0`, `0xe830`). Decode-commit and
  weight-unpack PCs appear in short-scoreboard samples, but no new instruction
  optimization opportunity is established. Release-counter fence samples are
  small in absolute count and provide no reason to weaken correctness fences.

## Next experiment priority

Keep the existing-knob static-epi experiment first. The profile confirms that
scheduler consumers wait, and its implementation removes a specific claim/
cluster-broadcast sequence without changing arithmetic or role ownership. It
does not prove that those claims cause the observed waits; the clean paired
benchmark and numerical gate remain decisive.

The dispatch-only `(1,1)` epilogue publication tactic remains a valid separate
source-based hypothesis, because it can shorten whole-expert readiness delay.
This N64 epi-return capture does not measure that path. T4096's nsys trace
establishes the fused launch/resource contract but not internal readiness timing.
There is no profiler evidence here to prioritize broader register, dequant
instruction, stage-depth or barrier-removal changes above those bounded trials.
