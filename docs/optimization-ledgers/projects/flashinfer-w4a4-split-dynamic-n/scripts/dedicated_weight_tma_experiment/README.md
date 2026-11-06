# Dedicated weight-TMA producer experiment

Frozen control: `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. This task-local experiment changes no production source. It tests whether a separate A/SFA producer removes the measured imbalance between warp 0 and the three other FC1 Gather4/SF warps.

## Feasibility and ownership

- Existing topology: producer warps 0–3, epilogue warps 4–7, MMA warp 8. The experimental topology adds weight-TMA warp 9 and launches 320 threads. The extra role owns an independent pipeline state but visits exactly the same persistent tile/K sequence. Existing inline-epilogue configurations and FC2 preserve their topology and instructions.
- The one existing TMA full barrier uses five elected arrivals on the leader CTA. Each Gather4 warp contributes its own B transaction bytes; the weight warp contributes all A/SFA bytes. Both CTAs' completed transactions still target the leader barrier. The existing single MMA completion releases the shared operand ring after both NB2 channel MMAs.
- There are no new shared-memory buffers, barriers, TMEM columns, or MMA/epilogue stages. TMEM allocation remains warp 0; retrieval/final CTA barriers use the new block size; the first 128 threads retain deallocation ownership. All SF producer/relay roles are unchanged.
- All five arrivals occur for every K stage, including short K, OOB rows, and inactive channel tails. TMA transaction bytes remain the full requested tile bytes; predicated logical output does not remove an arrival. The independent weight producer drains its own state with `producer_tail`; this is a wait-only operation.

Let `G` be the CTA-group size, `C` the NB2 channel-tile count, `R` the local B rows, and `K` the tile reduction extent. Let `WA`/`WB` be the input bit widths and `SFA` the existing scale-stage byte size. The arrivals are:

```
weight = G * C * (128 * K * WA / 8 + SFA)
each of four gather warps = G * R * K * WB / 8 / 4
sum = original aggregate TMA byte count
```

For two-CTA NVFP4 NB2 N128/K256, this is `73,728 + 4 * 4,096 = 90,112` bytes. The original four equal arrivals each contributed 22,528 bytes. No divisibility-by-five assumption is needed. The transfer byte formula intentionally preserves the existing weight bit width, including existing unpacked-weight behavior in fallback configurations.

## Source evidence

- Installed CuTe DSL 4.7.1 `cutlass/pipeline/sm100.py:343`, `PipelineTmaUmma.producer_acquire(expected_tx=...)`, overrides per-arrival bytes and calls `MbarrierArray.arrive_and_expect_tx` only on the leader CTA.
- CuTe DSL 4.4.0 wheel source also has `MbarrierArray.arrive_and_expect_tx` at line 327 with the same elected-lane semantics. The exact public wheel URL is recorded in `compatibility-source.json`; extracted source is `dsl44-helpers.py.source`. This proves method availability, not a separate 4.4 runtime validation.
- The repository's SM107 Mega helper already implements this optional override in `moe_ep/kernel_src/sm107/next_cutedsl_megamoe/src/sources/kernel_src/rubin/custom_mix_cga_helpers.py:290`. No Mega sources are changed or imported by the prototype.
- The production SM100 copied pipeline lacks the override. `weight_trial/weighted_pipeline.py` adds only that method argument/body; frozen `custom_pipeline.py` remains the control. Replacing the entire copied pipeline with the installed version would introduce unnecessary synchronization differences.
- Production core anchors: pipeline creation around 960; A/SFA issue around 1190; SF/Gather4 producer completion around 1330; producer tails around 1380; MMA TMA-full wait and operand release around 1540–1660.

## Validation boundary

Initial scope is NVFP4, fixed native-routing NB2 N128. Broad formats or mixed 192-thread topology will be investigated only if the bounded native comparison gains. The first exact probe reuses the established bytewise control body and covers K64/384/512/768/1024, live routes 1/17/129/255/257/8193, M384/M768 channel tails, per-tensor generated FP4/SF output, and per-token BF16 output. Every output and SF byte, including sentinel padding, is compared to the frozen control.

Timing uses actual native DeepSeek routing at T8192/T16384 with adjacent forward and reverse controls, 10 warmups / 100 cold-L2 graph/CUPTI samples, retaining all samples. These are diagnostic phase/full-chain controls on the replacement environment, not a rerun or replacement of historical primary B1.

## Commands

```
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
source ../scripts/recovery442/env_candidate.sh
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/dedicated_weight_tma_experiment/run_paired.py --script probe_nv.py
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/dedicated_weight_tma_experiment/probe_modes.py --repo . --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 --tokens 8192,16384 --variants baseline,dedicated,baseline --mode nvfp4 --output ../logs/weight442-nv-r1.json
CUDA_VISIBLE_DEVICES=6 PYTHONPATH=. ../.venv/bin/python ../scripts/dedicated_weight_tma_experiment/probe_modes.py --repo . --expected-head 442d2aa53f68b4640c3ab5118a76f1599ff60d34 --tokens 16384,8192 --variants dedicated,baseline,dedicated --mode nvfp4 --output ../logs/weight442-nv-r2.json
```

## Decision and results

Rejected: FC1 is approximately neutral at 8K and improves only 0.9–1.1% at 16K. The full-chain 16K gain reverses sign with order, so the extra warp does not establish a repeatable end-to-end improvement. No broad-format runs, production integration, or primary benchmark reruns followed. GPU6 was released.

All 12 strict low-level cases and all 12 native timing arms passed byte-exact comparison. All native arms use identical routing histograms for each token count. An independent source review found no actionable barrier, tail, phase, or CTA-group issue. The compatibility source check covers the helper method; actual GPU execution used DSL4.7.1 only.

| Order | Tokens | FC1 control µs | FC1 dedicated µs | FC1 speedup | Chain control µs | Chain dedicated µs | Chain speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| ABA | 8192 | 151.5760 | 151.6160 | 0.99974× | 301.5928 | 300.8485 | 1.00247× |
| ABA | 16384 | 256.8653 | 254.1120 | 1.01083× | 528.6490 | 523.5690 | 1.00970× |
| BAB | 8192 | 151.0240 | 150.5920 | 1.00287× | 301.2005 | 301.2808 | 0.99973× |
| BAB | 16384 | 256.3680 | 254.0563 | 1.00910× | 523.6640 | 530.4248 | 0.98725× |

The table averages the two bracketing arm medians where present; it does not pool samples or choose minima. Every arm retains 100 samples for each of FC1, FC2, and the full chain in `results/weight442-nv-r{1,2}.json`. The unchanged FC2 also varied by roughly 0.8% at 16K, reinforcing the limited causal significance of the small FC1 improvement. `summary.json` preserves all phase comparisons.

Environment: replacement C1 devbox `fi-w4a4-pipeline-1025`, node B200-83, GPU6, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, Torch2.12.0a0+5aff3928d8.nv26.05, DSL4.7.1. The full environment and private cache epoch are recorded in `../recovery442/README.md`. No historical B1 was paired across this replacement environment boundary.

`source-manifest.json` records the immutable source snapshot and each native JSON embeds the same hashes. Dedicated core SHA256: `d2a26f71e4abbc3966d992f82e5fe8b3a1a2a38fcee9295a8333c7cf7cf3a7d1`. Weighted pipeline SHA256: `d96744090bb479b4afc215d9d68565b2a7dd0997a6ceaa52ad1cfb15bc440e87`. All preserved files are listed in `artifact-manifest.json`.
