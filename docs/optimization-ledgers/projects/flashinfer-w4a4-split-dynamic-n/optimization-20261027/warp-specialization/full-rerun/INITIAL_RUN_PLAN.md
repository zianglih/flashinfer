# Conditional full PR-table rerun

R2 is retained as `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`. All eight
workers are now active on GPUs0–7 after source/cache/CUPTI and idle-GPU preflight.
Frozen config: `0e497a5d623027316c423b02b19a62e061da6ba4bcca751f1e7d11d5a05c770b`.
The clean retained checkout has341 source files byte-identical to gatedR2;
the sole frontend diff is two local type annotations and required formatting.
The freeze independently verified recursive runtime bytecode equivalence and
pinned the parent's narrowly scoped AST/bytecode receipt. The completed pilot's
208 native CuTe winners are preserved unchanged; every full-table timing is new.

- Four models: V3 EP8, V41F EP4, K3 EP8, N3U EP8.
- All 13 token counts: `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`.
  Tokens 1/2 appear in raw output but remain excluded from the 44-row summary
  and retention decisions.
- Eight model/family workers on GPUs 0–7, in model order, NV then MX.
- Same current-PR arm matrix: swap-AB unfused versus TRTLLM, unchanged non-swap
  modes, and pre-PR W4A16. Legacy MX uses fused finalize where required and is
  marked `†`; unsupported K3 baselines stay N/A. W4A16 remains in the table,
  without attributing an improvement to this kernel refactor.
- Native CuTe selections from the completed R2 pilot cover all 13 public token
  keys. Reuse those selections only after source, receipt, cache, profile and
  key-geometry proof. W4A4/per-token caches merge only with identical metadata
  and nonconflicting records; the generation digest follows native AutoTuner
  serialization. Ordinary AUTO then fills missing TRTLLM/W4A16 selections.
  Legacy/pre-PR selections are copied from the prior completed full campaign
  after exact source/workload equivalence checks.
- All full-table measurements are fresh: 10 warmups, 100 cold-L2 CUDA-graph
  CUPTI samples, event fallback prohibited, frozen C-A-A-C pass medians. Native
  tuning remains eager for NV and graph-based for MX. NV includes the input
  quantizer; MX inputs remain prequantized. No pilot or older timing enters the
  final tables.
- Reuse the verified source-private R2 CuTe namespace after content equivalence
  to the clean committed checkout, and the persistent native C++ cache. Never
  delete caches. The CPU freeze verifies all native source hashes and link
  targets before reusing the existing native artifacts.

Expected output remains eight raw A2 CSV sections and a 44×9 summary. The
unchanged observer verifies all CuTe/TRTLLM saved cache hits and 100 sample
medians. The adapted assembler checks raw CSV verbatim, all fresh sample hashes,
15 unchanged control winner donors, and eight R2 candidate selection seeds.
Phase structure remains 8 AUTO invocation phases plus 46 frozen phases:
442 AUTO medians / 44,200 samples and 1,352 frozen medians / 135,200 samples.
The AUTO phases may hit pilot CuTe winners rather than performing a new search.

## Reproducible commands

First generate and upload the helpers. `make_deploy.py` only generates the
upload script; `deploy_remote.py` only writes a new remote artifact directory.
Both refuse existing destinations.

```sh
python3 optimization-20261027/warp-specialization/full-rerun/make_deploy.py
python3 swap-ab-exact-20261027/remote.py \
  optimization-20261027/warp-specialization/full-rerun/deploy_remote.py
```

On the devbox, once the parent has supplied `current-source.json` for the clean
retained commit (including verified source/native-cache provenance):

```sh
python3 tools/freeze_config.py --current-source current-source.json \
  --pilot ../performance --previous ../../retained-rerun --output config.json \
  --source-equivalence-receipt ../retained-deployment/commit-bytecode-equivalence.json
python3 tools/launch.py --config config.json \
  --approved-config-sha256 <frozen-config-sha256> --approved-head <retained-commit>
```

Preserve the entire new campaign root, including `seed-winners`, configuration,
current-source receipt, launch/helper receipts, every raw log/results file and
winner cache. Keep the completed pilot and previous full-campaign evidence in
their original local locations; the assembler reads their selection proof,
never their timing values for aggregation.

After fetching fresh evidence to this directory's `evidence/`:

```sh
python3 optimization-20261027/warp-specialization/full-rerun/assemble_results.py
```

Do not update the PR until all eight receipts and final assembly verify. Do not
silently resume failed phases or replace existing artifacts; preserve each
attempt and assess any failure before a separate rerun.
