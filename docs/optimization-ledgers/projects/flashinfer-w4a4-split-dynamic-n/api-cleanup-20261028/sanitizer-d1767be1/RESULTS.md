# Swap-AB sanitizer results

**PASS: 150 cases, zero failures, errors or skips.** The unchanged manual suite
`scripts/sanitize_cute_dsl_moe_swap_ab.py` ran at
`d1767be1f42fdc371f90db4fb06598299ea32845`. Independent auditing checked every
worker's raw output, all 15 complete tactic catalogs and racecheck shard unions,
and 347 source hashes. Both postflights confirmed the tracked tree was unchanged.

| Tool | Passed | Failed / skipped |
| --- | ---: | ---: |
| memcheck | 15 | 0 / 0 |
| synccheck | 15 | 0 / 0 |
| racecheck | 120 | 0 / 0 |
| Total | 150 | 0 / 0 |

Each mode (`w4a4`, `per-token`, `mxfp8`, `w4a8`/MXFP4x8, `w4a16`) ran at 1,
8 and 1024 local tokens. Each mode/token pair has one full memcheck case, one full
synccheck case and eight nonoverlapping racecheck shards. Each blockscaled catalog
has 320 tactics; each W4A16 catalog has 23. The campaign recorded **11,727 tactic
visits, 23,454 eager distribution/tactic checks and 46,908 graph replays**, across
300 random/skewed distribution records. Warmup and capture calls are additional.

The workload is GLM-5 geometry: hidden 6144, intermediate 2048, 256 total experts,
top-k 8, emulated EP8 with 32 local experts and local expert offset 32, SwiGLU,
BF16 output, top-k scaling in FC2 and unfused deterministic combine. Every valid
tactic runs random and skewed routing using the same buffers and graph pool;
each distribution runs eager execution and two graph replays. This is a sanitizer
matrix, not an autotuning or numerical-accuracy run.

## Environment and execution

- Two C3/infra devboxes: `fi-moe-nvfp4-port-1026` (101 cases) and
  `fi-moe-sanitize-1028` (49 cases), each with eight NVIDIA B300 SXM6 AC GPUs
  (SM103). One active case per GPU; disjoint GPU UUIDs and case ownership verified.
- Image `nvcr.io/nvidia/pytorch:26.05-py3`; CUDA tools `13.2.78`; driver `595.91.07`.
- Compute Sanitizer `2026.3.0.0`, build `38855100`; Python `3.12.3`, PyTorch
  `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL `4.8.0`, pytest `9.1.1`.
- Native O3/line-info compilation flags and routing symbols were audited. Persistent
  native compilation caches were preserved. Instrumented CuTe compilations bypassed
  the DSL cache as specified by the tracked script. No suppression, source change
  or reduction in the script's instrumentation options was introduced.

The full suite can be reproduced sequentially on one available GPU with the
recorded environment. This command reads the exact saved environment rather than
reconstructing sanitizer options; the tracked script owns those options:

```sh
cd /data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/api-cleanup-20261028/sanitizer-d1767be1
/data/ziangli/flashinfer-cute-dsl-moe-exact-reference/sanitizer-20261027/venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
import subprocess

root = Path.cwd()
source = json.loads((root / 'source.json').read_text())
runtime = json.loads((root / 'runtime.json').read_text())
env = {
    k: v for k, v in os.environ.items()
    if not k.startswith(('FLASHINFER_', 'TRTLLM_', 'CUTE_DSL_', 'FI_'))
    and k not in ('CUDA_VISIBLE_DEVICES', 'PYTHONOPTIMIZE', 'LOCAL_RANK', 'PYTEST_XDIST_WORKER')
}
env.update(json.loads((root / 'environment.json').read_text()), CUDA_VISIBLE_DEVICES='0')
subprocess.run(
    [runtime['python'], '-m', 'pytest', '-v', '-s',
     'scripts/sanitize_cute_dsl_moe_swap_ab.py'],
    cwd=source['repo'], env=env, check=True,
)
PY
```

Actual parallel execution used `driver.py` with one collected node per subprocess:
`<python> -m pytest -v -s <nodeid> --basetemp <case>/workers --junitxml <case>/junit.xml`.
Every exact argv, environment, working directory and source binding is in the
case's `command.json`. `evidence/environment.json` records architecture `10.3a`,
strict DSL cache keys, PDL enabled, `MAX_JOBS=8`, `OMP_NUM_THREADS=1`, and persistent
workspace/Triton cache paths. The 49-case transfer moved only unclaimed nodes under
the admission lock; mirrored receipts prove the original 150-case union remained
complete and disjoint. Both devboxes are retained for the subsequent TP benchmarks.

## Raw aggregate audit output

Exact stdout from `audit/remote-audit-receipt.json`:

```json
{"complete": true, "audit_valid": true, "mode": "raw-worker-and-final-PTX", "pytest_passes": 150, "tool_counts": {"memcheck": 15, "synccheck": 15, "racecheck": 120}, "worker_distribution_records": 300, "failed_cases": [], "missing_evidence": []}
```

The audit report SHA256 is
`ad819c95a41626468f0b6d88b50dfb369e1171d344aa748bb050e65cbd54c318`.
The script SHA256 is
`910b06870c7616a1eb5ec8728feff2691501c66c9776383f9408a0dc86ac20af`;
the source receipt SHA256 is
`4315d60d71f89f8cd67d02a23188488718244251f0f7bf37be832fe2046bc835`.

## Coverage boundaries and evidence

- Memcheck deliberately uses `--check-tensor-ops no`. Every owned GEMM memcheck
  compile requests `-g-tmem-access-check`; compiler options and generated PTX are
  verified, but assembled cubin/SASS guard instructions are not independently proved.
- SDK dump names overwrite earlier specializations. Complete per-compile
  hash/options/entry receipts remain; only the surviving final PTX files can be
  independently checked byte for byte. This limitation did not alter execution.
- PDL is enabled throughout the MoE; PDL-off is not covered. Initial activation
  quantization occurs outside the captured MoE graph. Native ELF symbol evidence
  validates filter names, not execution of every symbol at these token counts.
- Excluded: numerical accuracy, real distributed communication, legacy/non-swap
  kernels, fused/atomic finalize, NVFP4 strict/4over6 quantization, other model
  geometries/activation functions, unfiltered external helpers and SM100 execution.
  Separate numerical/API results are in `../full-validation/tests/RESULTS.md`.

`audit/remote-audit.json` and its receipt are authoritative. Compact commands,
JUnit/completion/source/toolchain/postflight receipts are under `evidence/` and
`evidence-secondary/`. The independent audit's `audit/core-evidence.tar.gz`
preserves raw pytest, sanitizer and worker logs/results plus native build/symbol
receipts: 1,351 verified files plus its manifest, archive SHA256
`eabb9459a4fd51af20611af23af05f897c37563f3377d63e65894bec540878f0`.
`audit/core-evidence-verification.json` binds the final audit and 600 surviving PTX
paths/hashes retained in persistent cluster storage.
The remote roots are siblings `sanitizer-d1767be1` and
`sanitizer-d1767be1-secondary` under
`/data/ziangli/flashinfer-w4a4-split-dynamic-n/c3-20261026/api-cleanup-20261028`.
