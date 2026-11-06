# Retiring CLC workers on padded tickets: closed without implementation

Decision: retain the existing cancellation loop. Early local retirement is coverage-safe at the current loop boundary, but current evidence does not expose padding-drain latency and the physical-launch tradeoff can be large. No source edit, new startup predicate, protocol or GPU experiment was made.

## Ownership and terminal state

Current swap scheduler (`moe_swap_ab_kernel.py:2785–2835`) has exactly one outstanding cancellation. It issues that request for current work, publishes current live metadata, then waits, decodes/fences, releases and advances the response before returning to the loop condition. A condition requiring both hardware validity and a live route would therefore discard only a known empty current ticket. An initial padding ticket has issued no cancellation. A returned padding ticket has already consumed its preceding request. There is no second cancelled tile stranded at either boundary.

Every live ticket still has exactly one owner: its physical launch, or the unique successful cancellation that transferred it to a persistent cluster. Cancellation order need not be monotonic. Encountering padding is only local retirement, not evidence that global live work is exhausted. Uncancelled live tickets remain launchable. Both current implementations use cluster N=1, so the route coordinate and retirement decision agree across the one/two CTA ranks. W4's current tactic topology is explicit in `tuner.py:1112–1123`.

The W4 CLC scheduler (`moe_w4a16_kernel.py:1513–1590`) follows the same issue/current-publication/wait/decode/release sequence but includes terminal publication inside its loop. Refactoring it would have to move the existing terminal publication outside a live-work loop. It must retain exactly one terminal metadata item, its metadata producer tail and CTA0 CLC producer tail. This is more than changing one condition, though it needs no new state.

Installed CuTe `dynamic_persistent_tile_scheduler.py:506–580` shows get_current_work decodes the completed response and issues the generic/async proxy fence; advance_to_next_work emits one elected cancellation. Installed `PipelineClcFetchAsync` uses a one-stage response and all participating scheduler threads release it. Producer tail protects the final shared response from peer retirement. The source snapshot SHA is `bb26b4d246b733e395828a5343220ecae3681722dd78f7f3569878a7e98d296d`.

Swap's existing terminal item remains required for every metadata consumer even on empty initial work. Its operand producer tail, delayed PDL waits, final all-thread join and TMEM release must remain unchanged. W4's metadata tail, operand/transform/accumulator drains, epilogue/TMEM peer lifetime and output tail remain unchanged. Neither design permits an early kernel return. Current startup/producer-exit PDL signals occur outside the live payload loops and already handle the empty-work sentinel; local retirement is not permission to skip them.

The ownership argument follows NVIDIA's [CLC contract](https://docs.nvidia.com/cuda/parallel-thread-execution/#parallel-synchronization-and-communication-instructions-clusterlaunchcontrol-try-cancel): cancellation is atomic on an unlaunched cluster and successful ticket identities are unique; multicast response requires peer lifetime. The local early-retirement conclusion is our inference from that contract and these source loops.

## Current geometry and evidence boundary

`clc-padding-geometry.json` reconstructs all50 control measurements whose captured native FC2 observer reports CLC enabled, using their recorded expert histograms, workspace route capacities and unchanged winner geometries. Examples:

| Native case | Live / allocated route tiles | Padded FC2 cluster tickets | Padded capacity |
|---|---:|---:|---:|
| V41F EP4 MXFP8,512tokens |96 /282|7,440|66.0%|
| N3U EP8 MXFP8,512tokens |68 /414|5,536|83.6%|
| V3 TP8 per-token,16384tokens |632 /767|7,560|17.6%|

These are grid-capacity counts, not observed physical launches or successful cancellations. The existing loop can cancel padded tickets while a previously published useful tile is executing. Retiring instead can leave those tickets to launch and pay barrier initialization, cluster rendezvous, TMEM allocation and teardown. The fresh V3 TP MXFP8 source-counter profile uses ordinary scheduling and cannot quantify that CLC tradeoff. No useful padding-drain timing or physical-launch counter exists in the captured CLC evidence. Therefore fewer cancellation instructions alone do not justify implementation.

## History

The exact idea was already reviewed, not benchmarked, in the old project's `scripts/clc_elected_owner_20261026/padded-ticket-early-stop-review.md`; it reached the same coverage/launch-cost boundary. The rejected `perf-general-20261026/clc-bounded-work` changes ticket mapping and is a different experiment. No attempt is reopened here.
