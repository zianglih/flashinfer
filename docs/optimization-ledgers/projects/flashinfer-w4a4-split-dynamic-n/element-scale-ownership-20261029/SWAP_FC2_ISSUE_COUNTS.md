# Swap FC2 TMA issue-count audit

Read-only audit of control `658a0c89`, frozen A `02031c5f`, and B `15d9533f`. No source changes, compilation, GPU work, or performance inference. The replayable [audit](audit_swap_fc2_issue_counts.py) binds both full source hashes, both triage configs, all frozen inputs, and the 56 selected swap FC2 cells in [JSON](swap-fc2-issue-count-audit.json).

The proposed `(2C, 2) → (C+1, C+1)` count is correct only when activation scales occupy one 128-row block. The general count needs `R`, the number of activation-scale row blocks per CTA:

- `C = max(1, logical_M // 256)`: sequential logical channel tiles.
- `Nalloc = max(32, route_tile)` and `R = max(1, Nalloc // 128)`.
- `G = physical_M // 128`: existing one/two-CTA MMA group. Elements B contain `route_tile/G` rows per CTA; **SFB remains full N in each CTA**, so its count is `R`, not `R/G`.

| FC2 producer ownership | Warp 0 issues/K/CTA | Warp 1 issues/K/CTA | Maximum |
|---|---:|---:|---:|
| Control: A+SFA / B+SFB | `2C` | `1+R` | `max(2C,1+R)` |
| A: A+B / SFA+SFB | `C+1` | `C+R` | `C+R` |
| B: A+SFB / SFA+B | `C+R` | `C+1` | `C+R` |

Total copies remain `2C+1+R`. The maximum decreases exactly when `C>R`. Both variants have the same count balance; A versus B changes which descriptor/payload work shares a warp. Across a complete CTA group, multiply issued copies by `G`; the cooperative TMA opcode does not remove the per-CTA issue or SFB replication.

Source: [geometry and SFB replication](../flashinfer-element-scale-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:1573), [one A or SFA copy per channel tile](../flashinfer-element-scale-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:2569), [one B copy versus R SFB copies](../flashinfer-element-scale-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:3156), and [the explicit one-instruction SFB helper](../flashinfer-element-scale-review/flashinfer/fused_moe/cute_dsl/blackwell/moe_swap_ab_kernel.py:173). The control issues both A and SFA inside that channel-tile loop; the total expected-byte announcement is unchanged.

## Frozen triage coverage

This is the selected 4/4096-token matrix, not all possible tactics. The 16 W4A16 cells are outside this swap-only count.

| Geometry | Cells | Control | A | B | Maximum change |
|---|---:|---:|---:|---:|---:|
| C1, R1 | 33 | 2 / 2 | 2 / 2 | 2 / 2 | None |
| C1, R2 (N256) | 11 | 2 / 3 | 2 / 3 | 3 / 2 | None |
| C2, R1 | 12 | 4 / 2 | 3 / 3 | 3 / 3 | 4 → 3 |

Thus 44/56 cells have no reduction in maximum logical issue count. The 12 C2/R1 cells are K3 EP W4A4 4096; V41F EP W4A4 4096; K3 TP W4A4 and per-token at 4/4096; V3 TP W4A4, per-token, and MXFP4x8 at 4; V41F TP per-token at 4/4096 and W4A4 at 4096. All 12 use two CTA. The JSON retains each exact native tactic, route hash, N and K-step setting.

## Lowering and interpretation limits

These are logical TMA issue counts per K stage, not counts of all setup/control instructions or a cycle model. Existing saved old-producer PTX supports the one-instruction-per-copy interpretation: `control128-epilogue248-ce4/evidence/native-1/control/capture/001-fc2.ptx` has C2/R1 with two A and two SFA issues per weight stage and one B plus one SFB; `native-0/.../001-fc2.ptx` has C1/R2 with one A/SFA pair and one B plus two SFB issues. Their source/capture geometries and PTX hashes are recorded in the JSON. These historical examples are not fresh A/B codegen qualification or a claim about every compiled specialization.

For C1/R1, there is no issue-count imbalance to fix. C1/R2 was already only one issue apart and retains that maximum. A/B still change dependency scheduling, descriptor work and payload sizes, while adding cursor/refill/polling control to preserve PDL runahead. Conversely, C2/R1's 4→3 count is only a possible issue-efficiency opportunity: weight and scale copies have different byte counts, readiness and completion latency, and the two producers need not be simultaneously runnable. Use the measured per-FC and end-to-end results to decide; do not predict a speedup or identify a bottleneck from this count alone.
