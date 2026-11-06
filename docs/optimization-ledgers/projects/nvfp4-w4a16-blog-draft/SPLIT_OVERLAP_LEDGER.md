# Split W4A16 overlap: source and optimization-ledger audit

Audit date: 2026-10-08. Read-only; no new benchmarks.

## Recommended blog framing

Suggested heading: **Weight decode can get a head start**.

Once routing identifies an expert, decoding its fixed NVFP4 weights has no data dependency on the incoming activation values. Separate activation-load, weight-load, and transform roles let weight loading and decoding advance as soon as their own inputs and buffer slots are available. The activation path waits for its producer; the weight path does not inherit that wait. In contrast, W4A4's fused output quantizer must first receive the current FC1 accumulator, apply the FP32 scale and SwiGLU, then derive block scales from that newly computed output. Fusion avoids another memory round trip, but cannot remove this data dependency or quantize an output before it exists.

The split implementation puts this independence to work with deliberately placed Programmatic Dependent Launch (PDL) signals and waits. FC1 releases FC2 after its initial routing metadata and weight pipeline state are ready, before its weight loop completes. FC2 can initialize its own pipelines/barriers and load/decode its weights while FC1 continues. Only FC2's activation-TMA role waits for the preceding grid before reading the FC1 output. This overlaps useful independent work across ordinary kernel boundaries: FC1 work can overlap FC2 startup, and FC2 weight preparation can overlap the remaining FC1 work when scheduling resources permit.

The persistent pipeline also carries weight-load and transform state across routed work tiles. With metadata and a free transformed-weight slot available, preparation of the next tile can start while the preceding tile's MMA/epilogue remains in flight. This is bounded runahead, not unrestricted execution or a claim that all dequantization is free.

## Current source anchors

Snapshot read from `evidence/layout-audit-current/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`; pinned public commit `bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4`.

- Lines 1015–1025: initialize the TMEM allocator/deallocation barrier, then arrive at pipeline initialization.
- Lines 1220–1225: common `pipeline_init_wait`, TMEM allocation and allocation wait precede role-specific loops. Therefore, do not say decoding bypasses its own initialization or barriers.
- Lines 1227–1229: scheduling explicitly independent of preceding grid.
- Lines 1411–1431: activation TMA is the sole role that calls `griddepcontrol_wait` for the preceding grid; it sets up tile and producer state first.
- Lines 1484–1505: static weight/scale loads have no preceding-grid wait; FC1 (`fuse_activation`) signals dependents after the first tile metadata and producer state initialization, immediately before its weight loop.
- Lines 489–523: transform depends on raw TMA readiness and a free TMEM slot. No activation-value dependency, but not literally zero dependencies.
- Lines 1634–1675: load/transform pipeline states are outside persistent work-tile loop; only after all tiles does `producer_tail` drain.
- Lines 1710–1764: MMA separately waits for both transformed weights and activation loads. Moving a wait out of the weight role does not let MMA consume incomplete data.
- Current source lines 1432–1438 now launch a standalone finalizer early from the FC2 activation role. This is newer than the July ledger's rejected early-finalizer tests; do not describe the July late-finalizer choice as current.

Pinned source URL: https://github.com/flashinfer-ai/flashinfer/blob/bcfa6539db86bf1202bb1a0fb2fcb15aaf1b36a4/flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py

W4A4 counterpart: `blockscaled_contiguous_gather_grouped_gemm_act_fusion.py`, same commit, lines 2952–3060 scale/clamp/SwiGLU, then 3062–3068 explicitly derive the per-vector absolute maximum and output scale from the SwiGLU result before quantization. The current per-token path's separate quantizer has the same value dependency, even though the fused quantizer description specifically applies to the per-tensor fused path.

## Retained history and measured limits

Ledger: `/Users/ziangli/playground/projects/flashinfer-w4a16/w4a16_optimization_experiments.md` (last updated 2026-08-03; history of PR #4048).

- **22–48, retained design:** separate activation and weight TMA roles, persistent transformed-weight lookahead, PDL with early static-weight initialization before dependent activations are consumed.
- **295–310, retained PDL:** initial on/off 1.006x geomean; later static weight split/release architecture retained for correct dependency placement, not a large isolated timing claim. Raw EP8 geomean 1.005x and TP8 0.963x, normalized same-run controls 1.007x EP8 and 1.014x TP8. The blog should explain opportunity, without attaching aggregate W4A16 gains to PDL alone.
- **557–572, rejected:** releasing FC1 dependents before first tile-info wait and pre-acquiring activation stage before dependency wait did not retain gains. Supports the word deliberately/curated: earlier is not automatically better.
- **948–962, diagnostic/not retained:** more aggressive PDL/async memset/setup did not yield a clean full-sweep win beyond retained static-weight overlap.
- **1311–1334 and 1667–1690, rejected:** restricting TMEM-allocation wait to consumers (letting scheduler/TMA proceed first) did not give a repeatable benefit; CTA-wide allocation wait restored. Do not present these experiments as implemented nonblocking local initialization.
- **3097–3119 and 3539–3567, later superseded:** custom Triton permutation demonstrated graph-node producer/GEMM1 overlap (11.072–12.256 us), but this is not retained production evidence.
- **3571–3636:** real distributed layer-boundary measurements rejected that Triton producer; shared CUDA permutation restored. Do not use its archived timeline or 11–12 us overlap as proof of current permutation/GEMM1 overlap.

Exact local history:

- `887facc5343f00900c65b162e64fc76e72e583cb`, **Overlap W4A16 dependent weight loads**: moved activation dependency wait after local state setup; moved FC1 dependent launch from end of weight loop to after weight-producer state setup. These kernel changes remain visible in current source.
- The same commit's early shared-permutation plumbing did **not** remain: `9c736346eb20e1840516c475dba680924c1a5257`, **refactor(moe): drop ineffective early permute PDL**, removes that plumbing while leaving the kernel changes. Ledger uses earlier pre-cleanup hash `8aed1a35` for this removal.

Relevant ledger log pointers (read-only archival evidence):

- `logs/w4a16_pdl_early_ep8_tp8_20260722_073245/run.log`
- `logs/w4a16_pdl_preacquire_ep8_tp8_20260722_073622/run.log`
- `logs/w4a16_tmem_overlap_bench_20260722_180535/run.log`
- `logs/triton_permute_topology_graph_nodes_ep8_4096_20260723_154010/` (superseded producer)
- `logs/pr4048_distributed_permute_ab_20260724_001201/` (reason producer was reverted)

## Phrasing boundaries

Use: “no data dependency on activation values,” “can run ahead,” “independent work can overlap across kernel boundaries,” and “when scheduling resources and pipeline slots are available.”

Avoid: “zero dependencies” without qualification; “decode runs before its own barriers are initialized”; “PDL guarantees simultaneous execution”; treating rejected early permutation or narrowed TMEM barriers as retained; using archived Triton overlap numbers as production benchmarks.

Memory lookup used only to locate ledger/history: `MEMORY.md:3373–3412` and `rollout_summaries/2026-09-03T19-00-41-QnwC-flashinfer_w4a16_dequant_overlap_and_fc2_l1_cache_audit.md:18–35`, rollout `01a068a5-080f-74c2-a9c5-cf28ebe6b452`. Claims above were rechecked against local source, Git history, and ledger in this audit.
