# M128/N64 two-group pre-launch source review

Reviewed candidate kernel SHA256
`5ea9b59f882cef50e6da6c915295acaa626b92331f4fb592c0744b47628de866`,
its frontend/epilogue, the separate three-decoded-stage patch and the installed
DSL 4.7.1 pipeline implementations. No source-level correction was identified
before the first numerical launch. This is a source audit; GPU progress and
numerics remain the required gate. No active source or GPU state was changed.

- **Physical CTA versus instruction group:** kernel lines 902–910 derive V
  from the actual MMA. M128 is V1 with physical cluster shape (2,1), so both
  CTAs issue MMA. Each owns 128 output features; the cluster still covers 256.
  Weight and scale task lines 758–788 use `tile_m_idx // V` and slice `bidx % V`,
  avoiding duplicate weights in the second CTA.
- **Raw and decoded rings:** raw `PipelineTmaAsync` lines 926–937 expects eight
  consumer-warp arrivals. Its installed thread selector uses lane modulo 32
  and only partners sharing V/M coordinates for `(1,0)` multicast; each M128
  CTA releases its own raw stage. Transform `PipelineAsyncUmma` lines 939–948
  expects 256 producer-thread arrivals at V1, and its installed V1 branch uses
  no remote producer/consumer mask. Both decode groups split the same K tile
  and follow identical stage/phase progress, so one group cannot publish a full
  decoded stage before the other group contributes.
- **Activation multicast:** lines 828–869 omit the nonleader N shift for V1,
  partition B across cluster-M and use its matching multicast mask. Both
  physical CTAs consume the full routed N64 tile. The transaction threshold
  is 32768 BF16 bytes per stage, not multiplied by the physical cluster size.
  `PipelineTmaUmma` lines 949–960 has two UMMA consumer arrivals; its installed
  release mask sends each CTA's one-CTA completion to both multicast partners.
  This matches local W4A16 kernel lines 928–938. It is distinct from M256 V2,
  where B is split by dynamic-N and only the instruction-group leader issues.
- **Accumulator and allocation:** lines 961–982 expect 128 epilogue consumer
  threads per V1 CTA and use one-CTA TMEM allocation. The installed accumulator
  pipeline's V1 consumer mask is local. Exactly 416 threads wait/retrieve TMEM:
  epilogue128 + MMA32 + decode256. Scheduler consumption remains 480 threads
  per CTA and the kernel-tail count remains640; neither uses V as a multiplier.
  Allocation/free remain512 columns. N64 accumulator stages occupy0–63 and
  64–127, decoded stages128–255 and256–383. The computed MMA A pointer at
  lines1209–1215 agrees with the transform helper and epilogue pitch.
- **Odd token tails:** dynamic BF16 MMA rounds positive valid N up to16, with
  a minimum issued width16 and a maximum64. Both epilogues use a full64-column
  stage as scratch; their second32-column half stays within that stage even
  when fewer tokens are valid. Invalid loaded values have no reductions into
  valid tokens. FC1 stores predicate `token_in_tile < valid_tokens` and output
  feature bounds at epilogue lines396–402. The inherited FC2 router predicates
  both token and hidden coordinates before metadata loads or output stores
  (`epilogue_refactor.py:2358–2398`, `2421–2455`). No stale padded metadata is
  consumed for invalid rows. The overlap-accumulator path stays disabled, so
  N64's single64-token subtile does not enter the parent's two-subtile preload.
- **Counter tails:** FC1 done counts only in-bound64-feature down-projection
  blocks (`epilogue_refactor.py:1323–1343`), agreeing with `ceil(I/64)` at kernel
  lines911–912. The partially padded physical CTA must still run its pipeline,
  but contributes no FC1 done signal. FC2 dispatch-return signals every feature
  CTA, including padded ones (`epilogue_refactor.py:1995–2010`); constructor
  lines171–179 computes `ceil(H/256)*2`. `token_comm.py:1319–1335` multiplies it
  by `ceil(expert_tokens/64)`. Do not apply the FC1 in-bound rule to FC2. The
  epilogue-warp return path instead routes directly and has no FC2-done publish.
  Epilogue phase-aware flag flushing and final tail flush remain unchanged.

`installed-pipeline-reference.txt` contains the read-only inspected library
source, including the V1 mask branches and full/empty arrival types. Named
source references above are to the candidate's preserved `proposed/` snapshot
and unchanged vendor/local files, so later active-source changes do not alter
this audit's basis.

The separate `w4a16_n64_transform3` patch changes only the decoded ring to3.
All six coupled sites are updated: mixed layout/column count, six barrier
slots, actual-storage fitter, transform pipeline, producer state and MMA A
consumer state. Activation and accumulator state remain2 and independent.
Installed `PipelineState.reset_count()` does not change index/phase; `advance`
compares against `stages`, so no power-of-two assumption applies. K28 then K8
starts the next decoded consumer state at (index1,phase1) then(index0,phase0).
Both FC1/FC2 transform helpers preserve returned states; the MMA loop also
preserves its index/phase. Final producer tail walks `self.num_stages`, including
unused initial slots correctly. It stays outside the persistent work loop.

For a warmup hang, map the **new binary's own PCs** to these stages; do not reuse
numeric PCs from the M256/N128 profile. Source lines identify the caller, while
the generated slow wait may carry a nearby optimized line. At raw5, the shared
barrier byte offsets relative to `SharedStorage` are:

| Role / wait | Consumer or producer | Two decoded stages full / empty | Three decoded stages full / empty |
|---|---|---|---|
| Raw A+SF | weight warp5 / decode warps12–19 | 0x00 /0x28 | 0x00 /0x28 |
| Decoded A | decode warps12–19 / MMA warp4 | 0x50 /0x60 | 0x50 /0x68 |
| BF16 B | activation warp6 / MMA warp4 | 0x70 /0x80 | 0x80 /0x90 |
| FP32 accumulator | MMA warp4 / epilogue warps0–3 | 0x90 /0xa0 | 0xa0 /0xb0 |

Offsets are derived from consecutive Int64 full/empty arrays. For another raw
depth R and decoded depth D: transform-full=16R, transform-empty=16R+8D,
activation-full=16R+16D, activation-empty=16R+16D+16,
acc-full=16R+16D+32, acc-empty=16R+16D+48. Confirm the actual emitted shared
base before inspecting memory.

- Stuck raw-ready: check weight TMA full tx=18432 bytes and all eight decode
  warp raw-release arrivals; producer wait caller kernel794.
- Stuck decoded-ready: check both groups committed all256 V1 arrivals and
  group-local128-thread layouts; MMA caller1239, local helper commit547.
- Stuck free decoded stage: inspect MMA activation wait and downstream acc
  ownership first; local helper producer wait488 is also a legitimate
  backpressure location. Stage3 requires the new full/empty offsets above.
- Stuck activation-ready: check V1 B tx32768 bytes, multicast mask, both MMA
  consumers and matching stage phase; kernel860/1240. If the activation warp
  instead waits at kernel1104, inspect the FC1 global done count and flag flush.
- Stuck accumulator-ready/free: inspect both physical CTA MMAs for M128,
  their independent128-thread epilogue releases and fixed64-column pitch;
  kernel1236/1254, FC1 epilogue295/313 or inherited FC2 wait/release.
- Stuck after useful work: distinguish raw/activation/transform/acc producer
  tails (kernel1079/1125/1207/1257), TMEM retrieve/free, scheduler terminal
  work publication, and dispatch-return global FC2-done wait. A hang only
  with `reuse_dispatch_warps` makes the padded-CTA completion formula and
  final release-tracker flush especially relevant.

Use the existing odd-token/K-tail/ring-wrap cases for both return modes. A
small K1/K2 sequence crossing several FC1/FC2 work boundaries is valuable for
stage3 because it exercises unused slots and phase wrap separately from the
DSV3 K28/K8 workload. Empty/refill graph replay remains a necessary GPU check.
