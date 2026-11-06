# Full manual sanitizer campaign

The completed campaign ran the unchanged tracked `scripts/sanitize_cute_dsl_moe_swap_ab.py` at `d1767be1f42fdc371f90db4fb06598299ea32845`: all 150 cases and the independent full audit passed. `RESULTS.md` records the final result; `SCRIPT-AUDIT.md` and `audit/README.md` document the coverage and evidence boundaries.

- Devbox: `fi-moe-nvfp4-port-1026`, cluster `c3`, namespace `infra`; existing image `nvcr.io/nvidia/pytorch:26.05-py3`.
- Devices: eight B300 GPUs, one active test process per GPU.
- Remote campaign: `/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/api-cleanup-20261028/sanitizer-d1767be1`.
- Source/runtime/native caches reuse sibling `full-validation/{source.json,runtime.json,flashinfer,compile-cache}`. No source deployment or cache reset is needed.
- Compute Sanitizer 2026.3.0.0; exact binary/version/hash and accepted options are recorded in `preflight.json`.
- All 150 unique collected nodes are queued dynamically: five modes, three token counts, memcheck + synccheck + eight racecheck shards. The tracked test owns its six-hour per-node timeout and subprocess cleanup.

Run these read-only status commands from the project root:

```sh
python3 swap-ab-exact-20261027/remote.py api-cleanup-20261028/sanitizer-d1767be1/status.py
python3 swap-ab-exact-20261027/remote.py api-cleanup-20261028/sanitizer-d1767be1/progress.py
python3 swap-ab-exact-20261027/remote.py api-cleanup-20261028/sanitizer-d1767be1/native_progress.py
python3 api-cleanup-20261028/sanitizer-d1767be1/fetch_metadata.py
```

`launch.py` and `driver.py` are the durable launch implementation, not status commands; do not rerun them for a running campaign. `launch.json` records all eight detached driver PIDs. `queue.json` records pending, active, completed, and any repeated global-startup-error pause. A failed case is retained and independent cases continue; three identical recognized global startup errors pause new admission.

Each case has `command.json`, `pytest.log`, `junit.xml`, `completed.json`, and the unchanged tracked worker outputs in `workers/`. A successful case requires one passed JUnit test, no failures/errors/skips, return code zero, and unchanged script hash. The independent auditor additionally validates full catalog identities, racecheck shard union, strict clean summaries, compile/native receipts, and all remaining PTX files. SDK dump filenames can overwrite earlier specializations; complete per-compile hashes/options/entry receipts remain, but the on-disk PTX files are only the final subset. TMEM guards are requested by the recorded compiler option; assembled guard instructions are not separately retained.

The initial shared line-info native builds took about eight minutes; subsequent native/weight setup reuses the persistent cache. All test logs and compiler artifacts stay in persistent storage. `fetch_metadata.py` copies and hash-verifies compact source, command, completion, and JUnit receipts locally; the independent audit owns full raw-log checks and evidence retrieval.

## Additional matching devbox

`fi-moe-sanitize-1028` (C3/infra) runs the same explicit 26.05 image on eight additional B300 GPUs. The initial ziangli request had no quota and was removed before the infra retry. `devbox-request.json` records image selection and request provenance. Retain both devboxes after the sanitizer and independent audit finish: the user requested subsequent TP benchmarks. No benchmark work may start until the sanitizer campaign completes.

After root review, 49 unclaimed racecheck nodes were transferred under the primary queue lock to sibling remote `sanitizer-d1767be1-secondary`. `transfer-secondary.json` is identical in both roots; the original 150-case manifest remains authoritative. The secondary uses the exact same driver, source, toolchain and native cache. No existing active case moved. GPU UUID sets are disjoint.

```sh
python3 swap-ab-exact-20261027/remote.py api-cleanup-20261028/sanitizer-d1767be1/combined_status.py
python3 api-cleanup-20261028/sanitizer-d1767be1/fetch_metadata.py --secondary
```

The aggregate status helper verifies disjoint case ownership and the full 150-case union, prints tool and box counts and findings, and saves detailed worker positions in remote `combined-status.json`. Secondary metadata is fetched locally into `evidence-secondary/`.
