# Inventory reconciliation audit

Passed independent reconstruction against Git blob contents, including all four exact primary submodule commits. Current is `14a338579eb8acddcc5cfd1cc58871fc0788de22`; before is `002529e17b22567a071091053c6c4dc2a55e050e` with only the preserved benchmark overlay `8078d09b8be9c5a992d8904ffc59fbcdb28fd2e34324a69e4fe250ed79477eab`.

Both corrected manifests have zero changed hashes for existing paths. Each moves 542 CUTLASS documentation assets (530 HTML, 12 MD5) from erroneous top-level `docs/` paths to `3rdparty/cutlass/docs/` and adds three tracked CCCL symlinks (two instruction documents and a license). All patch archive members and link targets match Git. Current has 34,762 content-file entries, before has 31,069. Neither kernel source nor runtime/compiler headers change, so this inventory repair introduces no runtime code confound.

The exact inventory covers regular files and file symlink target contents. It intentionally omits two tracked CCCL directory symlinks (`.claude/skills`, `.devcontainer/cuda13.3-rapids-conda`) instead of traversing them; these are tooling/documentation paths, not kernel inputs.

`reconcile_manifests.py` is a one-shot helper: rerunning it without a guard would overwrite saved historical manifests before failing its 545-added/542-removed assertion. Existing outputs remain correct. Parent was notified to avoid rerun or add an early existence guard. Detailed checks and hashes are in `manifest-independent-audit.json`; audit implementation is `audit_manifest_inventory.py`.
