# Gathered-SF lane coalescing: feasible mapping, no prototype yet

Read-only retained `2b8eb9d8`/swap `482b636a`. This is a CPU ownership hypothesis,
not a kernel patch, hardware qualification or performance result.

Four adjacent lanes could copy four consecutive4-byte SF words from the same
routed token while scattering directly into the unchanged canonical SFB image.
The existing copy instruction stays4 bytes and needs no stronger public pointer
alignment. No shared-layout or S2T descriptor change is required. This differs
from the closed shared-layout/vector-width proposal, which required an illegal
sub16-byte descriptor permutation.

For `W = tile_k / (4 * sf_vec_size)` words per row, a possible compile-time
group size is `G=min(W,4)`. Current supported W values are1,2,4,8. Permute each
warp's existing32 row owners into G lanes per row and G row batches, preserving
the original row permutation at G=1. Each lane still issues W copies per128-row
block. The source-bound CPU proof verifies the exact destination-word bijection
and all live/zero/unused classifications across all route counts, both CTA
groups, K-word tails and the current20 shared-stage geometries.

The costs are explicit:

- Full-warp K256/SF16 source requests become8 rather than32 distinct32-byte
  sectors per copy for distinct,128-byte-stride routed rows. Four instructions
  request32 rather than128 sectors in total, but **the unique source bytes are
  unchanged**: the current `.ca` copies can reuse the same cached sector across
  successive words. This is a request-coalescing hypothesis, not a claim of4×
  less DRAM traffic. General four-byte-aligned rows can cross sector boundaries.
- The same four lanes write four different shared words in the same bank.
  The32-bank arithmetic predicts four distinct destinations per bank, versus
  one currently. Actual cp.async serialization needs native counters; the CPU
  model does not assert measured four-way wavefront behavior.
- Distinct persistent64-bit SF offsets grow1→4 per thread, or2→8 for N256.
  This adds up to6 or12 logical32-bit register slots before compiler allocation.
  Reconstructing them inside K would instead add repeated routing/address work;
  no shuffle or extra staging workaround is proposed.
- The local barrier's SF-participant count must become
  `min(128, route_tile * G)` for this mapping, with exactly that static set
  attaching cp.async completion. The payload announcer remains separate.
  Both SF zero-fill bounds and combined payload/SF completion remain required.
  Shared footprint and pipeline stage count do not change.

Bounded history search found no completed measurement of this exact adjacent-K
lane grouping in the dedicated gather warpgroup. The old
`scripts/sf_warp_pairedrow_experiment/README.md` used physical N16 and the earlier
nine-warp pipeline; it reduced eight copy sites to four by assigning paired
rows, added startup stores and regressed0.7–1.3%. It is not evidence for this
constant-site-count mapping. The later SF/payload-coordinate-sharing variants
changed row ownership to reuse payload metadata and increased instructions or
spilled; they are also distinct, but caution against adding long-lived offsets.
The direct-TMA and wider-SIMT-load proposals remain closed.

The new wide-EP profile reports only2.00% MIO stalls, versus9.81% in the old TP
profile. Therefore keep this as a bounded feasibility note. No prototype is
warranted without stronger actual-PC request/issue evidence and a concise
register-safe implementation. It must not acquire a dtype/model-specific
policy or an additional tuning axis.
