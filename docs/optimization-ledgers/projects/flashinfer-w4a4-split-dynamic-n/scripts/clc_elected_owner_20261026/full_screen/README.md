# Elected-owner fixed-tactic screen

Preparation only. Launch requires the repaired candidate's successful exact/codegen gate at `clc-elected-owner-20261026/gate-validation.json` and six exclusively available GPUs, one worker per model/family.

- Exactly 48 affected points: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8 × standard NVFP4, per-token NVFP4, MXFP4x8, MXFP8 × 32, 128, 4096, 16384 tokens.
- Clean `9b4721b0` control versus device-only owner patch `d8ca478d`, with unchanged full six-field host policy. Both use the same saved native all-CLC cache, explicit True/True flags, and fresh CAAC timings.
- NVFP4 includes input quantization; MX uses prequantized input. PDL on, fused finalize off, public wrapper API, 10 warmups and 100 raw cold-L2 graph/CUPTI samples per point. No TRTLLM, W4A16, native AUTO, or existing timing rerun.
- The benchmark's `cutedsl` selector normally groups W4A4/W4A16. For standard NVFP4 only, the observer uses its existing `profile_backend='cute-dsl'` dispatch filter while keeping `profile_cuda=False`. This changes selection only; timing and public wrapper calls are unchanged. Per-token and MX use ordinary selectors.
- Four separate processes per cell in control/candidate/candidate/control order on the same GPU. Native C++ cache comes from the verified deployed persistent cache; DSL namespaces remain source-private. No compiled-cache cleanup.
- Receipts require matching source hashes, untouched input cache, equal actual six-field tactics, equal route identities, complete labels, and exactly 100 raw samples. Missing cache keys fail the run rather than trigger retuning.

Remote commands after gate approval and live GPU availability checks:

```bash
python3 run_campaign.py --model <model> --family nvfp4 --gpu <exclusive-gpu>
python3 run_campaign.py --model <model> --family mxfp --gpu <different-exclusive-gpu>
```

`stage_helpers.py` only deploys helpers and captures the installed IKET helper source; it launches no GPU work. `analyze.py --root <remote-experiment-or-collected-copy>` validates all nine CAAC cells and summarizes medians/drift across 48 points. This is a bounded CLC-only diagnostic, not native AUTO retention evidence.
