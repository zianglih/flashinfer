# CLC metadata: current native traffic and prior route trial

**Do not reopen route-in-slot3 or force four-word consumption.** The exact route proposal already failed its native gate. Current consumers are pruned by role; some vectorize and some deliberately read two separated words. No source/GPU work was performed.

Current source is clean `c1ac8ce7341039db65195b99445fcdeb193cf226`, swap SHA `482b636a1714486e2ffb34c8ae005da3cef26f25f0ce034ba1eb59c6198d6276`. `moe_swap_ab_kernel.py:2377–2383` already aligns the four-word metadata record to16 bytes. `next_work:2514–2529` reads tile/expert/valid before the existing release; scheduler publication at2833–2835 and2850–2852 writes those three fields. Slot3 is unused.

## Actual current native evidence

Source-bound control: `experiments/startup-weight-cache/qualification-r1/evidence/nvfp4-clc-1cta-control/codegen/00-Sm100BlockScaledGroupedGemmKernel.{ptx,sass}`. Its receipt identifies actual CLC, one CTA, N16/K256/SF16, PDL enabled; cubin SHA `6da029160136e9c14203875538579f85be5c39333ea642cce026403069c22809`. These are representative sites, not a claim about every specialization.

| Role | Native instruction(s) | Meaning |
|---|---|---|
| Scheduler live publication | `STS.64`0xc50 + `STS`0xc60, then release0xc70 | Two stores for three fields, not three scalar stores. Terminal publication also has two stores0xe00/0xe10. |
| Weight | `LDS.64`0x1980 (next item0x1d50) | Tile and expert merged. |
| Gather relay | `LDS`0xf00 (next0x10b0) | Only tile survives. |
| MMA | `LDS`0x1160 +0x1170 | Tile and valid are separated words. |
| Epilogue | `LDS.128`0x2420 (next0x3930) | All three required fields in one native load. |
| Gather | `LDS`0x39f0 +0x3a30 (next0x40d0/0x40f0) | Tile and valid are separated words. |

The MMA/gather PTX is already `ld.shared.v4.b32` with `used_bytes_mask 0xf0f` (PTX659/1418), yet PTXAS selects two scalar LDS. Consequently a source vector tensor/copy does not establish one native load. Forcing four words would retain extra field/register work instead of preserving current pruning; no native benefit is demonstrated.

A narrower untested possibility is to initialize reserved slot3 to zero at both scheduler publications and let ordinary vectorization merge all four stores. Alignment/storage/publication already permit this, and it requires no consumer interface or readiness change. It might replace the existing two stores with `STS.128`, but may instead add a store or register moves. No actual lowering/performance evidence supports retaining it, and this note does not authorize an experiment.

## Exact prior route experiment

`../flashinfer-w4a4-split-dynamic-n/scripts/clc_route_metadata_20261027/{README.md,candidate.patch,decision.json}` implements exactly: publish scheduler route in slot3, return it through `next_work`, replace consumer division, derive channel as `tile-route*total_m_tiles`, preserve flattened tile and static scheduling. On historical b85,40 exact replays per source/20 core pairs passed with no spills, but total native instructions increased99 and registers rose up to10. Some division removal was real; uniform-path/register changes outweighed it. It was not retained, with no E2E timing.

The separate `clc_route_uniform_20261027/{README.md,decision.json}` adds `make_warp_uniform` only to the route load. It passes the same gate, reproduces19/20 identical SASS files (the last only changes R2UR order/reuse flags), and retains the same +99 instructions/+10 maximum registers. Both decision files explicitly reject retention. This is historical evidence, not a measured result on c1ac; there is no new mechanism here that warrants replay.

These trials are distinct from `clc_elected_owner_20261026` / current `audits/clc-consumer-arrivals.md` (arrival/owner coordination) and lane-metadata / batched gather-index work (global token-map ownership). Both current and prior CLOSED_LEADS indexes plus the bounded CLC directories were checked; the exact route trials live outside the short index.

W4 is a useful contract comparison, not proof of a free swap change: `moe_w4a16_kernel.py:1575–1578` already publishes CTA-M coordinate, route start, expert and boundary distance. `mixed_input_helpers.py:956–967` copies that four-field record with `cute.autovec_copy` into its existing work object. Swap currently uses a flattened tile for termination, addressing and ordinary scheduling, so adopting W4's record changes that internal contract rather than deleting only a divide.
