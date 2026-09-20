# d1 numerical failure capture and CPU replay

**Status: original strict cross-path check FAIL; no performance result.** This bundle retains the complete eight N1/N3 rank tensors and all 38 diagnostic execution files unchanged. N1 passes, while N3 fails at 2 / 18,432 output elements with the original `atol=rtol=0.01`. The diagnostic worker exits 1 by design after preserving that failure. CPU analysis exits 0; that means the saved tensors were analyzed successfully, not that the GPU correctness gate passed.

- **Observed cause in these captures:** inputs, routing and all BF16 FC2 route terms agree bitwise (49,152 N1 terms; 147,456 N3 terms). Mega's K-order FP32 fused multiply-add followed by BF16 rounding and Split's owner-local accumulation followed by BF16 partials both replay exactly. Different collective/BF16 rounding reproduces the two final failures. See [findings](FINDINGS.md), [full arithmetic checks](cpu/analyses/glm52-numerics-20260920-d1-cpu-r1/analysis.json), and [two-element replay](violating-collective-replay-steps.json).
- **Scope:** GLM preset H6144/I2048/E256/K8, EP4, all-gather Split, live Mega capacity; N1/N3 eager capture on four NVIDIA B300 GPUs. Benchmark source `6f88c235b658104053761aad15158e954f439a41`; unchanged FlashInfer runtime base `ad0a5e5e78e57070ec7c582efe733cb55cd8839f`. Torch `2.13.0+cu130`, CuTe DSL `4.7.1`, loaded NCCL `2.29.7`; [exact invocation, environment and helper hashes](evidence/diagnostics/glm52-numerics-20260920-d1/provenance.json).
- **Limits:** d1 reproduces r3's PASS/FAIL and error aggregates, but r3 retained no tensors. d1 snapshots and skipped timing/graphs alter execution state. Candidate BF16 trees reproduce the saved NCCL outputs; the actual NCCL schedule was not captured. This is neither a tolerance relaxation nor GPU performance/model-quality evidence. The capture does not time kernels.

## Evidence and integrity

[Raw diagnostic log](evidence/diagnostics/glm52-numerics-20260920-d1/diagnostic.log) · [failure/exit receipt](evidence/diagnostics/glm52-numerics-20260920-d1/exit.json) · [capture helper](evidence/setup/helpers-glm52-numerics-20260920-d1/capture_r3_numerical_failure.py) · [CPU report](cpu/analyses/glm52-numerics-20260920-d1-cpu-r1/analysis.md) · [CPU retrieval receipt](cpu/verification.json) · [copy manifest](copy-manifest.json).

The [original diagnostic transfer receipt](verification.json) and [remote manifest](manifest.json) name paths relative to `evidence/`; the CPU receipt names paths relative to `cpu/`. Both manifests and all copied bytes were independently rehashed, including the original compressed archive SHA (archive retained locally; the entire uncompressed payload is included here). Each tensor is bound four ways: transfer manifest, file SHA, rank sidecar, and analysis input SHA. Original absolute paths inside unchanged JSON/Python files are provenance, not portable navigation links. The `.sha256` copies retain the original transfer filenames intentionally.

| Captured tensor | Download | SHA256 |
|---|---|---|
| n1/rank0.pt | [809,033 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n1/rank0.pt) | `9d1569b6eac71adf48f6d380f1beb57e300f46788049180f26adb3f503b6e137` |
| n1/rank1.pt | [566,473 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n1/rank1.pt) | `424de58ee0a527d3b438d30aaeeeeb2985ddd7c872b74232c93680a3d37bd35e` |
| n1/rank2.pt | [566,473 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n1/rank2.pt) | `8ab2a62d2f4cbbe7fa886e96039c6d40aeed2a456cb28282e48c4486b39cec3b` |
| n1/rank3.pt | [566,473 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n1/rank3.pt) | `cb316719628f796e2e65ff7827638c858c8bc9ca933da719180942f27e1eb8e3` |
| n3/rank0.pt | [813,321 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n3/rank0.pt) | `273425b968b5d2a9143fa4884dbc2b5e8f8ccf19bf1102bc474f26278369bfa8` |
| n3/rank1.pt | [813,321 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n3/rank1.pt) | `fe6d595c497b194649dda2266e66007b5312324b4bcefc147186e442fc777813` |
| n3/rank2.pt | [813,385 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n3/rank2.pt) | `b456b1acd9811f4638a883339aa7dbf25bd8080adf13da0c7b28431d42850132` |
| n3/rank3.pt | [570,761 bytes](evidence/diagnostics/glm52-numerics-20260920-d1/capture/n3/rank3.pt) | `5d5bf0587333214add1eb20105b9c00219081acf82bfa77675326e994e1d0af4` |

The [source audit](R3_NUMERICAL_FAILURE_SOURCE_AUDIT.md), [capture plan](NUMERICAL_CAPTURE_PLAN.md), and [helper review](diagnostic-helper-independent-review.md) are preserved pre-capture records; their pending/unknown-cause language describes that earlier stage. The current tensor findings and strict-failure status are above.

## CPU-only reproduction

From this directory, in Linux with the recorded Torch version and `libm.so.6`, choose a new output path:

```bash
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4 python3 -B \
  cpu/setup/helpers-d1-cpu-analysis-r1/analyze_numerical_capture.py \
  --capture-root evidence/diagnostics/glm52-numerics-20260920-d1/capture \
  --output /tmp/d1-cpu-replay-new
```

The helper uses `torch.load(map_location="cpu", weights_only=True)` and CPU `libm.fmaf`; it neither imports the GPU benchmark nor changes the raw capture. This command reproduces saved-value arithmetic, not GPU runtime or timing. Original CPU [invocation](cpu/setup/helpers-d1-cpu-analysis-r1/invocation.json) and [exit](cpu/setup/helpers-d1-cpu-analysis-r1/exit.json) remain unchanged.
