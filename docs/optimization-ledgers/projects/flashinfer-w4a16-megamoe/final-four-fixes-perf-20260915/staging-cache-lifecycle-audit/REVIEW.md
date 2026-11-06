# W4A16 staging-cache lifecycle audit

**Verdict:** the review identifies retained launch views, but does not establish a stale-address launch or numerical bug on a valid new workspace. A small teardown cleanup can release retained views if desired; clearing every compiled specialization is unnecessary. No source edits, package imports, remote calls or GPU work were performed.

Audited native `979ac4bd532ca1d9e2f5309b3935e77b0759d30d`; all ten relevant files are byte-identical to public `a48e5706c2a7775b0b698aa8eccb4e124b02118c`. Exact SHA records and 20 CPU checks of the real launch-key expression are in `audit.json`. The independent source check by gpu_preparation reached the same conclusion.

## Why exact address reuse is safe for this cache

- `bf16_nvfp4_bf16_cutedsl/staging.py:98` specializes by device, hidden width, top-k and ID dtype. Backend validation fixes the remaining element types. Lines 110–130 compare **all six data pointers, every shape and stride, and the stream** before reusing launch descriptors. Different output storage, input storage, capacity, live count, layout or stream rebuilds them; a new Python object alone does not matter to the kernel ABI.
- If a destroyed allocation is later reused at exactly the same addresses with identical geometry, the old descriptors encode the current intended pointer geometry. They contain no earlier activation/routing values. The compiled kernel reads those addresses on every call. If addresses differ, the key misses. Mere retention of an old descriptor does not launch it between calls.
- `staging_kernel.py:29–30,70–89` launches over the current capacity, rewrites each live row and sets every inactive routing ID to -1. There is no live-count memo or graph-history optimization to survive address reuse. Captured graphs must retire before destruction (`modes/mega_layer.py:42–43,445–449`); a graph replay after freeing its workspace is outside the stated lifecycle contract, and host-cache eviction would not repair it.

The CPU check evaluates the unmodified source AST with pointer-only descriptors: new objects at identical pointer geometry hit; individually changing any of six pointers, shapes or strides, or changing the stream, misses. This tests cache-key construction, not CUDA allocation lifetime or DLPack implementation behavior.

## Teardown and the existing universal path

`core/kernel/base.py:249–275` calls the global invalidation hook only on final pooled release, immediately before physical destruction; nonfinal owners do not free the storage. W4A16 does not override it. `frontend.py:435–441` releases the compiled frontend and explicitly frees symmetric roots, but module-level `_STAGERS` can still hold its latest six launch views.

The analogous universal `shim/quant_stage.py:175–225` also retains compiled stagers and pointer-keyed launch views. Its `forget_staged_tokens()` at lines 80–89 removes only `_LAST_STAGED_N` and `_GRAPH_CAPTURED_BUFFERS`. NVFP4/MXFP8 backend hooks call that function; they do **not** evict `_STAGERS`. Those extra state memos would be incorrect on address reuse, whereas W4A16 deliberately has neither.

## Separate retention question and minimal optional cleanup

CuTe's [public runtime implementation](https://github.com/NVIDIA/cutlass/blob/main/python/CuTeDSL/cutlass/cute/runtime.py) stores a DLPack capsule or TVM-FFI tensor and derives pointer/layout descriptors from it. Such views can extend ordinary Torch storage lifetime. Explicit NVSHMEM free can instead leave a retained descriptor whose raw pointer is temporarily invalid. This supports a lifetime-cleanup concern, not proof that the current cache key later launches at the wrong live address. The fetched public implementation is corroborating context, not a byte-verified copy of the installed 4.7.1 runtime; no exact-runtime retention measurement was performed.

If cleanup is wanted, keep the compiled specialization and reset only `launch_key`/`launch_args` for cache entries whose output-pointer slots 3–5 match the dying workspace's x/topk_idx/topk_weights on the same device. Invoke this through `_forget_workspace_state` before final physical free. A later call then rebuilds views without compilation, including during capture. No new identity cache, generic eviction framework, or full `_STAGERS.clear()` is needed. Full clearing discards reusable compile state and can force a separately warmed live workspace to take the capture fallback.

Suggested classification: **no demonstrated stale-launch correctness defect; optional targeted lifecycle cleanup**. A follow-up test, if implemented, should check final versus nonfinal pooled release and preserve unrelated cached specializations; it should not claim numerical corruption was reproduced.
