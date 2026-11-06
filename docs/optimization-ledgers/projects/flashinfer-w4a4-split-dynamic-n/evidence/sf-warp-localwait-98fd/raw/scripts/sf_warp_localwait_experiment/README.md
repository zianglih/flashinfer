# Warp3 local completion instead of a self-handoff

Final bounded refinement of frozen warp3 core2c4fee74. Independent actual-source
clone `flashinfer-sf-warp-localwait-review`, base98fd, two unstaged files.
The physicalN16/compactSFB epilogue is unchanged. Only the enabled generatedFP4
gatedNVFP4 FC1N16 publisher body changes: per-thread `cp_async_commit_group`
replaces its32-participant full arrival; every lane executes
`cp_async_wait_group(0)`, per-lane `fence_proxy("async.shared", space="cta")`,
then all32 lanes `sync_warp`, replacing its full wait.
No elected-lane-only wait is used. Every lane's eight SFB copies complete before
the elected TCGEN CP can read all rows. Invalid route/K groups still zero-fill.

The startup generic-store→async proxy fence and warp sync remain. The existing
SFA-full wait, TMEM-empty acquire and `tcgen05.fence::after_thread_sync` remain
before CP. TCGEN completion still releases the shared SFA/SFB source-empty;
MMA completion protects both TMEM SF slots. A/B issuers remain independent.
Source four-stage ring, two TMEM SF slots,288threads,stage counts and all iKET
markers are unchanged. The unused SFB full-barrier initialization is retained
so this experiment isolates the hot-path handoff; acquire/tail use only empty.

PTX §9.7.10.28.3.3 defines cp.async.wait_group's per-thread completion/visibility;
§9.7.15.2 defines bar.warp.sync ordering among participants:
https://docs.nvidia.com/cuda/parallel-thread-execution/
Completion reasoning is source-reviewed separately before GPU launch.

GPU2, replacement B200-92, adjacent98fd controls only. Commands:
`run_smoke.sh` then `run_pairs.sh`, using fresh private CuTe cache and unchanged
native epoch. Reuse the seven frozen baseline oracle cases (no baseline rerun),
compile/run per-token fallback and nativeT32 full exact before timing. Then
nativeT32/T128 fixedN16 ABA/BAB with10warmups/100cold-L2 graph CUPTI samples,
full outputs exact before/after everyarm. Initial quantization outside timing;
regular preparation inside fullchain/FC1. No AUTO or oldTRT comparison.
Prior warp3 screen/source/failure receipts remain unchanged.

Prelaunch review added the per-iteration generic→async proxy fence because
ordinary cp.async writes and TCGEN CP shared reads use different proxies.
The startup fence covers only initial odd-word stores. Pre-fence source
`dfcf99ba` was never launched and is preserved under history/r1-unmeasured-proxy-fence.
Measured source `7f0fdbc4` uses fresh r2 module/cache identity.
