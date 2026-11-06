# WG2 token-pull visibility in the current rank2 trace

The current HashInfer40d0ceb rank2 trace contains one `dispatch_fetch_input_tokens` slice: CTA(0,0,0), warp8, 14.432–23.488µs relative to the first recorded range, lasting9.056µs. It is nested inside `dispatch_exchange_tokens` after `dispatch_exchange_counts_sync`. The outer exchange and local staging ranges each appear on all eight recorded WG2 warps (warps8–11 in each of the two CTAs).

This uneven visibility comes from the marker guard in inherited `token_comm.py:1559`: `cta_linear_id == 0 and local_warp_idx == 0`. That guard covers the count, publication, pull and optional return phase labels. It does not guard the real `dispatch_pull` call at1606. The owned W4A16 subclass inherits this method unchanged. The kernel invokes the dispatcher on warps8–11 at `megamoe_kernel.py:1442–1463`.

WG2 first stages local BF16 inputs and routing data. The pull helper then fetches its assigned source tokens (from the appropriate local/peer staged buffer) via TMA into per-warp shared storage, stores them to the local expert FC1 pool, carries routing metadata/weights, drains stores and publishes FC1 readiness. The9.056µs range includes the whole helper, including bookkeeping and waits; it is not a pure NVLink transfer measurement.

Thus missing pull labels on warps9–11 or CTA1 are a marker-coverage limitation, not evidence that these warps skip the helper. Per-token markers were previously omitted because lane-guarded markers in divergent loops caused native IKET patch-point/event problems. That limitation is distinct from marking the whole warp-uniform helper call on each participating warp, which would be the narrow improvement if expanding coverage.

This investigation is read-only for source/PRs and reuses the existing capture. No new GPU run or trace is claimed. Exact ranges and trace hash are in `rank2-ranges.json`.

## Startup versus sustained activity

In the same instrumented rank2 capture, all eight recorded WG2 outer dispatch ranges finish by23.520µs. Every recorded WG2 warp enters `cta_wait_all_roles_finished` at24.064µs and leaves at532.960µs. The recorded leader CTA issues MMA from25.280 through528.544µs. Thus these two CTAs finish input pulling before their first MMA and WG2 spends the main compute interval waiting. Times are relative to this rank's first recorded range and are not uninstrumented benchmark latencies or evidence of all-grid completion.

This is a finite input-dispatch pass: each assigned token/expert route is fetched into the FC1 pool once. Here128 global tokens×8 routes÷4 ranks=256 received routes/GPU, versus148 CTAs×4 dispatch warps=592 dispatch warps, so each active warp pulls at most one route. Larger workloads can keep the pull loop active longer and overlap early FC1 work, since the scheduler is released before pulling and tile readiness is published incrementally. Warp6 activation TMA continues loading local FC1 input / FC2 intermediates through the compute pipeline; that is distinct from WG2 token dispatch.

The selected `epi_warps` tactic returns FC2 outputs through epilogue warps. A `reuse_dispatch_warps` winner can keep WG2 busy waiting for and pushing output tokens after the finite input-pull pass; that continued activity is output return, not continued input pulling.
