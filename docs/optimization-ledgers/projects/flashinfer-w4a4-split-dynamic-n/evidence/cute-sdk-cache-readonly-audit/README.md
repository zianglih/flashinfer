# Installed CuTe SDK disk-cache audit

Read-only CPU source capture from the current B300 devbox. No runtime environment or benchmark process was changed.

`CUTE_DSL_CACHE_DIR` is recognized. However, `cute.compile` unconditionally sets `compile_only=True` and `no_cache=True` (installed `base_dsl/compiler.py:1514–1515`). `base_dsl/dsl.py` gates file-cache loading and dumping on `not no_cache`; compile-only also independently forces that flag. `CUTE_DSL_DISABLE_FILE_CACHING=False` is the default and cannot override it.

The FC1/FC2 factories call `cute.compile` and cache the compiled callable in Python with `functools.cache`. This supports within-process reuse, not cross-process SDK file-cache reuse. The configured path alone is not evidence of stored artifacts. No environment-only disk-cache switch was found for this compile entrypoint. A future persistence experiment needs a separately reviewed compile/export/load path or SDK-supported entrypoint; it must not change the current campaign.

Exact source text and SHA-256 values are in `sdk-sources.json`, `sdk-compile-sources.json`, and `review.json`; command/return-code receipts are preserved. Initial transport quoting failure is retained separately and made no remote changes.
