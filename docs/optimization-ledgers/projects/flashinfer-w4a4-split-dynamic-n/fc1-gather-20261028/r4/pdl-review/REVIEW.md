# R4 PDL dependency and prefetch audit

Frozen R4 kernel `6fae1558`, host `b0575e7f`, retained base `d35fcfda`. Reconstructed snapshot matches the archived patch and source receipt. No production edits or GPU work.

## Result

Do not turn on `prefetch_weights_before_wait` for gather FC1 under the current routing contract. Expert-selected weight/SFA TMA requires `num_tiles`, the route expert and, for cache policy, neighboring experts. The missing prepare kernel previously acquired routing completion and republished it before its own payload copies; it was that bridge, rather than intrinsic independence of weights, which enabled the old FC1 prewait loads. Direct gather has no equivalent safe routing publication before its dependency wait.

R4 keeps the substantial independent prologue ahead of the wait: pipeline/barrier initialization, cluster join, TMEM allocation/retrieval and shared operand views. FC2 retains prewait weight/SFA loads, scheduling and MMA setup, and its producer-exit signal. FC1 retains startup publication after the routing wait. No extra inter-stage wait was added by the host change. There is no evidence here that removing the required FC1 wait would recover a meaningful measured time; it would violate a supported path.

## Trace of all producers

- `cute_dsl/fused_moe.py` calls `moe_sort` before FC1 using the original top-k IDs and weights. The C++ binding passes those IDs to `routingDeepSeek::run`; the provided-ID branch immediately delegates to `runPostTopKPipeline`, which dispatches the shared custom block, dynamic-block, cluster, cooperative or histogram/offset kernels. Thus the late signal in the DeepSeek *top-k computation* body is not the relevant provided-ID contract.
- The shared block path (up to4 tokens) and eligible dynamic-block path (up to16 tokens) wait for their predecessor, then signal before writing routing maps, experts, limits and counts. Larger cluster permutation, cooperative and final offsets kernels signal after their output loops. The mixed dispatch cannot be treated as a universal completed-routing signal, nor should consumer policy duplicate those thresholds.
- Initial activation payload, linear SF and optional per-token scale are supplied directly by the API. In the benchmark, input NV quantization occurs before routing on the same stream; routing's dependency wait preserves that earlier producer chain. External callers still owe the ordinary stream/event readiness contract. R4 waits before all gather-lane input/map reads and before epilogue per-token-scale reads. Weights/SFA/alpha/global scale supplied by the caller are likewise protected by the ancestor dependency; none is newly made asynchronously ready by removing prepare.
- FC1 waits before reading routing, then its activation-control warp executes the existing release publication and startup trigger. FC2's weight/scheduler roles may therefore access completed routing while its payload-reading roles wait for FC1 output. FC1 does not publish its newly computed activation/SF payload early: FC2 still waits for it.
- In per-token mode, the intermediate quantizer first waits for FC1, releases completed ancestors and signals before its output stores. FC2 may prefetch weights using published routing, but activation/SF/per-token-scale consumers still wait for quantizer completion. The same quantizer entry contract applies when used before FC1; direct gather does not special-case the between-GEMM use.
- FC2's producer-exit path waits for its predecessor when required, republishes ancestors and signals combine. Combine may preload original inverse-map/top-k metadata before its own dependency wait but reads FC2 outputs only afterward. This remains the retained behavior. Fused finalize, W4A16 and non-swap paths are unchanged.

## Remaining independent work

Weight TMA partition/view construction and initial state setup appear syntactically after the wait, and descriptor-cache prefetch could in principle be issued before it. Many of these views compile to constants, so emitted code must first establish a real missed opportunity. Moving them is different from fetching expert-dependent weight payload. Blindly prefetching every expert, duplicating native routing dispatch, or adding a new routing-ready flag/publisher would increase traffic or protocol complexity and is not justified by this source audit.

The unavoidable overlap loss is only the removed prepare bridge's overlap of FC1 weight fetch with prepare's routed copy. The gather design also removes that copy. Comparing those critical paths requires component timing; a startup-wait count alone cannot estimate the net cost. Independent initialization, post-routing activation/weight concurrency and FC2 prefetch remain available.

Source paths and hashes are bound in `receipt.json`; exact source snapshots of the two changed files are under `snapshot/`.
