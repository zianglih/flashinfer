# Independent regular-TMA FC1 audit

Audited 2026-10-25 against production `442d2aa53f68b4640c3ab5118a76f1599ff60d34`.
This is a source and CPU address-algebra review, not GPU validation. No production,
prototype implementation, or test source was changed. Exact audited file hashes
and source-equivalence checks are in [independent-audit-receipt.json](independent-audit-receipt.json).
The design contract is [FEASIBILITY_442.md](../prepermuted_tma_audit/FEASIBILITY_442.md).

**Disposition:** no new bounds, scale-indexing, or pipeline-lifetime defect found
for the current serialized experiment with valid `moe_sort` metadata. Scratch
ownership needs an explicit production contract. N16 boundary and changing-route
replay coverage remain useful before broad integration.

## Source-supported checks

- **Payload preparation:** `prep.py:28–30,75–82` copies raw 16-byte vectors; it
  does not reinterpret FP4 nibbles or perform numerical conversion. Row size and
  pointer alignment ensure each vector stays inside its row. Invalid rows are
  zero-filled; Int64 row offsets avoid 32-bit byte-address arithmetic.
- **Live metadata only:** `prep.py:55–74` bounds mapping reads by both the current
  active padded extent and the absolute tile limit. SF-atom padding and the N16
  extension cannot read poisoned mapping slots. This assumes the existing sort
  contract: `0 <= num_tiles <= capacity / route_tile`, valid limits, and in-range
  original token IDs for live routes. The host checks metadata storage, not device
  values (`prep.py:131–134`).
- **Complete SF atoms:** `prep.py:63,83–92,107,129` initializes and allocates whole
  128-row atoms. Its UInt32 offset is the feasibility note's canonical byte
  offset divided by four. An independent CPU enumeration of 900 geometries
  found unique, contiguous, bounded SF-word coverage. Every invocation overwrites
  its current physical payload extent and complete reachable SF atoms. Stale
  suffix capacity is not consumed under serialized reuse.
- **Short K:** accepted inputs require `K % (4 * sf_vec_size) == 0`
  (`prep.py:104,137`), so there are no extra canonical source K-padding bytes.
  A final stage wider than K still requires descriptor-bound zero fill. The
  regular core retains the existing three-axis SFB descriptor and its Int32 K
  axis (`regular_core.py:749–774`); this prevents a short K load from spilling
  into the next row atom. Payload TMA uses the actual K extent.
- **N16 physical N32:** `prep.py:58–63` initializes 16 extra payload rows when
  allocated, clipping at capacity. At full capacity, the regular descriptor's
  exact `num_routes` row extent provides OOB zero fill
  (`regular_core.py:539,557–560`). Within active capacity, extra rows can belong
  to the next tile; dynamic N and epilogue validity predicates exclude them.
  Quantization reduces channels for each token, not across these inactive token
  lanes (`utils.py:563–598,612–653`). The final SF atom is also initialized.
- **Group 2 and dynamic N:** the regular B partition is the frozen FC2 path
  (`regular_core.py:1087–1112`). After the CTA partition offset, CTA rank `r`
  starts at `route_start + r * align16(valid) / 2` and loads `allocated_n / 2`
  rows. All 768 `(N in {128,256}, valid, rank)` address cases stay within that
  route tile; the MMA consumes the active halves. N128/N256 starts are aligned
  to complete SF atoms. Each CTA receives the full local SFB row blocks, matching
  group-2 S2T's requirement (`349–359,1253–1268`).
- **Transactions and lifetimes:** regular TMA changes the producer count from
  four Gather4 arrivals to one and adds full local SFB bytes to the group-wide
  expected transaction count (`972–988`). Both NB2 MMAs precede operand-stage
  release (`1607–1662`). Source comparison confirms the post-loader lifetime
  code, shared-storage declaration, custom pipelines, and epilogue are unchanged
  from 442, apart from the epilogue module's import path. TMEM allocation,
  overlap protection, 128-thread free collective, and payload/SF storage sizes
  therefore retain the existing contracts; this review makes no register-count
  or generated-code claim.
- **Original-token scales:** the new activation source extent is routed capacity,
  while `per_token_scale` keeps the original token extent (`539–544,613–617`).
  Both gated and Relu2 epilogues still index
  `per_token_scale[token_mapping[row] // top_k]` (`utils.py:568–570,615–620`).
  `install.py:47–49` preserves those arguments. Activation math and FC2 remain
  unchanged.

## Integration and validation boundaries

- **Scratch ownership is the substantive integration issue.** `install.py:37–45`
  reuses one scratch pair per device, dtypes, capacity, K, and SF vector size.
  Concurrent same-shaped streams or graphs would alias that pair. The current
  serial diagnostic is safe; production needs execution/graph-owned workspace
  or explicit serialization, with storage kept alive through GPU completion.
  Global function interception and variant selection are also experiment-only.
- **Capacity cost remains real.** Allocation uses graph-safe route capacity, not
  a host read of the live count. Scratch bytes are
  `capacity * packed_payload_row_bytes + ceil128(capacity) * K / sf_vec_size`.
  The installer retains separate capacity/format entries even after
  `torch.cuda.empty_cache()`. Native performance evidence must include preparation
  and account for peak retained workspace; `probe_native.py:212–235` does include
  preparation inside each full-chain timed call and prewarms the selected arm.
- **Focused coverage gaps in the audited probes:** core probes independently
  zero the entire routed capacity, so their exactness cannot detect incomplete
  preparation. `probe_prep.py` covers count 3 then 0, N16/128/256, poisoned
  padding, and suffix guards. It does not cover a changing nonzero live count
  during graph replay, N32/64, N16 at full capacity, or N16 active rows 128 with
  the physical extent reaching 144 and a second SF atom. These are validation
  boundaries, not source-proven defects. A small prep-to-core replay sequence
  that grows, shrinks, reaches zero, and regrows would cover the new lifetime
  contract more directly than repeating the frozen 442 matrix.
- Zero-capacity calls, arbitrary externally supplied invalid metadata, concurrent
  graph execution, and fused finalize are outside this audit's supported scope.
  The current preparation launch expects a positive capacity even when live
  routes are zero. No GPU execution was performed for this review; reported
  device passes from the implementation agents are separate evidence.
