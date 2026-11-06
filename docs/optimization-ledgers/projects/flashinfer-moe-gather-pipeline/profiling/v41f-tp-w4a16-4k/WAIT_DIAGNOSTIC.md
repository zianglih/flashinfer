# Retained V41F FC1 wait attribution

This additive note uses the unchanged `2b8eb9d8` source and loaded ELF in
`RESULTS.md`. It does not modify the original report, raw evidence, or peer seal.
`analyze_waits.py` replays the counters into `wait-analysis.json`.

The larger sampled waits do **not** establish a removable synchronization or
justify more gathered-B stages. The gather role is mostly waiting to reuse its
buffer; the MMA role has B ready after acquiring transformed A.

| Dependency | Actual native evidence | What it establishes |
|---|---|---|
| Raw A ready | Cached P3 is consumed at `0x2a60` 614,400 times. The fallback probe `0x2a80` executes only 1,154 times (0.188%). The next-stage probe at `0x2cf0` precedes 170 non-NOP decode/store instructions before loopback. | The cached query usually succeeds, but this is not a measurement of readiness at query issue. The nominal static distance is not the scoreboard-independent window; see the refinement below. |
| Gather B empty | `0x5870` enters the fallback for 98.956% of predicated thread observations; `0x6be0` performs 5,898,964 repeated queries for 307,200 producer acquisitions. | This is real buffer-reuse backpressure, not evidence of slow Gather4 completion. Reuse still depends on completion of prior MMA reads. |
| MMA A full | The `0x1f20` fallback is entered on all 38,400 stage acquisitions; its loop performs 753,377 queries. | The MMA role waits for transformed A publication. The count alone does not separate dequant issue latency, asynchronous read completion, and steady-state pipeline pacing. |
| MMA B full | The `0x1f60` fallback is never taken; its `0x6760` query executes zero times. | B is ready **after the preceding A wait**. This is not a counterfactual measurement of swapping acquire order or removing B's dependency. |
| Weight A empty | 76,208 of 76,800 initial acquisitions enter fallback; 1,991,492 repeated empty queries. | Raw-weight residency is also generally ahead of transform consumption. More issue runahead is not supported by these counters. |

The two decoded slots also cycle through their empty acquisition. The raw,
decoded, B and accumulator barriers protect different storage and asynchronous
readers; none is a second spelling of the same dependency. The current MMA loop
acquires A, acquires B, issues all stage MMAs, then commits the asynchronous A/B
releases. Removing or advancing those releases would change the operand lifetime.

Source anchors are `moe_w4a16_kernel.py:703` (transform), `:1931` (MMA),
`:2754` (gather), and `:1064` (barrier storage). The selected full-K FC1 has
20 K256 stages; no K-tail predicate explains these observations.

## Comparison and closed mechanisms

Rubin split's regular TMA producer carries an empty token after issuing B/SFB
(`rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:2456–2512`).
Next Rubin Mega advances/peeks its combined AB ring before SFB issue, after a
160-thread gather rendezvous (`block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1063–1086`).
Those are different completion/producer contracts. W4 already has four independent
gather issuer arrivals and caches row IDs outside K; copying the rendezvous or
adding another token does not remove the real empty dependency here.

W4 Mega inherits this transform. Its raw release precedes the TMEM-store fence,
whereas split releases afterward. The native split fence has no newly exposed
stall signal, and earlier raw-release schedules were already measured and
rejected. This narrow source difference does not reopen them.

History boundaries: `audits/w4-readiness-test-followup.md` already found a useful
raw-query window in N3U; `audits/pipeline-followup-2b8.md` records the distinct
wait lifetimes. The previous project's `CLOSED_LEADS.md` preserves plain raw-wait
decode losses, neutral scale-preload evidence, independent-stage prefill losses,
and rejected producer-ownership cursors. No TRY-to-TEST, raw preload, stage-count,
or gather issue-order prototype follows from these branch/fallback counts alone.

## Native scoreboard refinement

The subsequent exact control-word audit changes the raw-query interpretation:
`LDS.128` at `0x2ca0` and `0x2ce0`, plus the next-raw `TRYWAIT` at `0x2cf0`,
all assign write-dependency barrier 5. The `F2FP` at `0x2f80` waits mask `0x20`
after only **40 intervening instructions** and has 617 observations, 587 long
scoreboard. The later P3 branch at `0x2a60` waits `0x16`, not `0x20`; the final
decoded-slot TRY at `0x3790` assigns write barrier 1/read barrier 4. Therefore
neither the 170-instruction distance nor the branch's 1,244 observations isolates
raw-query latency. Raw LDS and the early query share a dependency group at an
earlier conversion. Independent replay is `audits/v41f-w4-scoreboard-peer.json`.

This supports a distinct **source-only** assessment of replacing the existing
raw query's potentially suspending TRY primitive with TEST, retaining both
existing tokens and every mandatory wait. It does not reopen raw-peek removal,
add a lookahead state, or establish how much of the mixed dependency is query
latency. See `audits/w4-raw-test/DESIGN.md`; no candidate is implemented here.

## Separate load-path observation

The four packed-weight `LDS.128` sites each require four ideal wavefronts and
have zero excess. The two scalar SF `LDS` sites at `0x2be0`/`0x2c60` each show
four achieved versus one ideal wavefront: 1,843,200 excessive wavefronts per
site. This is source-correlated load evidence, unlike the ambiguous aggregate
output-store counter. Its exact scale-address layout/history is a separate
read-only follow-up. It does not yet establish an exposed latency or a legal,
source-simple remapping.

NVIDIA's [PTX barrier contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-mbarrier-test-wait-mbarrier-try-wait)
keeps successful phase observation distinct from the consumer's later release;
its wait/query syntax does not determine native independent-instruction overlap.
The [NCU guidance](https://docs.nvidia.com/nsight-compute/ComputeTriage/#symptom-shared-memory-bank-conflicts-are-significant)
requires source-level load/store attribution before assigning aggregate conflicts
to a layout. No sample count here is converted into an E2E savings estimate.
