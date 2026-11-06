# Installed IKET owner-loop source check

Captured the exact installed CUTLASS DSL 4.7.1 helper from `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/control-0def601d/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/cute/experimental/iket/iket.py`. SHA256 `fc9a2fcb53e86c30eb381ff5e66f47bca0348af7e3fd140ffafd2155163c244d`; complete source and receipt are `sdk-iket.py` and `sdk-iket-source.json`.

Our scheduler calls `range_push("scheduler_item")` without a payload and matching `range_pop()`. In this installed source, these directly emit `iket.range_push` (line 344) and `iket.range_pop` (line 363). They introduce no Python-side election, shuffle, warp barrier, or collective. The owner branch remains balanced: each loop iteration pushes and pops exactly once, including terminal publication.

This establishes source-level compatibility only. The instrumentation lowering is outside these Python helpers. A separate bounded IKET-enabled 1/2-CTA smoke can verify compilation and marker capture; it must not instrument or contaminate the ongoing timing campaign. Markers remain in production code.
