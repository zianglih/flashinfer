# Small-N stage depth and persistent occupancy experiment

Independent `../../flashinfer-small-n-occupancy-review` clone at98fd, one unstaged
core change. No production or public API change. This is an explicitly forced
experimental policy, not a validated generic resource fallback.

The host passes `max_active_clusters=num_sms`; the existing kernel launches that
many CTAs with `min_blocks_per_mp=1`. Reducing shared memory alone cannot provide
two resident CTAs when the persistent grid has only one CTA per SM. The earlier
`small_n_widek_experiment` has a generated widek2 module, but keeps this same grid;
its measured small-N decisions compare3/4 stages and do not test this mechanism.

For existing one-CTA K8 N16/N32/N64 only, set two operand stages, double the
persistent CTA grid, and request `min_blocks_per_mp=2`. TMEM/epilogue ownership,
thread roles, math, preparation, TMA, small-N SF cp.async and public tactics are
unchanged. Every other geometry retains its old branch. No model H/I/token-count
selection or dtype threshold is introduced. Initial admission and timing are
NVFP4 N16/N32 only; no other-format correctness or performance claim.

Before the first candidate GEMM launch, compile control/candidate FC1/FC2 and
require actual SharedStorage <= half device shared memory, TMEM <=256 columns,
zero local memory, and driver occupancy >=2 at the real thread count and dynamic
shared-memory request. Preserve PTX/CUBIN/SASS and register counts. A failed gate
stops the experiment; it does not silently dispatch the old kernel. Only after
admission do bounded byte/SF and native-routing timing checks proceed. Future
promotion would need a clean generic static resource policy and broader exact
coverage; do not implement that refactor before a performance win.
