# One operand empty ring — 2026-10-26

Independent unstaged source `../../flashinfer-shared-empty-20261026`, based on
`0def601d6603df828ea39679b41ccbce64f7f09e`. Two files change: the SM100 split
blockscaled core and its private pipeline helper. Production is untouched.

## Ownership contract

The TMA pipeline owns the only operand empty ring. Narrow SF loading keeps its
own 128-arrival local cp.async full ring; two-CTA scale publication keeps its
existing cluster join. Both payload and SF shared storage remain occupied until
the same final native MMA (including both channel tiles) completes. One existing
TMA-pipeline `tcgen05.commit` releases that common lifetime.

`PipelineCpAsyncUmma.create` accepts an optional explicit `empty_owner` without
changing callers that omit it. Reuse does not initialize the owner's barriers
again. It validates stage count and UMMA completion ownership. The split core
passes its TMA pipeline, allocates only SF full barriers, and updates the raw
metadata calculation from four operand rings to three. Existing TMA-only paths
still reserve the SF full block as before; the removed empty block was unused
there. Alignment and buffer capacity remain calculated from actual storage.

The installed SDK gives both original empty arrays a one-arrival TCGen05Mma
consumer. Admitted clusters are exactly `(cta_group_size, 1)`: the release masks
are local for one CTA and `0b11` for two CTAs for both original pipelines. The
installed SDK sources for arrival, initialization and tail semantics are saved
in `sdk-pipeline-source.json`. SF full arrivals remain local; the existing peer
join is what protects the leader's group-wide SF reads.

## Acquisitions, phases and drains

- Warp zero keeps every existing weight-stage acquisition, including all
  nonwrapping startup stages before the PDL wait. Its later SF writes reuse
  that acquisition. Other SF producer warps wait on the owner's empty phase.
- Both original pipelines used the same producer/consumer state, with one
  advance per K stage and no reset across persistent tiles. Sharing the array
  changes neither index nor phase. Startup uses a separate temporary state and
  acquires at most `min(num_stages, k_tiles)` initial slots.
- Separate TMA and SF full waits, transaction bytes, SF proxy fence, two-CTA
  join, MMA order and accumulator lifetime are unchanged.
- Warp zero drains every shared empty stage through its cloned tail state.
  Other producer warps can reach the existing whole-CTA teardown barrier sooner;
  storage cannot be freed until the owner drain and all roles reach that barrier.
- Inline/overlap epilogues and CLC alter work ownership but not this per-stage
  lifetime. Initial invalid/no-local work acquires no startup slot; the existing
  initial phase and all-stage tail semantics cover unused slots.

## Prior history

`single_completion_experiment` removed redundant completion on old Gather4 and
found only roughly 0.3% phase gains, rejected. The later regular-TMA
`producer_roles_experiment` shared two payload empties while adding a producer
warp and retained a separate SF ring; both variants regressed. The
`merged_operand_ring_experiment` merged full and empty rings with three elected
TMA arrivals plus 128 SF arrivals; it was neutral. This candidate isolates only
the existing payload/SF empty lifetime under the current regular-TMA, CLC,
two-CTA SF join and multi-stage PDL startup design, with no new warp or flag.

## Validation plan and boundary

GPU7 on c3/infra `fi-moe-nvfp4-port-1026`, image
`nvcr.io/nvidia/pytorch:26.05-py3`. Native C++ compilation cache is reused from the
verified persistent control cache; candidate CuTe objects are private.

The private exact gate adapts `api_cleanup_validation/probe_chain.py` and the
current public benchmark's data/chain. It compares separate source-pinned
processes, PDL off/on, changing activations/route weights and balanced/skewed/
no-local routes. Six geometries per NVFP4, MXFP4x8 and MXFP8 cover one/two CTA,
narrow/wide SF, inline/overlap and CLC/static. An extra per-token NVFP4 case
covers the BF16 FC1 output. Static controls use an explicit two-SM diagnostic
budget to force persistent reuse. Full gates retain PTX/CUBIN/SASS and verify
exact output bytes, input hashes, one fewer narrow operand commit and zero
spill instructions. They are diagnostic controls, not benchmark changes.

Only after this gate passes: V41 fixed C–A–A–C public benchmarks at 32/128/4096,
then other models/native AUTO if warranted. Timings retain the standard input
quantization and 100-sample cold-L2 CUPTI methodology. No sanitizer or exhaustive
correctness claim is made from the bounded gate.

## Completed bounded synchronization/codegen gate

Both source processes completed 114 changing-route graph replays (19 geometry /
dtype configurations × PDL on/off × three inputs/routes), with byte-identical
outputs between control and candidate and no nonfinite output. The no-local
routes are zero. All 76 core artifacts have zero stack/local allocation and no
local load/store instructions. PTX, cubins, disassembly, resource dumps and byte
hashes are retained under `evidence/gate-matrix`.

All 52 narrow core specializations remove one redundant `tcgen05.commit` per
emitted mainloop body. NV emits one body; MX FC1 emits two and therefore changes
from five static commits to three (not four). The original driver asserted one
static copy and stopped *after* exact comparison; its original failure log is
preserved. `verify_gate.py` independently verifies both completed processes,
all artifact/source hashes and the emitted-copy accounting without rerunning
any kernels. All 24 wide specializations preserve commit counts. Actual cubin SASS `UTCBAR`
counts independently match these PTX reductions in every specialization,
including the two-SM instruction forms (`sass-commit-counts.json`).

Stage counts remain identical. Actual shared-storage size is unchanged in 64
specializations and drops 128 B in 12 after alignment. Register allocation is
unchanged in 46, decreases in 22 (up to 26 registers), and increases by one or two
in eight. The candidate range is 68–185 registers versus 72–185 for control.
These are bounded diagnostic geometries, not an exhaustive resource claim.

The source remains frozen for timing. A possible later cleanup would remove
the existing unused SF-full allocation in wide TMA-SFB paths; it is intentionally
not mixed into this candidate or its measurement.

## M512 follow-up

The two bounded M512 cases passed 12 additional paired exact replays, closing
two-channel execution coverage. NVFP4 N32 uses overlap/CLC; MXFP8 N128 uses
inline/static; both use two CTAs and PDL on/off. All eight core variants have
zero stack/local allocation, unchanged stage depths/shared storage and the
expected actual SASS completion counts. Registers are unchanged except NV
FC2 PDL-on decreases 130→128. Frozen source pins remain unchanged. Artifacts
are under `evidence/gate-two-channel`, with summary `two-channel-summary.json`.
Proposed API wording and the caller audit are in `owner-contract.md`.
