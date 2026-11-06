# Static weight-cache hint candidate on 13ca1475

Candidate for a primary AUTO screen; not a retention claim. Production was unchanged. The independent marker patch is in `../iket13_experiment/markers.patch`.

## Contract and mechanism

- Physical operand A is the weight tile; physical operand B contains activations. The proposed patch changes only A TMA to EVICT_FIRST for one-CTA, eight-K-step geometry (`cta_group_size == 1 and k_steps == 8`). Other geometries retain the default policy. SFA/SFB and all activation loads retain their previous policies.
- This static policy has no token count, model dimension, expert count, or measured-workload branch. Small token panels stream weights across channel tiles while reusing source activations. NB2 loads and reuses operands differently and empirically regresses under A-FIRST, so it retains default hints.
- Default policy literal is 0; EVICT_FIRST is `0x12F0000000000000`; the rejected/diagnostic EVICT_LAST arm is `0x14F0000000000000`.
- A-FIRST wins strongly at T4 across all three formats and N16/N32/N64. MXFP8 at T128/512 has small losses, and NV N16 T512 regresses in both orders. These are retained in the table. No token cutoff was introduced. AUTO can continue selecting N32/N64.
- A-LAST is neutral at large NB2; A-FIRST regresses it. B-LAST has insufficient whole-chain evidence and is excluded from the proposed patch.

## Evidence boundary

- Frozen source `13ca1475d96839f3bf3c46699cc63204b4d3b409`, c1 `fi-w4a4-dyn-n-1024`, B200 GPUs 1/4, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1.
- Native DeepSeek benchmark inputs and seed 42, hidden 7168, intermediate 2048, 256 experts / 32 local, top-k 8. Native generated routing, captured phase arguments and returned allocations are reused within each control/variant comparison.
- 10 warmups / 100 samples, cold-L2 CUDA graphs with CUPTI medians. Every full-chain arm first compares its final output bytes to the control. Isolated phase arms compare output and output-SF bytes. Fixed tactics are diagnostics, not replacements for primary AUTO medians.
- `results/` contains complete timing samples, expert counts, valid row counts, exact-check logs, commands, and original metadata. No old B1 rerun; no primary A2/B2.

## Full-chain medians

| File | Tokens | Baseline us | A-FIRST us | A-FIRST+B-LAST us | B-LAST us |
|---|---:|---:|---:|---:|---:|
| cache13-mxfp8-n16-chain-r1 | 4 | 81.5525 | 72.7200 | 72.5125 | — |
| cache13-mxfp8-n16-chain-r1 | 128 | 231.1685 | 231.8890 | 231.7285 | — |
| cache13-mxfp8-n16-chain-r1 | 512 | 255.8090 | 262.9760 | 262.4810 | — |
| cache13-mxfp8-n32-chain-r1 | 4 | 80.7680 | 71.3440 | 71.1355 | — |
| cache13-mxfp8-n32-chain-r1 | 128 | 232.0640 | 233.7760 | 233.0720 | — |
| cache13-mxfp8-n32-chain-r1 | 512 | 247.1680 | 248.7685 | 248.0800 | — |
| cache13-mxfp8-n64-chain-r1 | 4 | 86.7200 | 81.9680 | 81.7920 | — |
| cache13-mxfp8-n64-chain-r1 | 128 | 238.9450 | 238.6720 | 237.1520 | — |
| cache13-mxfp8-n64-chain-r1 | 512 | 250.8800 | 252.8485 | 251.8085 | — |
| cache13-nv-n16-chain-r2 | 4 | 54.4320 | 47.7920 | 47.7920 | — |
| cache13-nv-n16-chain-r2 | 128 | 142.7520 | 139.9040 | 140.1610 | — |
| cache13-nv-n16-chain-r2 | 512 | 156.2240 | 157.3450 | 156.9610 | — |
| cache13-nv-n32-chain-r1 | 4 | 54.1600 | 47.7440 | 47.5205 | — |
| cache13-nv-n32-chain-r1 | 16 | 82.8480 | 74.1925 | 73.9040 | — |
| cache13-nv-n32-chain-r1 | 128 | 141.8565 | 140.0000 | 139.6480 | — |
| cache13-nv-n32-chain-r1 | 512 | 153.2795 | 152.1440 | 152.0160 | — |
| cache13-nv-n64-chain-r1 | 4 | 57.2800 | 51.2645 | 51.0880 | — |
| cache13-nv-n64-chain-r1 | 128 | 144.5445 | 143.0880 | 142.5760 | — |
| cache13-nv-n64-chain-r1 | 512 | 156.2400 | 154.8480 | 155.3760 | — |
| cache13-nv-nb2-chain-r1 | 8192 | 319.9690 | — | — | 320.2885 |
| cache13-nv-nb2-chain-r1 | 16384 | 565.1700 | — | — | 556.6255 |
| cache13-nv-small-chain-r1 | 4 | 54.3040 | 47.6315 | 47.7600 | 54.2720 |
| cache13-nv-small-chain-r1 | 8 | 71.4725 | 62.9440 | 63.3120 | 71.4400 |
| cache13-nv-small-chain-r1 | 16 | 82.6880 | 73.5840 | 73.5360 | 83.0400 |
| cache13-nv-small-chain-r1 | 128 | 142.5605 | 139.4405 | 139.8720 | 142.3840 |
| cache13-nv-small-chain-r1 | 512 | 155.7600 | 157.3440 | 157.6965 | 155.6005 |
| cache13-w4a8-n16-chain-r1 | 4 | 65.1360 | 56.8320 | 56.6720 | — |
| cache13-w4a8-n16-chain-r1 | 128 | 158.0325 | 154.9120 | 154.6890 | — |
| cache13-w4a8-n16-chain-r1 | 512 | 187.3605 | 187.1840 | 187.2800 | — |
| cache13-w4a8-n32-chain-r1 | 4 | 65.1200 | 56.9125 | 56.5770 | — |
| cache13-w4a8-n32-chain-r1 | 128 | 158.3040 | 155.2165 | 155.1685 | — |
| cache13-w4a8-n32-chain-r1 | 512 | 166.4800 | 164.5925 | 164.6250 | — |
| cache13-w4a8-n64-chain-r1 | 4 | 75.7120 | 72.9120 | 72.6410 | — |
| cache13-w4a8-n64-chain-r1 | 128 | 162.7680 | 159.8725 | 159.6805 | — |
| cache13-w4a8-n64-chain-r1 | 512 | 172.4480 | 169.7760 | 168.9920 | — |

## Integration

`cache-hints.patch` applies independently to the existing shared Blackwell core. `cache13_trial/selected_core.py` is the immutable selected implementation used for raw paired checks. Parent owns composition with the newer constexpr wrapper annotations and primary AUTO screening.

The static resource inspector `inspect_resources.py` compiles layout metadata for six supported dtype configurations and 15 phase/geometries, recording 90 cases in `results/cache13-static-resources.jsonl`. It does not launch kernels. Compile-time resource decisions are geometry/layout based; output route count remains runtime.

## Validation

Six-format paired checks passed **48 FC1 + 24 FC2 cases**, including gathered/permuted rows, short K64/128 and K384, N16/N64, per-token scaling, quantized FC1 output/SF, and BF16 FC2 output. Every output and SF byte matches frozen 13ca. Logs: `results/cache13-selected-exact-fc1.log` and `results/cache13-selected-exact-fc2.log`. Native chains additionally compare final outputs before timing. The final primary retention decision is pending.
