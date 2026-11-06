# Wide prefill: current source and prior experiments

Source audit of measured current `0b7fe90151340d4fca6a5ec41a91019dde743819` versus
old `002529e17b22567a071091053c6c4dc2a55e050e`. Kernel source paths below are
under `flashinfer/fused_moe/cute_dsl/blackwell/`. Historical measurements retain
their own hardware/source contracts and are not current speedup evidence.

## Structural differences worth keeping distinct

- Old FC1 directly gathers original activation rows. Current FC1 consumes a
  byte-preserving routed payload and canonical SF allocation prepared once per
  call. Current preparation adds a global read/write pass, but removes repeated
  routed SF/payload issue work from every FC1 channel tile. Activations on MMA B
  and dynamic N do not inherently require materialization.
- Old one-CTA route-M128/channel-N256 is a missing current geometry, separate
  from loading. The completed channel-tiling candidate addressed that gap using the
  existing channel loop and lost on all four measured wide-prefill cases. The older narrow-route one-CTA channel-reuse trial
  tested N16/32/64, not the proposed wide N128 case.
- Both implementations already derive operand stages from resource capacity.
  Old FC1 reserves two C stages, then uses spare capacity for more C stages
  (`gather_grouped...py:3452–3565`); old FC2 starts with one C stage
  (`grouped...py:2363–2477`). Current derives TMEM accumulator overlap and SMEM
  operand counts together (`grouped...py:1511–1796`). Its bulk FC2 reservation
  prefers 64-token/two-stage output, falling back to 32-token/one-stage output.
  Maximal operand depth alone is not a new policy: larger output buffering
  competes for the same capacity, and cross-output-tile prefetch is intentional.
- Current FC1/FC2 already prefetch all available startup operand stages, bounded
  by the reduction's K tiles, before the activation dependency wait. Moving
  more producer roles or adding stages without a specific measured blocked
  dependency repeats previously neutral/regressive work.

## Regular TMA was compared against the transposed Gather4 implementation

`scripts/fc1_regular_tma_experiment/DIRECT_SOURCE.md` and
`OPTIMIZATION_LEDGER_2026-10-24.md:450–559` preserve actual-source comparisons
on base442 after the new weight layout and transposed dynamic-N implementation
already existed. They include preparation inside full-chain timing, identical
inputs/routes/final bytes, four samples of each arm, and 100 timings per sample.

| Existing tactic | 8192 control/regular | 16384 control/regular |
|---|---:|---:|
| N128, FC1 logical M512/NB2 | 0.989934× | 1.025444× |
| N256, M256/group2 both phases | 1.135621× | 1.169912× |

These were fixed-tactic diagnostics, not current AUTO results. The final native
AUTO campaign compared against the original upstream baseline rather than
isolating Gather4. Its V3 NVFP4 8K/16K losses do not erase the positive matched
N256 loader comparison. Restoring a Gather4 architecture from current timing
alone would therefore be premature; it would reintroduce four producer warps,
routed SF copying, and a different completion contract.

## Preparation policy and closed alternatives

`moe_prepare.py:95–179` assigns one persistent CTA per routed row, copies valid
payload with 256-bit operations when aligned, and scatters four-byte SF words
into the canonical 128-row atom. Full-warp SF source loads are contiguous;
destination words are 512 bytes apart. This is a sector-efficiency concern,
not proof of HBM saturation: L2 can combine stores from neighboring rows.

For R live routed rows, payload P bytes/row and S scale bytes/row, useful copy
traffic is approximately `2*R*(P+S)`, with extra SF padding stores. V3 NVFP4
has P=3584 and S=448. At R≈16384, this is about132MB; a25.84µs preparation is
about5.1TB/s of useful copy traffic. Actual routing counts, L2 hits and physical
sectors must qualify that estimate; it is not a measured DRAM-bandwidth claim.

Already evaluated:

- **128-row SMEM SF transpose:** 16,896B scratch, two CTA joins, contiguous SF
  stores. Rejected at prefill: preparation1.83–3.12× slower. See
  `scripts/regular_tma_sf_tile_experiment/README.md`.
- **Wider SF source vectors:** fewer source loads but longer scalar scatter
  chains; preparation regressed NV8K/16K about3.4–3.8%, MX16K about1.9%.
  See `scripts/prep_sf_vector_experiment/README.md` and ledger767–804.
- **Destination-linear scalar SF ownership:** separate barrier-free SF loop,
  contiguous stores but scattered source/metadata loads. It passed36 byte
  checks and saved only0.04–0.08µs at decode32/128. No prefill/full-chain screen
  was run. This is the remaining bounded store-coalescing question, not a new
  proven gain (`scripts/prep_linear_sf_experiment/README.md`).
- **Independent A/SFA and B/SFB rings**, **weight/SFA issuer split**, **producer
  loop role hoisting**, **two-CTA SFB multicast**, **deeper narrow-route operand
  stages**, **wide-K overlap**, **K96**, **K-tail MMA predication**, and **SF32
  scratch double buffering** all have closed negative/neutral experiments.
  Do not restart them solely because the old implementation differs.

## Current round decisions and remaining experiments

The PDL-only half-budget preparation grid passed36 byte checks but was neutral
or slower at prefill, including a1.62% Nemotron NVFP4 loss. It is rejected;
the full hardware-derived grid remains (`prepare-pdl/`). The selected-kernel
NCU preparation profile shows23.38% peak DRAM throughput and86.97% long-scoreboard
stalls, not HBM saturation (`profiles/ncu-prepare-v3-nv16384/`). Neither this
profile nor the negative destination-linear SF result justifies a new
model-specific ownership rule.

The balanced ternary absmax experiment compiles to the same eight ternary
instructions as the compiler-fused control, but reduces their dependency depth
from eight to three, with unchanged registers and no spills. Exact live FC1 checks passed, but the tree is rejected: decode is neutral
and Nemo NVFP4 16K loses 0.895%. Source copies are removed; evidence and caches
remain (`amax-tree/`). The prior nine-operation B200 trial remains neutral
historical evidence.

The bulk-drain candidate moved the terminal shared-read drain to the next
epilogue entry with a final owner drain. All 72 exact replays passed, but the
repeated eight-cell screen had no convincing stable gain. It is rejected;
the simpler existing scratch lifetime remains (`bulk-drain/disposition.md`).

FC1 protected-prefix buffering passed the revised 48-case exact gate and
CLC checks without spills. However, four completed native brackets averaged
−0.93%, including a stable −2.54% Nemo per-token 4096 loss. The twelve-cell
plan stopped early, and the incomplete next cell is excluded. The additional
142 source lines and higher registers are rejected (`fc1-prefix/`).

Packed per-token FC2 scaling is retained at `7ae6244d`: unchanged ownership
and shuffle counts, pairs of scalar products replaced by the existing packed
multiply. Eighteen paired exact checks pass with no spills, while six FC2
variants remove 64–256 instructions each. The eight-cell CAAC screen is
neutral overall (1.000217×), accepting an observed V4.1 prefill loss of 0.688%.
No end-to-end gain is claimed (`bulk-scale-pairs/`). No new tuning or policy
axis is added. The complete old/current campaign remains attributed to its
measured `0b7fe901` source.
