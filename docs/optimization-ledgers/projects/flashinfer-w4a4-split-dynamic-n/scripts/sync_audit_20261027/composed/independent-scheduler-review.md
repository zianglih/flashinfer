# Independent final composition review

Reviewer `/root/flashmla_clc_audit`, 2026-10-27. **Approved; no source blocker.** Exact patch and file hashes are pinned in `independent-scheduler-review.json`.

Byte comparisons establish that the three-file diff is exactly:

1. Frozen operands V4 (unused SF ring removed, SF readiness folded into existing full completion, explicit16-byte metadata alignment), plus terminal barrier2 removal and cleanup admission narrowed to allocator warp0.
2. Frozen independent bulk-stage wait motion in `utils.py`.
3. The single quantizer barrier deletion previously independently reviewed.

No other source files or untracked files are present. No MegaMoE/Rubin/API/tuning-policy changes are included. All three Python files parse.

The folded operand protocol keeps local SF completion/proxy publication and explicit cluster acquire, with the existing empty multicast preventing phase reuse; the separately saved independent operands V2 review applies unchanged. V4 additionally expresses the metadata object's16-byte alignment directly and retains the same slots/participants. The installed-SDK layout check covers actual offsets and the planner bound.

After barrier2 removal, `warp == 0` expresses the SDK's actual allocator ownership. Both helper calls already guard their device work to allocator_warp_id0. Their peer-deallocation handshake has32 arrivals, not128. The final all-CTA barrier1 still drains all other roles before this warp enters cleanup, and every allocator lane participates. Compile-time free bookkeeping still executes once while tracing the helper; this is not a runtime count change.

The bulk reuse wait and128-thread join remain before the first shared overwrite. Independent TMEM loads/packed-register conversion precede them; the early accumulator-release fence and all later publication/drain steps remain unchanged. The quantizer retains its cross-row reduction-scratch barrier, and no thread reads the published per-token scale during the same quantization pass.

The final composed source still requires its own exact/codegen gate and model screen. Separate source results must not be reported as final composed measurements.
