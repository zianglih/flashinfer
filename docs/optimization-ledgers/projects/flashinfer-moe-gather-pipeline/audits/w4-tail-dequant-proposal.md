# W4 compile-time K-tail transform validity: read-only proposal

Current source02de; native evidence `profiling/n3u-tp-w4a16-16k/`. The useful distinction is arithmetic/TMEM work removal, not moving a wait or reducing participant counts.

- The current MMA already peels static K tail (`moe_w4a16_kernel.py:1982`). For FC2 K640/stage256 it executes40 K16 atoms, not48.
- The shared `_transform_tile` is passed only `k_tile_cnt`, runs a full transform for each stage, and cannot distinguish logical K640 from K768. The caller has static `mA_mkl.shape[1]`, so the missing information is compile-time, not a new runtime/tuning policy.
- Current native FC2 assigns two transform groups via `(warp_id-8)>>2`; each group adds64 to its TMEM column coordinate. BF16 packs two elements per TMEM column, so the groups cover K[0,128) and K[128,256). In the final stage, group1's arithmetic/store output is unused by the existing MMA tail. Confirm generalized layout ownership using the actual CuTe partition rather than hardcoding this observation.
- `_setup_transform_partitions` divides the partition's mode3 across the transform groups. Need a CPU/layout-level proof across every supported MMA/CTA geometry and K remainder, and both weight-row contracts, that source coordinate and destination column validity agree. Small K tails may split a group's fragment and need a compact valid view rather than a group-wide skip. Do not add runtime shape dispatch or a new public/tactic knob.

Minimal qualification order if the layout permits concise source:

1. Prove K ownership and source/SF/TMEM ranges from actual static layouts, including K16–stageK remainders. Preserve untouched valid value arithmetic and conversion order.
2. Retain all current waits, releases, arrivals, and phase advances in both active and inactive transform roles. Raw TMA keeps nominal geometry; no buffer lifetime changes. No raw/SF read or store for wholly invalid fragments. Only the existing final stage requires a runtime path; the divisibility decision is constexpr.
3. Stop if this needs a larger state machine or fallback branches. The only expected extra information is actual compile-time logical K; do not infer it from token/model shapes. Shared MegaMoE `_transform_tile` callers currently supply K-tile count only, so prefer an isolated split implementation boundary or an exact no-op default for full stages with explicit shared-callsite qualification; no silent legacy contract change.
4. Before performance: paired exact/codegen for one/two CTA, FC1/FC2, K shorter than stage and nonmultiple stage, repeated persistent tiles, CLC/static, both gated layouts, and relevant activations. Require no new local allocation/register pool changes. Native codegen must show reduced unused decode/TMEM stores with unchanged full-K specializations.
5. Only then a frozen-tactic paired screen on affected native EP/TP cases. N3U TP is a useful signal, but not a model-specific retention gate. A large speedup is not expected from the already73% tensor-active FC2 profile.

History searched: old-project W4 closed-lead index; W4 raw/decoded independent-stage, transform-wait/preload, output-acquire, register and route-ID experiments; original W4 optimization ledger. No exact K-tail transform-skip trial found in that bounded search. This is not a claim that all possible historical source copies were searched.
