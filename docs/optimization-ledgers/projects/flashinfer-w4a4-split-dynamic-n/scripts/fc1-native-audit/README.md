# Native-routing FC1 audit

This bounded diagnostic targets the remaining NVFP4 FC1 regression in the
weights-A / activations-B dynamic-N implementation. It does not time or replace
any of the three primary benchmark arms.

## Frozen inputs and environment

- Core/utils snapshot: `d9074cb6e9e934d387e358a069e90ddf084f5ef7`; hashes are in
  `manifest.json`. Frozen imports are isolated under `audit_trial/`.
- Devbox `fi-w4a4-dyn-n-1024`, c1, namespace ziangli; GPU3 only, NVIDIA B200.
  Container `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1.
- Native `bench_moe_deepseek.py` preparation and actual top-k-8 routing:
  T=16384, H=7168, I=2048, 32 local experts, 16280 local routes. N256 produces
  77 route tiles versus 64 in the balanced synthetic fixture.
- FC1 uses M256/two-CTA and N128 or N256. FC2 is forced to M128 only to capture
  the real native FC1 arguments. Timed calls include FC1 alone.
- CUPTI CUDA-graph timing, cold L2, 5 warmup and 30 timed iterations per arm.
  Every timing sample and the harness SHA256 are retained in the JSON files.
  The candidate source checkout was not reset or switched during this audit.

## Retained change

`gatherlast_core.py` moves exactly the existing SFB `cp.async` loop immediately
before the FC1 Gather4 loop. Weight/SFA TMA remains first. FC2 has no Gather4
loop, so its instruction order is unchanged. This adds no storage or payload
staging and changes no addresses, predicates, barriers, copy counts, scales,
per-token behavior, or arithmetic. Issuing the fragmented SF requests earlier
lets them progress while the producers issue Gather4 payload requests.

The production edit is only this reorder plus its rationale comment in
`blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py`.

| Native FC1 arm | N | Control us | Variant us | Latency reduction |
| --- | ---: | ---: | ---: | ---: |
| Early accumulator release, R2 | 256 | 335.6485 | 334.1450 | 0.45%, rejected as neutral |
| SF before all weight/payload TMA, R2 | 256 | 335.6485 | 322.2405 | 4.00%, broader diagnostic only |
| SF before FC1 Gather4 only, R3 | 128 | 335.5680 | 334.8170 | 0.22%, neutral |
| SF before FC1 Gather4 only, R3 | 256 | 332.1765 | 323.7440 | 2.54% |
| SF before FC1 Gather4 only, reverse-order R4 | 256 | 334.4170 | 324.8490 | 2.86% |
| SF before FC1 Gather4 only, reverse-order R4 | 128 | 335.7765 | 333.9685 | 0.54%, neutral |

R2 order was early, loadfirst, baseline. R3 order was baseline, gatherlast at
N128, then baseline, gatherlast at N256. R4 reverses both the tile and arm order and confirms the N256 gain.
Only the FC1-only reorder is proposed for retention. These isolated times do
not claim a full-pipeline improvement; the root task owns the combined screen.

Raw files are at `../../logs/fc1-native-{early,loadfirst,baseline}-r2-d907-gpu3.*`
and `../../logs/fc1-native-{baseline,gatherlast}-n{128,256}-r{3,4}-d907-gpu3.*`.

## Correctness and harness correction

Native N128 and N256 candidates pass output-byte and output-SF-byte comparison in both R3 and R4
against the frozen original. `run_paired.py --variant gatherlast --script
probe_contract.py` passes all 24 paired byte checks:

- NVFP4 E4M3/SF16, FP4 E8M0/SF16, MXFP4 E8M0/SF32, MXFP8 E4M3, MXFP8 E5M2,
  and mixed W4A8.
- N128/one-CTA and N256/two-CTA, each with per-tensor quantized output or
  per-token BF16 output. Native N128 additionally covers M256/two-CTA.
- K64 for SF16 and K128 for SF32, including the FP4 tile-K256 tail; random
  power-of-two scale factors; 133 routes drawn from 17 sources with top-k-8
  repetition and reversed source rows; persistent execution with one CTA group.
- Full output and scale tensors, including prefilled padding, compare bytewise.

The initial native comparison used separately allocated result buffers while
native `out=None` kwargs left padding unwritten. Whole-buffer comparisons then
reported false failures. The corrected harness retains the captured output and
SF allocation for both implementations, giving padding identical initial
state. R2 and later supersede the initial failure logs. The early-release arm
passes this corrected check; it is rejected for negligible gain, not incorrect
results. Current harness SHA256:
`87ca9c18ef127a278bbe2f5a7b73f72962ed72475392592b27cb2a507c141d65`.

Raw contract output: `../../logs/fc1-native-gatherlast-contract-d907-gpu3.log`.

## Diagnosis and limits

The frozen native N256 control measured 335.0565 us by CUPTI. One NCU diagnostic
launch took 357.728 us and reported tensor-pipe activity 32.54%, TMEM activity
41.29%, shared-LSU activity 58.29%, and shared-TC activity 21.47%. It used 90
registers/thread, 195584 B dynamic SMEM and no local-memory spill requests.
Producer empty-stage waits and epilogue accumulator-full waits dominate the
sampled long-scoreboard locations. These counters show a coupled pipeline;
they do not establish a single saturated resource.

The fragmented SF `LDGSTS` requests account for 58,347,520 of 60,890,420 global
L1 requests (95.8%; TMA is excluded from this denominator). Balanced routing
had 58,720,256 SF requests, so extra ragged tiles do not imply a proportional
increase in executed global SF requests: predicates eliminate inactive rows.

The transposed epilogue has structural TMEM traffic overhead relative to the
old direct accumulator read. Actual native FC1 processes 16800 epilogue row
lanes for 16280 valid rows, only 3.19% padding. TMEM activity and short-scoreboard
samples do not establish TMEM throughput saturation. This investigation does
not attribute the remaining old-baseline gap to a single mechanism.

Direct Gather4 of a 16-byte SF row cannot produce the existing prepared-SFB
physical layout: the four 4-byte SF words for a row land at offsets
`0, 512, 1024, 1536`, while Gather4 retains contiguous words in its contiguous
row dimension. A 128-byte XOR swizzle cannot supply those 512-byte separations,
and a direct 4-byte TMA row is below the 16-byte minimum. The existing scratch
transformation/prefetch variants were already rejected; see
`../sfasync_experiment/README.md`, `../sfload_experiment/SFB_COPY_AUDIT.md`, and
`../epilogue_experiment/README.md`. No new SF scratch stage was added here.

The early-release candidate makes the accumulator available after the final
live slab's TMEM transpose but before quantization/stores. Only 77 of 525
native token slabs are final slabs, limiting overlap opportunity. It passed
correctness but is performance-neutral and was not integrated. A balanced
absmax tree was generated for inspection but never GPU-tested or retained;
SASS already fuses portions of the original max chain.

## Reproduction

From the remote candidate checkout, using the isolated immutable core:

```bash
CUDA_VISIBLE_DEVICES=3 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
  ../.venv/bin/python ../scripts/fc1-native-audit/profile_native_fc1.py \
  --repo . --tile 256 --variant gatherlast \
  --output ../logs/fc1-native-gatherlast-n256-recheck.json
CUDA_VISIBLE_DEVICES=3 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
  ../.venv/bin/python ../scripts/fc1-native-audit/run_paired.py \
  --variant gatherlast --script probe_contract.py
```

Use `--variant baseline` for the paired control and `--tile 128` for N128.
`--profile` brackets exactly one native FC1 call with CUDA profiler APIs;
`ncu --profile-from-start off` captured the archived NCU evidence. The `.ncu-rep`
is retained remotely, with raw and source CSV exports in local `logs/`.
