# Non-bulk SF copy to TCGEN shared-memory ordering

Read-only audit, retained98fd and installed CuTe4.7.1. No production edit,
new GPU run or reproduced numerical failure accompanies this finding.

Retained core `blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`
loads SFB with non-bulk cp.async at1170–1177, commits its full barrier at1187,
waits at1397, and issues shared-to-TMEM copies at1438–1439. Its proxy fence at1410
is inside the group2 relay branch. One-CTA smallN does not execute that branch.
The actual archived FC1N16 control PTX contains no `fence.proxy.async` instruction.

Installed helpers contain no hidden proxy fence: `pipeline/sm90.py:279`
consumer_wait delegates to `pipeline/helpers.py:511` MbarrierArray.wait, which
calls `cute/arch/mbar.py:286` parity-wait intrinsic. The producer commit dispatches
to cp.async mbarrier arrival. Exact file hashes and source excerpts are preserved
in `inherited-proxy-helper-source.json`; the installed helper is inspected after
unwrapping the DSL decorator to avoid incorrectly identifying its wrapper file.

PTX9.4 defines ordinary cp.async as generic-proxy, whereas TCGEN shared reads use
the async proxy. Its wait_group0 completes the executing lane's copies; warp
synchronization orders participating lanes. A separate async-proxy fence is still
needed before TCGEN reads. Startup fencing only covers earlier padding stores.
See the [cp.async definition](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async)
and [TCGEN shared-memory rule](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-shared-memory-accesses).

The localwait prototype was repaired before GPU launch: all32 lanes execute
wait_group0 → async.shared proxy fence → warp sync, retaining the subsequent
TCGEN execution-order fence. Source7f0fdbc4 is clear for bounded smoke; source
dfcf99ba is preserved unmeasured. This is a specification-level inherited
ordering limitation, not evidence that earlier exact outputs or timings were
wrong. Existing numerical/sanitizer success does not establish the missing
cross-proxy ordering guarantee. Broader retained-source action belongs to root.
