# FC1 TMA Gather4 experiment

The retained local production change replaces routed FC1 activation cp.async loads with TMA Gather4. Weight/SFA TMA and SFB cp.async share the existing pipeline. Four producer warps each register one quarter of the stage bytes and issue their own Gather4 requests, eliminating an extra synchronization barrier. Routing IDs are vector loaded in aligned groups of eight and reused across K tiles. Invalid source rows use TMA zero fill. FC2 and arithmetic contracts are unchanged.

Production integration: `flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`, SHA256 `d192a3ecdd302ce903a4b92476e0ab8ba1e7bba008d060dcce25239229adb6c0`. Frozen control core SHA256 `1e4cf7ce1b961751adf8e7d70ede6574d72726fa038379c41f3e827c309dfa81`. The minimal patch is `gather4.patch`. Root owns commits and deployment.

## Validation

The flattened production version (`integrated_core.py`) passed 64 exact byte comparisons against the frozen cp.async core: 20 NVFP4 FC1 cases, 8 N256 cases, 24 dtype/per-token cases, and 12 short-K cases. This covers N16/32/64/128/256, partial route tiles, reversed/repeated mapping, FP4 SF16 E4M3/E8M0, FP4 SF32 E8M0, homogeneous E4M3/E5M2 FP8 SF32, mixed W4A8, per-token BF16 output, and generated FP4/FP8 outputs including SF bytes. Short K values are 64, 128, 384. Existing task-local probes were used; no production test file added. Local ruff and Python compilation passed.

Raw outputs: `../../logs/gather4-integrated-*.log` and `../../logs/gather4-multi-paired-*.log`.

## Controlled phase diagnostic

C1 B200, one GPU, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, Torch 2.12 development, CuTe DSL 4.7.1. Balanced 16,384 routed rows, 32 experts, hidden 7,168, gated FC1 channels 4,096, grid 148 CTAs. CUPTI CUDA graph timing, cold L2, 3 warmups, 15 repeats, median microseconds. This is a synthetic phase diagnostic, not full-MoE retention evidence.

| Tactic | Control R2 | Gather4 R2 | Gather4 R3 | Control R3 | Speedup |
|---|---:|---:|---:|---:|---:|
| N128, 4 stages | 383.936 | 362.273 | 362.401 | 384.000 | 1.060x |
| N256, 3 stages | 367.072 | 351.071 | 351.296 | 367.041 | 1.045x |

Sparse one valid route per expert was unchanged: N16 103.232→103.264 us, N32 103.200→103.232 us. Stage policy is unchanged. N128 stage5 measured 357.343 us, but was not retained as part of this change. N256 stage4 regressed to 372.928 us.

Run from the remote candidate checkout:

```bash
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python -u \
  ../scripts/gather4_experiment/run_paired_fc1.py \
  --variant integrated --script probe_fc1.py

CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python -u \
  ../scripts/gather4_experiment/run_variant.py \
  --variant gather4_multi --script probe_core_perf.py \
  --repo . --tokens 16384 --tiles 128 --factors 1 --stages 4 --phases fc1
```

Repeat the exact comparison with `probe_n256_fc1.py`, `probe_dtype_gather.py`, and `probe_fc1_tail.py`. Phase control uses `--variant cpasync`; N256 uses `--tiles 256 --stages 3`. Raw phase outputs are preserved under `../../logs/gather4-perf-r[23]-*.log`; initial barrier-based variants remain archived for diagnosis.
