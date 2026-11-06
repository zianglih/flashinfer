# Direct behavior configuration and producer-exit PDL

Independent unstaged `flashinfer-pdl-behavior-review`, based on corrected retained `aab93f854054de834447bdd8985b8bbd653fb3c8` plus the preserved producer-drain candidate. Production and every earlier candidate remain unchanged.

The two existing public wrappers explicitly select eight internal effects: `prepare_input`, `scatter_output`, `per_token_scale_is_routed`, `k_steps`, `num_stages`, `overlap_epilogue`, `overlap_activation_accumulators`, and `pdl_signal_at`. The last takes `startup` or `producer_exit`; the latter signals before the final producer drain. There is no phase flag, phase enum, generic configuration object, default behavior branch, or new keyword-only separator. Public signatures and activation arithmetic remain unchanged.

The native helper dispatches each arm's actual public wrappers, private host factory/cache, core, epilogue, prep, and finalizer. It pins source bytes and checks function identities and paths. The exact-oracle and timing functions are AST-identical to the prior bounded helper. Native inputs/routing and 10 warmups/100 cold-L2 CUDA-graph CUPTI measurements remain unchanged.

Documented `CUTE_DSL_KEEP=ptx,cubin` and a unique `CUTE_DSL_DUMP_DIR` preserve the actual native compile outputs with unchanged compiler options. Each `cute.compile` result is archived immediately to avoid same-name overwrite; explicit host/preparation caches serve all timed calls. The timer asserts no compilation occurs during capture or measurement. These controls disable the underlying DSL JIT cache, not the explicit compiled-object caches.

CPU review passed 90 caller policies and 9,408 constructor/epilogue/extent cases. Changed-file pre-commit passed. T1 exact with zero-route FC2 canary and T16384 native exact passed. The T4/T32/T128 N16 and T4096/T16384 N256 adjacent corrected-aab ABA/BAB screen is running on new-node GPU2. No primary AUTO, original baseline, or TRTLLM rerun is part of this bounded screen. No historical cross-node TRTLLM speed claim is made.

The T1 guard used source epoch r1. Pre-commit then required merging two identical FC2 stage-selection branches with `or`; epoch r2 changes only that host expression, with all kernel/epilogue/preparation bytes unchanged. The complete policy audit re-passed. Both epochs, hashes, and the original T1 receipt are preserved.
