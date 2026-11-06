# W4A16 FC2 packed scaling port

Base: `fd72759b15b8d417d6c791c0382f90d14262a8e4`. The independent active review is
`flashinfer-w4a16-epilogue-review`; one kernel file is unstaged. Source and patch
hashes are in `source-local.json`. No new tactic, public argument, allocation,
output layout or pipeline synchronization is introduced.

The candidate applies `mul_packed_f32x2` once to each pair in the existing FP32
accumulator fragment, then uses the unchanged full-TMA or partial-SIMT store.
This removes the two branch-local scalar-vector alpha multiplications. CuTe's
packed helper uses round-to-nearest and no FTZ request, matching the intended
scalar multiplication contract. Pair traversal is already used on this same
fragment by the nongated Relu2 path. The fused-finalize and activated branches
remain unchanged. Generated-code and bitwise checks decide whether this is a
useful instruction simplification; no speedup is assumed.

## Recent changes that W4A16 already has

- The shared `moe_swap_ab_prepare.py` is already called from W4A16 with no SF
  tensor (`moe_w4a16.py:451`). It retains its 256-thread payload ownership and
  256-bit copies with the existing 128-bit alignment fallback. The recent
  SF-index change compiles out; all30 prior unscaled streams were identical.
- Deterministic combine is the same `moe_finalize.py` implementation. Its packed
  arithmetic and vectorization improvements already apply.
- Unfused FC2 already writes to padded routed `hidden_workspace`, uses ordinary
  two-dimensional TMA for full epilogue slabs, and combines with the existing
  inverse routing map (`moe_w4a16.py:487–524`, kernel:2504–2570). Blockscaled
  compact-prefix/dense-index metadata would be redundant here: that change
  replaced its expanded-row scatter while W4A16 was already routed.
- Weight and activation TMA roles and independent startup already exist.
  Raw weights/scales share a transaction barrier; transformed weights and
  activations have different ring depths/lifetimes. The blockscaled shared-ring
  sole-announcer change is not a mechanical W4A16 port.
- K96 is native FP4 blockscaled MMA; W4A16 dequantizes weights into BF16 and
  issues BF16 MMA. Its numerical/instruction contract is different. The
  independently owned partial-K experiment is separate from this candidate.

The earlier W4A16 cleanup retained shared prepare, scheduler publication and
static M/K/cache identity with the original23 tactics. Its paired EP screen was
neutral overall (1.0002x); CLC doubling, independent K128 tactics, deeper CLC
metadata, and deferred output-store waits were rejected. See
`w4a16-perf-20261027/README.md`, `sync/audit.md`, `composed23/README.md`, and the
original W4A16 optimization ledger's deferred-store-wait entry at line5607.

## Qualification plan

Primary GPU3 is reserved for the paired gate. `probe.py` invokes the maintained
storage-bit reference boundary test for six routing/topology combinations
(N8/16/32/64/128/192), one-row and half-tile-plus-one tails, static/CLC, PDL off/on.
Each eager result also receives a captured graph replay and bitwise comparison.
This is48 exact-reference cases and48 graph comparisons per source; each owned
W4A16 compile is saved immediately as PTX/cubin/SASS/resource output. Codegen must
quantify PFMUL2/FMUL, registers, local spills and uniform-register spills, with
unchanged FC1 as the control. Native compilation caches remain linked to the
persistent verified cache.

The performance owner will use the current frozen W4A16 winners and routes for
four models in EP and TP, T4/64/4096/16384, C-A-A-C,10 warmups/100 cold-L2 CUPTI
samples. Existing published83df results are workload context, not causal
evidence for this candidate. No performance launch or retention is authorized
by this document alone; the parent coordinates it after the gate.
