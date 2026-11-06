# FC1 overlapping accumulator experiment

Task-local investigation against frozen `13ca1475d96839f3bf3c46699cc63204b4d3b409`. No variant here is a primary-AUTO retention result. Production changes, if selected, are composed and screened by the parent task.

## Motivation and implementation

The retained opt-in iKET instrumentation measured a 4.328 us mean accumulator-empty wait per FC1 output tile and 4.334 us epilogue body in the native NVFP4 T16384 NB2 configuration. FC2's existing ping-pong accumulator did not have that serialization. The experiment overlaps two virtual 256-column accumulator windows while preserving one pipeline barrier stage.

- `overlap_core.py` / `overlap_utils.py`: NB2-only prototype, two physical channel tiles of N128; windows start at 0 and 192. Alternate the epilogue traversal order, consume the shared 64-column interval first, fence TMEM loads, then release ownership before quantization/stores.
- `wide_core.py` / `wide_utils.py`: immutable generalized version also supporting one channel tile of N256. These files are shared with the independent one-CTA diagnostic and must not be rewritten in place.
- `compact_core.py` / `compact_utils.py`: runtime slab loop to reduce static code expansion. Correct, but rejected by the initial MXFP8 native-chain comparison.
- `footprint_core.py` / `footprint_utils.py`: actual SF columns are `tile_K / sf_vec_size`, with SFB multiplied by its 128-row blocks. Round only the protected interval to the epilogue's 32-column slab. NVFP4/SF16 keeps a 192-column window stride; SF32 uses 224. FC2 retains its original 64-column overlap ownership policy. No activation arithmetic, quantization, route mapping, metadata rounding, stage count, or extra shared-memory allocation is introduced.

For both CTA groups, an elected leader issues the MMA and the accumulator ownership release requires all 128 epilogue threads per CTA. Each transpose remains within the currently owned 32-column TMEM slab. The second channel MMA uses `mma_accumulator.iterator + allocated_n`, so both channel tiles follow the phase-selected window.

## Layout and lifetime proof

`audit_sf_footprint.py` compiles the installed CuTe layout helpers for all six input formats, one/two CTA groups, N32/N128/N256, and native/doubled K tiles: 72 configurations. It enumerates the exact byte addresses of SFA/SFB layouts and checks contiguous column coverage over all 128 TMEM datapaths.

| Native format | K tile | SFA columns per channel tile | SFB N128 / N256 | Total for NB2 or N256 | Protected columns | Accumulator windows | SF end |
|---|---:|---:|---:|---:|---:|---|---:|
| FP4, SF16 (E4M3 or E8M0) | 256 | 16 | 16 / 32 | 48 | 64 | [0,256), [192,448) | 496 |
| FP4, SF32 E8M0 | 256 | 8 | 8 / 16 | 24 | 32 | [0,256), [224,480) | 504 |
| FP8 or mixed, SF32 E8M0 | 128 | 4 | 4 / 8 | 12 | 32 | [0,256), [224,480) | 492 |

All scale-copy base addresses remain four-column aligned. A `32x128b.warpx4` scale-copy atom writes four 32-bit columns; the existing packed-byte MMA selectors remain unchanged. TMEM allocation remains 512 columns for these configurations. The overlap boundary and every transpose address are 32-column aligned.

`check_ownership.py` checks every valid-N value for both geometries and both phases, including skipped inactive slabs: 2304 ownership cases. Before release, no pending TMEM read or transpose write intersects the next accumulator window. SF32's cross-warp scalar absmax exchange is in independent shared memory and occurs after TMEM ownership release.

Source references:

- In-tree `flashinfer/gemm/kernels/dense_blockscaled_gemm_sm100.py`, overlapping accumulator calculation near lines 432–450 and alternating epilogue/release near 1532–1586.
- [CUTLASS v4.4.0 dense blockscaled persistent CuTe example](https://github.com/NVIDIA/cutlass/blob/v4.4.0/examples/python/CuTeDSL/blackwell/dense_blockscaled_gemm_persistent.py), corresponding overlap/layout calculation and release after the protected epilogue subtiles.
- [PTX tcgen05.cp semantics](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-copy-instructions-tcgen05-cp): group-2 copies use each CTA's local shared memory; the 32x128b shape requires warpx4 replication. The existing scale layout and copy atom are preserved.

## Evidence boundaries

All paired probes compare every output/SF byte to the immutable control, preserving sentinel bytes before each arm. They exercise generated FP4/FP8 outputs, per-token BF16, short K, K384 tails, multiple persistent tiles, partial routes, inactive channel tiles, GeGLU/SiTU/ReLU2, and FP16/BF16 metadata where applicable. These are task-local probes, not added repository test files.

**Discarded probe records:** `nb2overlap-formats-r1.log` and `nb2overlap-boundaries-r1.log` used 257 routed rows with only 17 source tokens at top-k8, beyond the host contract. Their passes are not correctness evidence. The corrected probes use 37 source rows and assert routed capacity. Native benchmark inputs were always valid.

Initial NB2 prototype corrected checks: 24 format + 44 boundary/activation + 4 ReLU2 cases passed. Generalized wide variant: 24 format cases passed. Compact variant: 24 NB2 + 24 N256 cases passed after fixing its dynamic alignment annotation and compile-time guard around an absent pipeline.

Timing uses the same native preparation, actual routing, 10 warmups, 100 cold-L2 CUDA-graph CUPTI samples and median as the prior phase diagnostics. Whole-chain probes compare final output bytes before timing. No old primary baseline is rerun; adjacent controls are frozen13ca, and fixed-tactic numbers are diagnostic only. Full samples, environment, input shape, harness hash, order and selected tactic are in each JSON.

## Final focused checks and timing

The footprint variant passed **260 paired cases**: NB2 formats24, N256 formats24, NB2 boundaries44, FC2 formats48, small-N/ReLU2/M384-tail reuse76, and N256 boundaries44. `results/nb2overlap-footprint-*.log` contain the full outputs. The host layout audit passed72 configurations and the ownership checker passed2304 states.

Whole-chain medians below use every one of the100 samples; no quartile or minimum replaces the reported metric. All measured arms passed final-output byte comparison. Mixed W4A8 keeps its existing producer/epilogue structure; its SF allocation is compacted consistently.

| Record | Tokens | Control us | Footprint us | Control / footprint |
|---|---:|---:|---:|---:|
| nv-chain-r1 | 4096 | 211.424 | 207.296 | 1.0199 |
| nv-chain-r1 | 8192 | 323.425 | 311.217 | 1.0392 |
| nv-chain-r1 | 16384 | 566.561 | 545.313 | 1.0390 |
| mx-chain-r1 | 4096 | 330.913 | 329.377 | 1.0047 |
| mx-chain-r1 | 8192 | 478.322 | 467.826 | 1.0224 |
| mx-chain-r1 | 16384 | 867.859 | 834.178 | 1.0404 |
| mx-chain-r2 | 4096 | 331.280 | 329.233 | 1.0062 |
| mx-chain-r2 | 8192 | 477.858 | 468.594 | 1.0198 |
| mx-chain-r2 | 16384 | 828.899 | 862.979 | 0.9605 |
| mx-chain-gpu1-r1 | 16384 | 865.633 | 857.280 | 1.0097 |
| mx-chain-gpu1-r2 | 16384 | 905.697 | 862.721 | 1.0498 |
| mx-monitored-r1 | 16384 | 869.857 | 882.433 | 0.9857 |
| mx-monitored-r2 | 16384 | 876.481 | 869.377 | 1.0082 |
| w4a8-chain-r1 | 4096 | 259.616 | 259.904 | 0.9989 |
| w4a8-chain-r1 | 8192 | 433.632 | 433.329 | 1.0007 |
| w4a8-chain-r1 | 16384 | 783.521 | 773.874 | 1.0125 |

NVFP4's benefit repeats across the initial and opposite-order runs. MXFP8 improves consistently at4K/8K, but its16K complete medians are order/run-sensitive, so this experiment does **not** establish a retained MXFP8 prefill gain. The compact runtime loop is rejected; the final footprint variant keeps static unrolling. N256's early NVFP4 check was smaller/near-neutral versus its own N256 control; paired-tactic or AUTO selection belongs to the composed campaign.

### Drift investigation

All eight MXFP8 T16384 chain records have the same expert-count histogram SHA256 and tile-valid-row SHA256. The two monitored repeats also match their complete routing-index SHA256. No routing distribution change explains the timing difference. The full hashes and summaries are retained in `results/summary.json` and the original JSONs.

`monitor_run.py` starts a read-only100ms nvidia-smi sampler and always terminates/reaps it. Each measured arm lasts roughly0.15s, giving only1–2 telemetry samples. One control arm reports1725MHz and an active software power cap, versus1965MHz in the other samples; memory stays3996MHz. No sampled thermal or hardware-power-brake throttle is active. This sparse evidence is compatible with transient power/clock effects but does not prove their contribution to the entire within-arm drift. Raw CSVs, cleanup metadata and `results/telemetry-summary.json` are archived. Timing remains the unchanged100-sample median.

### Reproduction

Run from remote `candidate/` using CUDA13.2, `nvcr.io/nvidia/pytorch:26.05-py3`, CuTeDSL4.7.1 on c1 B200. The remote production checkout remains frozen13ca; the imported experiment modules are immutable task-local files.

```bash
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_fc1_formats.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_wide_formats.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_boundaries.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_wide_boundaries.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_fc2_formats.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/run_paired.py --variant footprint --script probe_footprint_extra.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/audit_sf_footprint.py
CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. ../.venv/bin/python ../scripts/nb2_overlap_experiment/probe_chain_modes.py --repo . --expected-head 13ca1475d96839f3bf3c46699cc63204b4d3b409 --tokens 4096,8192,16384 --output ../logs/unique-mx-chain.json --tactic '[128,[[512,128],[2,1],false],[[128,128],[1,1],false]]' --mode mxfp8 --variants baseline,footprint
```

The NVFP4 command uses `probe_chain.py` without `--mode` and FC2 tactic `[256,128],[2,1]`; mixed uses `--mode w4a8`. `probe_chain_monitored.py` changes only observability metadata (timestamps/routing hashes), not preparation, timing parameters or measured work. `monitor_run.py --gpu 1 --output <csv> -- <benchmark command>` wraps it; the actual commands are saved in each telemetry metadata JSON.

## Handoff

`accumulator-overlap.patch` is generated against verified exact13ca production sources, with production imports restored. SHA256: `cfabdab6188ec4129d07793edd80edb6f325d9125a722a1f19dfd7fd7831ee93`. Full source forms are `production_candidate_core.py` and `production_candidate_utils.py`.

Compose this patch with current production rather than replacing its files: retain the newer cached-shape Constexpr annotations, reduced compiled-call ABI, weight-cache policy, disabled-by-default iKET instrumentation, and combine rounding changes. Only the shared Blackwell core and its epilogue utility change. No new stage, launch, public API, tactic, test file, MegaMoE code, or format-specific performance exception is added. The parent owns composition, commit and primary AUTO retention.
