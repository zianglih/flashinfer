# Physical N16 experiment

Independent actual source clone `flashinfer-physical-n16-review`, base 98fd3566b5f945c100f48cddacf25deb2432cbc2. All changes remain unstaged.

The candidate narrows both B and accumulator C to 16 columns for N16 gated NVFP4 FC1 with generated FP4 output. The already proved Ld16x256 epilogue reads exactly those columns, activates in FP32, preserves scale/FP4 arithmetic, and reorders packed nibbles. Four operand stages, warp roles, grid, cache hints, SF staging and all host preparation remain unchanged. Other formats and per-token BF16 output explicitly keep the original physical N32 path.

Two accumulator stages occupy 32 rather than 64 columns. The total TMEM allocation still rounds to 128 columns after the unchanged 64 scale columns. This is not a claim of reduced hardware TMEM occupancy.

Checks: existing bounded random FC1/output-SF exact probe, including K64/K384 tails, partial N and per-token fallback; then native fixed-tactic full-chain ABA and BAB at T32/T128, 10 warmups and 100 cold-L2 CUDA graph CUPTI samples per arm. Input quantization outside timing. Separate classes and compiled caches use actual candidate source, no source rewriting at import. Source and samples are archived. No primary benchmark or baseline campaign is rerun.

Status: closed, not retained. The bounded full-chain gate was mixed and sub-percent; production remains unchanged at 98fd.

## Measured result

Replacement B200-92, GPU2 UUID `GPU-7e973000-5213-bf29-4ca1-25a6d947f8e3`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2.78, Torch 26.05, CuTe 4.7.1. Only adjacent controls on this node are paired; no old-node TRTLLM or primary comparison. Native W4A4 input/routing, simulated EP8 (32 local experts), unfused finalize, fixed `[16,[[128,16],[1,1],false],[[128,16],[1,1],false]]`. Preparation remains inside the full-chain measurement and input quantization remains outside.

All seven bounded random FC1/output-SF cases passed exactly, including K64/K384, valid N1/7/8/15/16/17 and per-token BF16 fallback N31. Native FC1/SF, FC2 and final outputs matched before/after every arm. The helper releases captured intermediates before graph timing. CPU lane/register and packed-nibble proofs pass. This is a focused performance gate, not a full numerical/sanitizer campaign.

| Tokens | ABA: control / candidate / control (us) | BAB: candidate / control / candidate (us) | Control/candidate geomean |
|---:|---|---|---:|
| 32 | 105.8720 / 106.4005 / 105.9045 | 106.2730 / 106.1125 / 106.3050 | 0.996584x |
| 128 | 143.4085 / 142.6885 / 143.5530 | 142.7050 / 143.4405 / 142.6730 | 1.005456x |

Measured resources: shared memory 197,504 to 181,120 B; registers 64 to 50; local memory 0 B both; active CTA/SM 1 both. Four operand stages, 288 threads, 128 allocated TMEM columns and 4096 B SFB/stage remain unchanged. Both logical accumulator stages are truly 16 columns, not 32. SASS instruction count 1144 to 1224; the candidate eliminates the FP32 TMEM transpose but uses 15 shuffles (12 SF reductions plus 3 packed-nibble exchanges), 2 Ld16x256 accumulator loads. Cubin/PTX/SASS are archived.

Reproduce on the prepared replacement environment:

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n
bash scripts/physical_n16_experiment/run_smoke.sh
bash scripts/physical_n16_experiment/run_pairs.sh
```

These commands refuse existing result outputs. The completed evidence contains 12 timing arms/1200 individual samples, each median recomputed locally, and matching input/routing fingerprints between ABA/BAB.

Archive SHA256: `900e864d9843f1fe3fb89fc96958112156237399145637395c374908aa73eb77`. Source pins and every raw-file digest are in `manifest.json` and `archive-receipt.json`. Both experiment source files remain unstaged in `flashinfer-physical-n16-review`; no commit or PR change was made.
