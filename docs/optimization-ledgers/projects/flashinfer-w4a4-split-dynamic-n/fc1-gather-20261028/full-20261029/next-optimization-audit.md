# Gathered FC1 follow-up audit

Base: fork experiment `fb66a27e6b40bdbbefd1b8bf0c0fc3f3ada8af90`.
Read-only audit followed by the requested isolated payload-first candidate.
The source audit was read-only. Subsequent authorized validation is recorded in
`payload-first/`; candidate source remains unstaged.

## 1. Payload-first issue order — rejected after matched measurements

Workspace: `flashinfer-fc1-gather-payload-first-review`, independent clone at
`fb66a27e`; one unstaged file. Artifact: `payload-first/candidate.patch`.

Move the existing 32-line Gather4 issue block before the existing SF cp.async
issue/arrival block in the gather K loop. The intent is to overlap payload TMA
latency with scale address calculation and copy issuing. This differs from R8:
R8 moved only the async completion arrival after Gather4 while SF loads still
preceded Gather4. R8 was not retained.

Ordering proof:

- The operand-empty wait still precedes every write into the reused stage.
- The same elected thread announces the same Gather4 transaction byte count;
  it remains before that thread's payload and SF issue. Cross-warp announcement
  ordering is unchanged from the qualified base.
- Payload writes only `sB`; scale copies write disjoint `sSFB`.
- The local barrier still expects 129 arrivals: one transaction announcement,
  plus one async SF completion from each of 128 gather threads. SF bytes are
  not included in TMA transaction bytes.
- Every thread's `cp_async_mbarrier_arrive_noinc` remains after all its SF
  copies. The local barrier cannot complete until both TMA bytes and SF
  arrivals complete, independently of their issue order.
- The relay wait, async-proxy fence, cluster publication, MMA waits and shared
  stage release are unchanged. No stage, CTA, register, scheduler or PDL policy
  changes. FC2 is unchanged.

Local CUTLASS reference:
`references/cutlass/python/CuTeDSL/cutlass/experimental/primitives/nvvm_wrapper.py:2871–2929`
documents the exact hybrid TMA plus per-thread cp.async arrival accounting and
CTA-local completion-forwarder pattern. The public primitive implementation is
`references/cutlass/python/CuTeDSL/cutlass/cute/arch/mbar.py:466–484`.

Static checks passed: inverse block relocation reconstructs the base byte for
byte; AST parse; `git diff --check`; all applicable file-scoped pre-commit hooks,
including mypy, Ruff check and formatting. Kernel SHA256:
`bb9dc56eb993192e43ee3b1d2d2a2ed6742cd4e7b756b1c4d5f874378d300dcd`.
All seven selected existing correctness cases passed on B300/CUDA 13.2,
covering two-CTA MX modes, SiTU, NVFP4 per-token/per-tensor and partial K.
The five-job, 44-cell C-A-A-C screen at 8/256/4096/16384 tokens completed
against clean `fb66a27e`, with 100 strict-CUPTI cold-L2 samples per phase and
frozen routing/tactics. Affected-cell geometric mean was −0.178%; N3U EP
W4A4 at4096 regressed2.017% with low phase spread. Do not retain. Full
results: `payload-first/RESULTS.md`. The possible downside is delaying SF
request issue behind many Gather4 requests; retain only after matched
measurements across narrow and wide tiles.

## 2. Descriptor prefetch — small general startup candidate

The current swap-AB kernel does not prefetch TMA descriptors. Descriptor addresses
are available before the PDL dependency wait and do not depend on routing or
activation payload publication. A dedicated producer warp can prefetch A/SFA;
the activation owner can prefetch B and, for regular-TMA FC2, SFB. Prefetch the
output descriptor only when present. This does not permit reading routing
metadata or weights before the required dependency publication.

Existing patterns:

- W4A16: `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:1133–1138`.
- Rubin: `flashinfer/fused_moe/cute_dsl/rubin/blockscaled_contiguous_gather_grouped_gemm_swiglu_fusion.py:1374–1379`.
- Hopper: `flashinfer/fused_moe/cute_dsl/hopper/contiguous_grouped_gemm_finalize_fusion.py:398–400`.
- CUTLASS Blackwell grouped GEMM:
  `references/cutlass/examples/python/CuTeDSL/cute/blackwell/kernel/grouped_gemm/grouped_gemm.py:539–544`.

Likely a startup improvement, not sufficient by itself to explain or close the
large sustained EP prefill gap. No implementation in this candidate.

## 3. Avoid Gather4 requests outside runtime MMA N — larger follow-up

Current Gather4 issues the full static route tile, including complete row groups
outside runtime MMA N. Define live payload rows per CTA as
`round_up(valid, 16) / cta_group_size`; predicate whole Gather4 groups outside
that extent and use exactly the same live extent in expected transaction bytes.
Keep zero-fill sentinel coordinates within the rounded extent and preserve full
SFB publication. The policy follows the instruction's actual read extent and
does not need model, dtype, token-count or topology exceptions.

Reference: Rubin MegaMoE
`flashinfer/moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/inference/mega/block_scaled_swap_ab_fc12_mainloop_gen_specialized.py:1218–1273`
uses `dynamic_gather`, the same aligned two-CTA row midpoint, and live-row issue
predication. Its producer synchronization differs; do not copy its named barrier
into this asynchronous relay pipeline.

Safety requirements: expected bytes must match all issued payload groups on
every CTA; source OOB rows inside the instruction extent still need hardware
zero-fill; skipped shared rows must never be read by MMA. Test N16, group2,
partial routing tiles and partial K before performance. This principally saves
padding work and should not be assumed to cure full-token prefill regression.

## Existing structure and rejected directions

- Shared operand-empty stages correctly allow weight and gather producers to
  advance independently until MMA releases their common read lifetime. Separate
  free-stage rings are not automatically an improvement.
- The narrowed relay publication and non-reconverging 80/128/256 register scopes
  are required retained design. The earlier broad cluster release dominated
  K3 stalls; the earlier reconverging donation variant increased spills.
- SF row IDs and row-stride products are already outside K. Wider 8/16-byte SF
  cp.async is not a drop-in: adjacent source words are 512 bytes apart in the
  destination layout. Avoid a new transpose just to widen these copies.
- Earlier direct-payload cp.async versus Gather4 experiments predated the
  broad-fence fix and did not isolate the current bottleneck. They do not prove
  cp.async will lose after R14, but payload-first is a smaller initial test.
- N3U EP W4A4 T16384 uses M256/N128/group2/K256; per-token uses M512/N128/group2/K256
  and regresses much less. This is a signal for issue/reuse amortization, not a
  causal conclusion; arithmetic and epilogue differ between those arms.
- Current FC1 PDL cannot safely prefetch route-dependent weights before its
  dependency wait: moe_sort's early signal does not yet publish routing. Keep
  metadata consumers behind the wait; descriptor-only prefetch is independent.
