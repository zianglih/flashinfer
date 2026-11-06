# Asynchronous SF16 staging experiment

All variants in this isolated experiment are **rejected**. Production was not changed. The final warp-aggregated arrival screen did not recover a material gain, and this SF-scratch route was stopped.

`build.py` starts from the frozen two-CTA overlap + Gather4 core `36bcef61277ad54957440d48d4cb5a89fe0d33d7add47c96f0bbdb96f5b2af82` and copies its dependencies into `sfasync_trial`. `manifest.json` records every copied/generated module hash. The same frozen epilogue is used in both arms.

## Mechanism and correctness boundary

For FC1 SF16 and K divisible by 256, the four loader warps issue one asynchronous 16-byte copy per token row into per-stage, row-linear SF scratch. Invalid rows use the existing copy helper's zero-fill predicate. Each producer commits immediately; there is no producer wait after the copy.

The existing MMA warp waits for local SF completion, loads each 16-byte scratch row into four Uint32 registers, and scatters those four words into the prepared SFB layout. Each lane processes one row per round using `row = 8*round + 32*(lane//8) + lane%8`; the final four-byte stores therefore touch distinct banks across the warp. The existing async-proxy fence and 64-thread two-CTA relay follow the stores. This preserves local SFB ownership and leaves group-2 S2T/MMA unchanged.

Short/nonaligned K and non-SF16 explicitly retain the original four-byte cp.async path. These fallback branches were source-reviewed and Python-compiled; they were not revalidated on GPU because the proposed fast path lost its performance screen.

Eight paired cases passed with identical output bytes: N1/129/255/257, random FP4 values and nonuniform powers-of-two scales, reverse routing, repeated route tiles, and per-token false/true, M256/K256/N256. The existing BF16 phase smoke also passed. This does not establish exhaustive dtype, generated-FP4-output, sanitizer, or fused-combine coverage.

## Controlled phase screen

C1 B200 GPU2, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, CuTe DSL 4.7.1. Balanced 16,384 routes, 32 experts, FC1 M4096/K7168, 148 CTAs, five stages. Same GPU, CUPTI + CUDA graphs, cold L2, three warmups, 15 repeats, median microseconds. Control ran before the candidate; the regression was large enough to reject without a retention campaign or further correctness expansion.

| N | Frozen composed control | Async SF scratch + MMA transform |
|---|---:|---:|
| 128 | 270.912 us | 328.032 us |
| 256 | 267.393 us | 309.793 us |

## Profile interpretation

NCU profiles compare the frozen composed N256 kernel (`sfb-composed-nvfp4-n256-ncu-01`) with this variant (`sfasync-nvfp4-n256-ncu-01`). NCU durations are diagnostic; the CUPTI table above is the latency screen.

| Counter | Control | Async SF scratch |
|---|---:|---:|
| NCU duration | 276.576 us | 310.144 us |
| Tensor pipe active | 40.321% | 35.651% |
| LSU/L1 data pipe throughput | 68.974% | 35.234% |
| SF-copy global L1 requests | 58,720,256 | 14,680,064 |
| SF-copy shared wavefronts | 29,360,128 | 7,340,032 |
| Dynamic SMEM | 195,584 B | 216,064 B |
| Registers/thread | 80 | 80 |
| Local load/store sectors; spill reads/writes | 0 / 0; 0 / 0 | 0 / 0; 0 / 0 |

The asynchronous vector fetch reduces fragmented SF request overhead by four times. The added conversion runs serially on the MMA warp, and the net kernel slows. The new shared vector loads have no excess wavefronts in NCU, so a simple scratch-load bank conflict does not explain the loss. A future producer-side conversion would need to preserve asynchronous overlap; simply waiting immediately after a vector load would repeat the previously rejected synchronous-vector behavior.

## Producer conversion follow-ups

`build_prefetch.py` moves conversion to the 128 producers and uses two producer-owned SF scratch slots. It preloads SF0, issues SF(k+1) before the current stage acquire, waits with `cp_async_wait_group(1)`, transforms SF(k), and sends an ordinary local `mbarrier_arrive` after the async-shared fence. The final iteration uses wait-group zero. An ordinary arrival is essential: the original cp.async-mbarrier arrival would also wait for the future prefetch. The unchanged local-ready / two-CTA relay protocol then admits MMA. All producer threads retain disjoint scratch rows, and the scratch slot is no longer needed after that producer's register load.

`build_depths.py` extends this to three/five scratch slots with matching prefill depth and explicit decreasing tail wait counts. `build_warp.py` keeps two slots and aggregates ready arrivals: each thread fences its stores, the warp synchronizes, then one elected lane arrives with count32. Expected arrivals remain128; fallback paths keep the original cp.async-mbarrier behavior.

Each of these four producer variants passed **50 paired byte comparisons**: K64/384 fallback and K512/768/1024 fast paths, N1/17/129/255/257, per-token false/true, M512, and one persistent CTA-pair processing multiple tiles. This exercises final-prefetch drain and reuse across K/route/channel tiles. The comparison is against the frozen core; occasional one-ULP differences from the separate Torch activation smoke are shared by both arms.

All producer phase screens use the same GPU2 workload/methodology above:

| Arm | N128 us | N256 us | Screen |
|---|---:|---:|---|
| Two scratch slots | 333.823 | 264.992 | R2, candidate first |
| Frozen control | 270.848 | 267.072 | R2, control second |
| Three scratch slots | 333.023 | 268.768 | R3 |
| Five scratch slots | 335.616 | 278.528 | R3 |
| Frozen control | 270.975 | 267.169 | R3, control last |
| Two slots + count32 warp arrivals | 346.208 | 272.544 | R4 |

The two-slot N256 result is near-neutral; N128 regresses substantially in every producer variant. Increasing lookahead and aggregating arrivals do not recover a useful gain. No SF32 extension, full-MoE benchmark campaign, new production test, or production integration was performed for these rejected changes.

Raw evidence is preserved in `../../logs/sfasync-*.log` and `../../logs/sfasync-nvfp4-n256-ncu-01-{raw,source}.csv`. The remote `.ncu-rep` has the same prefix.

From the remote candidate checkout:

```bash
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. OMP_NUM_THREADS=1 \
  ../.venv/bin/python ../scripts/sfasync_experiment/run_paired.py \
  --script probe_fc1.py

CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. TRTLLM_ENABLE_PDL=1 OMP_NUM_THREADS=1 \
  ../.venv/bin/python ../scripts/sfasync_experiment/run_variant.py \
  --variant async --script probe_perf.py --repo . --mode nvfp4 \
  --tokens 16384 --tiles 128,256 --factors 1 --stages 5 --phases fc1
```

Use `--variant baseline` for the frozen control. The profile command uses the same arguments with `--profile` under the NCU sections/metrics listed in the sibling `sfload_experiment/SFB_COPY_AUDIT.md`.

Producer variants are `prefetch`, `prefetch3`, `prefetch5`, and `prefetch_warp`. Their paired command uses `run_paired.py --variant <name> --script probe_boundaries.py`. All module hashes are in `manifest.json`; all variants and helper scripts remain archived for source comparison.
