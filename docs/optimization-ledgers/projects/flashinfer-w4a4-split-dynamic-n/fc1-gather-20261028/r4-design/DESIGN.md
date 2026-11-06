# Dynamic-N Gather4 prefix: read-only proposal

Source reviewed: R3 kernel `c259b6cb4b01037def6f1b8d4be09221f7abc36dd76e910660ced0179daebf75`. No production source edits or GPU runs.

The prefix reduction is legal. For each live route tile, use `padded_n = (valid + 15) & -16` and `payload_rows = padded_n / cta_group_size`. Preserve the existing physical B row pitch, K-slab stride, stage stride, allocation, descriptor and full local SFB atoms. Native MMA rounds N to `8 * cta_group_size`; the proposed16-rounding exactly matches group2 and conservatively transfers up to8 extra rows for group1.

The leader's sole-announcer count becomes:

```
cta_group_size * ((128 * tile_k * weight_dtype.width / 8 + sf_stage_bytes) * channel_tiles)
    + padded_n * tile_k * activation_dtype.width / 8
```

Keep the existing weight transfer-width expression, including mixed FP4-to-byte storage: SMEM storage width is not its TMA transaction width. Group2 contributes `payload_rows * tile_k * activation_bits / 8` from each CTA; all completions still target the leader. The pending weight arrival protects early negative transaction counts exactly as before. Each TMA command still transfers its full128-byte row chunk, including OOB zero-fill, so a short finalK stage retains full `tile_k` transaction accounting.

Weight warp obtains the same `valid` already used by gather/MMA: retain `scheduled_valid` from CLC metadata; use one `mn_limit` read per static route tile. Compute the rounded prefix once before K. Only the gather specialization needs the value; FC2 keeps its existing static byte count and does not acquire a new limit read. Empty routes/terminal tickets still execute no operand stage. Stage count, state advances, reuse, SF readiness and teardown do not change.

## Minimal implementation and tradeoff

Keep R3's compile-time row/K task decomposition and additionally require `row_base < payload_rows` before issuing Gather4. Apply the same bound to hoisted mapping reads. This avoids runtime division and retains the current coordinate register allocation. It removes unused payload commands, source mapping reads and shared zero-fill traffic. It does not reduce full-SFB cp.async work or the existing per-stage SF wait.

The cost is one uniform live-prefix predicate at each statically emitted command site, a small per-route rounding calculation, and dynamic transaction-byte arithmetic in the weight warp. Full route tiles gain no transfer reduction and therefore need performance measurement. The existing ring and synchronization need no modification.

For a nominalN256/group2/K512 FP4 tile, valid1 reduces each CTA's Gather4 commands64→4 and the group payload65,536→4,096 bytes per stage. Valid33 gives64→12 commands and12,288 payload bytes. These counts describe payload traffic, not total GEMM traffic or promised speedup.

One ownership caveat: retaining R3's static row-fast ordering uses only two payload warps when the live group2 prefix has eight rows per CTA, even if two K chunks provide four commands. All four warps still gatherSF. A universal K-fast task order restores four payload issuers, but doubles the hoisted coordinate groups per warp for wide Ksteps8 tiles. Dynamic row-fast flattening instead introduces non-power-of-two runtime division/modulo and irregular cache indexing. Neither is a free simplification; the first prefix-only ablation is cleaner unless four active payload issuers is a hard requirement for every nonempty task set.

`proof.json` enumerates3,968 geometry/live-N cases: every consumed MMA row is covered, each issued row/K chunk is unique, issued bytes equal the dynamic announcement, and physical stage bounds remain unchanged. Hardware exact/codegen/performance qualification would still be required.
