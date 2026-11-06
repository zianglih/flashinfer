# V3 helper-isolated elected-owner fixed-tactic screen

Preparation only. Launch requires the repaired candidate's successful exact/codegen gate at `clc-elected-owner-20261026/gate-v3-validation.json` and six exclusively available GPUs, one worker per model/family.

- Exactly 48 affected points: V3 EP8, V4.1-Flash EP4, Kimi K3 EP8 × standard NVFP4, per-token NVFP4, MXFP4x8, MXFP8 × 32, 128, 4096, 16384 tokens.
- Clean `9b4721b0` control versus device-only owner patch `96cfbfbe`, with unchanged full six-field host policy. Both use the same saved native all-CLC cache, explicit True/True flags, and C–A–A–C timings: reuse the source-matched final v2 control as the opening control on the same GPU, then run fresh candidate, candidate, and control. No v2 candidate timing is reused.
- NVFP4 includes input quantization; MX uses prequantized input. PDL on, fused finalize off, public wrapper API, 10 warmups and 100 raw cold-L2 graph/CUPTI samples per point. No TRTLLM, W4A16, native AUTO, or existing timing rerun.
- The benchmark's `cutedsl` selector normally groups W4A4/W4A16. For standard NVFP4 only, the observer uses its existing `profile_backend='cute-dsl'` dispatch filter while keeping `profile_cuda=False`. This changes selection only; timing and public wrapper calls are unchanged. Per-token and MX use ordinary selectors.
- Three fresh processes follow the recorded prior control in control/candidate/candidate/control order on the same GPU; reused source/path/timestamps are recorded explicitly. Native C++ cache comes from the verified deployed persistent cache; DSL namespaces remain source-private. No compiled-cache cleanup.
- Receipts require matching source hashes, untouched input cache, equal actual six-field tactics, equal route identities, complete labels, and exactly 100 raw samples. Missing cache keys fail the run rather than trigger retuning.

Remote commands after gate approval and live GPU availability checks:

```bash
python3 run_campaign.py --model <model> --family nvfp4 --gpu <exclusive-gpu>
python3 run_campaign.py --model <model> --family mxfp --gpu <different-exclusive-gpu>
```

V2 timing results remain separate in `../full_screen/results-v2`. `analyze.py --root <remote-experiment-or-collected-copy>` validates all nine CAAC cells and summarizes medians/drift across 48 points. This is a bounded CLC-only diagnostic, not native AUTO retention evidence.
