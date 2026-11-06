# W4A16 structure compared with regular-TMA blockscaled FC1

CPU/source-only audit, 2026-10-25. The reference is this project's frozen 442
W4A16 implementation, not an assumption that the older W4A16 checkout is equal.

| Source | SHA256 |
|---|---|
| 442 `blackwell/moe_w4a16_kernel.py` | `2fdadcdaee4a1819b050815fddab44017b31e4649f5146a99278cddcefa536cf` |
| 442 `blackwell/moe_w4a16.py` | `09771708151bfda13c7654a79d7143bb16851555d1b5e8d6dfb3595ad6f6658e` |
| Initial regular-TMA core | `9f53fd0a8a775f0091d3b718d944e0271708ae8022d9fac59ae7dba6425d1c0a` |
| Older W4A16 checkout `adcf4b123caaeda1fe589a722462c8beb75d7176` kernel | `4a870648549397c4ef8d4db52b4bfe3dde3ff09feed94abd942ea945f3185866` |

The older checkout has the same role map, load pipelines, stage fitter, cache
hints, descriptor prefetch, and FC1 early PDL trigger. It lacks 442's standalone
FC2 early finalizer trigger, prepared gated-weight layout, transform tracing
hooks, and static/tail refinements. References below use **442 line numbers**.

| Mechanism | W4A16 at 442 | Initial regular-TMA core |
|---|---|---|
| Roles | 16 warps: epi0–3, MMA4, scheduler5, weight TMA6, activation TMA7, transform8–15 (`153–177`) | 9 or 5 warps; N128/N256 TMA issue is all on warp0; other original SF-loader warps are idle (`387–393,1186–1268`) |
| Input pipelines | A/SFA TMA→transform, transform→MMA, independent B TMA→MMA (`932–973`) | One TMA→MMA ring for A/SFA/B/SFB; narrow N also uses SF cp.async |
| Stages | Fits load/transform/output depths from SMEM/TMEM, metadata1 with CLC or3 static (`2378–2543`) | Fixed 3–5 operand stages; NB2 SF16=4, SF32=5 (`375–397`) |
| PDL | Only activation loader waits; FC1 weight role triggers dependents early; unfused FC2 triggers finalizer after its activation wait (`1401–1428,1493–1495`) | All roles wait before reading active metadata; trigger at kernel end (`1063–1065,1681`) |
| Cache | A `EVICT_FIRST`, B `EVICT_LAST`, scales default (`1457,1544`) | A first only for one-CTA K8; otherwise A/B/SF default (`419–424,1216`) |
| Prefetch | TMA descriptors at entry (`907–910`), weight producer carries empty-stage probe (`1527,1559`), MMA carries transformed-A readiness probe (`1718,1762`) | No descriptor or data prefetch, blocking stage acquires/waits |
| Accumulator release | Four elected epilogue lanes per CTA; expected count `4*G` (`976–984,1991–1993,2154–2156`) | All128 epilogue threads per CTA; expected `128*G`; helpers also release internally |
| Workspace | Invocation-local allocation; caching allocator and private graph pool own storage (`moe_w4a16.py:59–91`) | Diagnostic installer caches shared shape-keyed scratch; initial review-copy host has invocation-local allocation |

## Minimal useful transfer

After the preparation result is established, isolate **independent A/SFA and
B/SFB pacing**, without adding a warp or storage stage:

1. Keep the existing 288/160-thread role map. For regular FC1 N128/N256 only,
   retain A/SFA on warp0 and assign B/SFB to existing idle warp1. Leave small N
   and FC2 on their current paths.
2. Use two `PipelineTmaUmma` rings of the existing depth. Reuse inactive
   `ab_barriers` for B; its `2*num_stages` entries already fit. Keep all operand
   layouts, SMEM buffers, TMEM SF offsets and accumulator lifetimes unchanged.
3. Expected group-wide bytes are
   `G*C*(128*tileK*weightBits/8 + sfStageBytes)` for A and
   `G*(bRows*tileK*activationBits/8 + sfbStageBytes)` for B. Their sum equals
   the original TMA transaction count. Each ring has one elected producer
   arrival; both CTA transactions target the corresponding leader full barrier.
4. Each producer acquires, advances, and drains its own per-thread state.
   The MMA leader waits for both rings and releases both only after **both NB2
   MMAs**. Do not release shared B/SFB after the first channel tile or copy the
   W4A16 accumulator arrival count without changing its participants.
5. Preserve current PDL placement in the first variant. A later activation-only
   wait requires proving routing metadata ready before other roles read it,
   and protecting both prepared payload and SFB until preparation completes.
   Merely moving the wait in the existing combined producer is insufficient.

No W4A16 dequantization warps, transformed-A TMEM stages, or 176/80/128 register
redistribution should be imported: blockscaled MMA consumes the quantized
operands directly. Separate pacing is a source-supported hypothesis, not a
measured speedup. The new clone is `flashinfer-regular-tma-pipeline`, based on
442 plus the exact three-file `review_snapshots/initial/manifest.json` snapshot.
All changes remain unstaged; no GPU launch is part of this audit/prototype step.

## Avoid repeating rejected work

- The old blockscaled cache/descriptor-prefetch screen and safe early PDL were
  neutral or slower: [pipeline/cache ledger](../pipeline_cache_experiment/README.md).
- Adding a tenth weight-TMA warp while sharing the Gather4 full barrier did not
  produce repeatable full-chain gains: [dedicated-weight ledger](../dedicated_weight_tma_experiment/README.md).
  The proposed variant instead reuses a warp and separates the barriers after
  regular TMA eliminated the 128-thread SF producer.
- Compact six-warp FC2 passed exactness but was neutral/inconsistent:
  [role-count ledger](../fc2_roles_experiment/README.md). Do not use the structural
  comparison to recommend repeating it.
- The W4A16 ledger rejects activation-stage pre-acquire polling (`1927+`), dual
  operand readiness probes (`1989+`), broad/rolling TMA L2 prefetch (`4284+`), and
  direct PTX L2 prefetch (`4395+`). More probes or prefetch instructions are not
  intrinsic benefits of adopting W4A16's organization.
- W4A16 CLC benefits and metadata staging are distinct from producer pacing.
  Current blockscaled scheduler controls are already archived in
  [scheduler ledger](../scheduler_experiment/README.md); no new scheduler axis
  is proposed here.
