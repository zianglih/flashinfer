# GPU and artifact handoff

Both the GLM5 CAAC measurement and the focused consolidated accuracy run have
finished. All eight GPUs were verified idle afterward (0MiB,0% utilization).
No sanitizer or new optimization experiment was run.

- Managed devbox: `fi-mega-scale-1029`, cluster`c2`, namespace`ziangli`.
- Invoke `/usr/local/bin/h` from `/Users/ziangli/playground/repos/hai`; no
  repository-local HAI executable. Use the existing node rather than request
  another allocation.
- Image/runtime: `nvcr.io/nvidia/pytorch:26.05-py3`,8×B300,CUDA13.2,driver595.91.07,
  CuTe DSL4.8.0,PyTorchNGC26.05,NVSHMEM3.6.5/4Py0.3.1,CUPTI13.2.0/13.2.86,
  pytest8.4.2. Exact package versions are in `runtime.json`.

Remote task root:

```
/data/ziangli/flashinfer-w4a4-split-dynamic-n/upstream-integration-20261029/megamoe-glm5
```

Its `test-consolidation/source` is the prepared source with production4376662a
and the final consolidated test file (SHA256
`5a8b73eb23da42036522aacfda774785672c50f463c2ee94dce9743453b80e01`). The baseline
`current` is clean437 production with the earlier test file; `control` differs
only by the old dequantization helper. These benchmark snapshots need no more
GPU work. Keep only sources still needed by active follow-up experiments.

After the focused run, all13,245 tracked-file contents were compared with
pushed commit`658a0c8942c7454050f990c0be3083aa61b6a89f`: no differences. Compared
with the measured437 candidate, only the consolidated test file differs.
`test-consolidation/full-source-attestation.json` records this and the final
all-eight-GPUs-idle snapshot; `tested-tracked-manifest.json` holds every hash.

Persistent caches under that root:

- `cache/cpp` is `FLASHINFER_WORKSPACE_BASE`; native objects are under
  `.cache/flashinfer/0.0.0+unknown/103a/cached_ops` and fetched cubins/headers
  under `.cache/flashinfer/cubins`.
- `cache/driver`, `cache/triton`, `cache/cute-focused-tests` are the driver,
  Triton and focused-test DSL cache locations.
- The native MegaMoE direct-compile path did not populate its separate
  `cache/cute-control`/`cache/cute-candidate` directories; do not claim cache hits.
- Switching distinct source paths changed native build commands and rebuilt
  C++ objects. For Python-only follow-ups, immutable shared include/csrc links
  can keep those paths stable while Python kernel files differ. No cache needs
  deletion.

**Sync only to a dedicated leaf.** `h sync` removes remote files absent from the
local source directory. Syncing a small helper directory to this entire task
root would delete its remote source/cache siblings. Single helper updates can
use `h ssh ... python3 -c` with a base64 payload instead.

Local result artifacts:

- `public/` and `pr-section.md` are frozen for root's immutable publication.
- `summary.json`, `summary.csv`, `logs/*.log`: full raw qualified benchmark.
- `test-consolidation/pytest.log`, `run.json`:92 passed,1132 deprecation warnings,
  exit0,633.19s. Source hash is unchanged before/after. Benchmark completed
  `2026-10-30T04:57:10Z`; tests started`04:58:49Z`, so there was no overlap.
- `codegen-proof/`: native representative16k SASS and resources, independently
  audited. Final C2/A2 cubin hashes match C1/A1 byte-for-byte; receipt is
  `final-codegen-hashes.json`.
- Adjacent `../perf-audit/` contains independent source, codegen and full-data
  audit receipts.
