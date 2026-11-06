# Cache handoff hold

The qualification owner reported that linking only the four `cached_ops`
directories does not isolate the private workspaces correctly: private
generated/cubin include paths entered the `moe_utils` Ninja description and
triggered a shared C++ rebuild during the remaining exact cases.

The original wide pilot remains sealed. The owner is preserving the interrupted
extra qualification; no performance gate or release has been supplied.

Performance config `1971cb0e` and plan `15b18b6c` remain unchanged. The launch,
close and fetch wrappers have only been syntax-checked locally. No deployment,
private-cache materialization, benchmark or GPU reservation was performed by
this task. Launch stays held until the qualification owner supplies the
corrected canonical generated/cubin input binding, restored normal release
cache/no-op receipts, completed exact/native gate, and GPU/cache release.

The future preflight must verify the actual private-workspace import/build
description against the canonical release identity; a shared-root-only preflight
cannot establish that private-workspace property.
