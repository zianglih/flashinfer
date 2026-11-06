# Compilation-cache audit

The native84-cell retune used3271 observed compile API calls. Summed job wall time5265.93s comprises4076.59s inside compile APIs (77.41%) and668.79s exclusive profiling machinery (12.70%); these are aggregate process times across parallel workers, not elapsed wall time or compiler-backend-only CPU time.

All nine native C++ cache links point to persistent /data project storage and survived the devbox replacement. The installed CuTeDSL4.8.0 `cutlass/base_dsl/cache_helpers.py` resolves its separate file cache to `/tmp/root/cutlass_python_cache` unless `CUTE_DSL_CACHE_DIR` is set. That cache was ephemeral. This was checked from the installed package, not inferred from the newer reference checkout.

Future experiment launchers should set:

```sh
CUTE_DSL_CACHE_DIR=/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/fc1-gather-20261028/compile/cute-dsl-4.8.0-cuda13.2-sm103
```

The new directory is version/architecture scoped and deliberately starts empty; copying live partially written temporary compiler files would be unsafe. Keep `FLASHINFER_CUTE_DSL_STRICT_CACHE_KEY=1`, source manifests and runtime register guards. Leave fresh-codegen `no_cache` diagnostics unchanged. Do not alter in-flight campaign environments or receipts. No production source or global environment was changed by this audit.
