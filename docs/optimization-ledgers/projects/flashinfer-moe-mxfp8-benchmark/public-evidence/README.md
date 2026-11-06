# DeepSeek MoE: TRTLLM MXFP8 comparison through 16384 tokens

PR: https://github.com/flashinfer-ai/flashinfer/pull/5301
Original source (1..4096): https://github.com/zianglih/flashinfer/commit/1cafd1a22ea7be32497c1b8e66c466ea873bb0af
Extension source (8192/16384): https://github.com/zianglih/flashinfer/commit/48f8a7a7bf2282cdb976dd4e28ec01ff32bf9cd1
Final source (corrected TRTLLM NVFP4 per-tensor): https://github.com/zianglih/flashinfer/commit/964f6fd2a582da1a7b57b5c20e3872caea80f693

Follow-up to FlashInfer #4985 on one retained C2 B300 using CUDA 13.2, DeepSeek-V3 H7168/I2048/E256/top8, groups8/top4, EP8 local simulation/TP1. Three recipes (inference per-tensor, inference per-token, deterministic RL configuration), five backends. The original batch has 585 measurements / 9 processes; the separately appended batch has 90 / 9; corrected TRTLLM NVFP4 per-tensor reruns have 45 / 3. Total: **720 raw measurements, 675 selected cells, 45 superseded cells, 45 configuration/token medians**, 21 processes. CUTLASS is skipped. CUDA graph+CUPTI+cold L2, 10 warmups / 100 iterations, initial activation quantization included, prewarm autotuning outside measurement. MXFP8 columns precede BF16.

The extension source changes only the shared TRTLLM `tune_max_num_tokens=max(n,8192)` argument, allowing 16384-token tuning at its own size; the bound at <=8192 matches the previous default. Final source corrects the preexisting TRTLLM NVFP4 per-tensor activation-scale layout: previously swizzled bytes were passed to an API expecting linear. Only those 45 cells are replaced from a separate all-token rerun. `results.md` has 75 selected cells per configuration/repeat table, plus a collapsed table preserving all 45 invalid/superseded observations, excluded from every median/speedup. A repeat label pairs separate collection processes. `results-provenance.json` records all three sources and exact replacement scope.

`runs.json` and unprefixed `inference-*.json/log` / `rl-*.json/log` are immutable original evidence. **New files use `extension-16k-` or `nvfp4-linear-` prefixes**, including their separate `runs.json` manifests. `bench_moe_deepseek.py` preserves original source; `extension-16k-bench_moe_deepseek.py` and `nvfp4-linear-bench_moe_deepseek.py` preserve the later sources. JSON retains unrounded results and manifests record exact commands/environment/source/result/log hashes. `file-manifest.json` hashes this payload. Diagnostic/incomplete runs are excluded; superseded scale-mismatched rows remain explicitly labeled.

GPU validation uses an existing broad provisional MXFP8 fuzz envelope on small shapes; full-shape checks establish finite output/API/replay, not cross-precision parity. Historical GPU validation stays at its historical commit. Final source has separate token-cap, NVFP4 activation-operand/QDQ-layout, and MXFP8 full 16384 checks. The CPU/meta token-cap check does not validate scale contents or kernel numerics; the NVFP4 operand check does not execute native MoE or establish full-MoE numerical correctness.

## Reproduce collection

Place helpers next to an independent `flashinfer/` checkout and install dependencies from `setup_devbox.sh`. Use separate output directories so the original evidence cannot be overwritten:

```bash
git -C flashinfer checkout 1cafd1a22ea7be32497c1b8e66c466ea873bb0af
python3 run_sweeps.py --tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096 --output artifacts/repro-original --gpu 0
git -C flashinfer checkout 48f8a7a7bf2282cdb976dd4e28ec01ff32bf9cd1
python3 run_sweeps.py --tokens 8192,16384 --output artifacts/repro-extension-16k --gpu 0
git -C flashinfer checkout 964f6fd2a582da1a7b57b5c20e3872caea80f693
python3 run_nvfp4_linear_baseline.py --output artifacts/repro-nvfp4-linear
# Or remeasure every point on final source (not the historical batch split):
python3 run_sweeps.py --tokens 1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384 --output artifacts/repro-full-16k --gpu 0
```

## Regenerate from this flat gist

Restore `runs.json`, `environment.txt`, and `pip-freeze.txt` to `artifacts/`; restore unprefixed original run files under `artifacts/runs/deepseek-v3/`. Strip each `extension-16k-`/`nvfp4-linear-` prefix and place the manifest/environment/package snapshot in `artifacts/extension-16k/` or `artifacts/nvfp4-linear/`; place its per-run files under the corresponding `runs/deepseek-v3/` subdirectory. Then run `python3 build_results_report.py`. Copied-artifact file-manifest entries have a `source_path` giving their workspace destination; source snapshots are identified by `commit`. The report verifies hashes/settings, all three source commits, and narrowly allowed source changes before selecting or superseding cells. Absolute run-manifest paths are provenance only.
