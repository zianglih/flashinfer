# Split block-scaled FC2 epilogue iteration

The selected epilogue variant preloads every live output row and its final-rounded scale before processing the tile's 32-token groups, then keeps this metadata in registers with static group indices. The actual activation, transpose, quantization, and store math lives in one shared helper. FC1 retains its original dynamic group loop. The store cap increases from 128 to 256 bits for BF16, FP16, and FP32; FP8/FP4 fragment stores remain unchanged. This is an integrated checkpoint; full-MoE retention has not yet been established.

Production file: `flashinfer/fused_moe/cute_dsl/blackwell/utils.py`, SHA256 `d5d7060d60b189fd2df03c9c739884d2d839fb56f533cdf32456f3e190875018`. The production file uses `..common.kernel_utils`; the experiment uses `.kernel_utils` inside its isolated package. The actual epilogue implementation is identical, and the production-relative import was verified remotely against the real FlashInfer common package. Exact candidate snapshot: `epi_trial/integrated_utils.py`, SHA256 `69dfd49f2e1bde42b93e1d2545e8d0e0d08bc60b2220885447b3dec9e82d2d5b`. Frozen control epilogue SHA256 `1e4a5e1603b0cc7d24e88b815432069b5cc269e2c347f506f56b007255a56f0e`. All compared cores include the same Gather4 integration; this experiment changes only the epilogue. Constructor/run ABI, M128/up16gate16 layout, routing destinations, and per-token BF16/FP16 metadata rounding are preserved.

## Focused exact checks

All 102 task-local paired cases passed with identical output bytes and SF bytes, using the existing phase probes:50FC2 cases across BF16/FP16/FP32/E4M3/E5M2 output, BF16/FP16/FP32 metadata, per-token/per-tensor scales, N16/32/64/128/256 and partial routes; 20 NVFP4 FC1 cases; 8 N256 FC1 cases; 24 FC1 dtype/quantization/per-token cases. No production test file or new reference contract was added. This is focused iteration validation; fused atomic combine bit-exactness is not claimed. Ruff, Python compilation, and git diff checks passed.

Raw logs: `../../logs/epi-integrated-probe_*.py.log`.

## Controlled phase measurements

C1 B200, single GPU2, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA 13.2, Torch 2.12 development, CuTe DSL 4.7.1. Balanced 16,384 routed rows, 32 experts, FC2 hidden 7,168/reduction 2,048, grid 148, 4 pipeline stages. CUPTI + CUDA graphs, cold L2, 3 warmups and 15 repeats, median microseconds. These are phase diagnostics, not the full-MoE retention benchmark. Reverse-order R2 ran the candidate before the control:

| Mode | N | Control (us) | Candidate (us) | Speedup |
|---|---:|---:|---:|---:|
| nvfp4 | 128 | 298.848 | 232.928 | 1.283x |
| nvfp4 | 256 | 249.248 | 171.456 | 1.454x |
| mxfp8 | 128 | 395.424 | 329.760 | 1.199x |
| mxfp8 | 256 | 317.024 | 239.871 | 1.322x |
| w4a8 | 128 | 382.527 | 314.688 | 1.216x |
| w4a8 | 256 | 306.336 | 228.737 | 1.339x |

Raw complete phase outputs: `../../logs/epi-r1-{baseline,integrated}-*.log` and `../../logs/epi-r2-{baseline,integrated}-*.log`.

Causal screens at N256 (NVFP4 / MXFP8 microseconds): control 248.8/316.9; only 256-bit stores 212.2/279.2; metadata preload 206.2/275.6; plain full loop unroll 251.4/316.6; combined shared helper 171.6/240.1. Thus plain unrolling does not explain the preload gain.

Rejected task-local variants remain archived: scalar direct store, coalesced metadata broadcast, warp-shuffle transpose, permuted-lane shuffle, BF16/FP16 MOVM transpose, and single-/multi-stage shared-memory bulk stores. None changed production. Direct scalar stores also regressed sparse N16, so no special decode path was added.

## Reproduction

From the remote candidate checkout:

```bash
CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python -u \
  ../scripts/epilogue_experiment/run_paired.py \
  --variant integrated --script probe_fc2_contract.py

CUDA_VISIBLE_DEVICES=2 PYTHONPATH=. ../.venv/bin/python -u \
  ../scripts/epilogue_experiment/run_variant.py \
  --variant integrated --script probe_core_perf.py \
  --repo . --tokens 16384 --mode mxfp8 --tiles 128,256 \
  --factors 1 --stages 4 --phases fc2
```

Control uses `--variant baseline`. Other phase modes are `nvfp4` and `w4a8`. Additional exact probes are `probe_fc1.py`, `probe_n256_fc1.py`, and `probe_dtype_gather.py`. Existing run scripts freeze module imports and use separate kernel caches; no production source is rewritten remotely during a run.

## Sparse route and compiler-resource checks

| N | Valid routes per expert | Control (us) | Candidate (us) |
|---|---:|---:|---:|
| 16 | 1 | 64.352 | 64.479 |
| 16 | 4 | 64.640 | 64.832 |
| 16 | 16 | 65.344 | 64.928 |
| 32 | 1 | 65.888 | 66.336 |
| 32 | 4 | 65.728 | 66.208 |
| 32 | 16 | 67.392 | 66.209 |

Sparse diagnostics use the same phase harness, 32 experts, 5 pipeline stages, and capacity N × 32. Changes at 1/4 live routes are at most 0.48 us (<0.8%); 16 live routes improve. Full pipeline decode retention remains the parent benchmark’s responsibility.

| MXFP8 FC2 N256 resource | Control | Candidate |
|---|---:|---:|
| Registers per thread | 104 | 120 |
| SASS instructions | 1,208 | 2,448 |
| SASS code extent | 19,328 B | 39,168 B |
| Stack allocation | 1,024 B | 1,024 B |
| Local load/store sectors | 0 / 0 | 0 / 0 |
| Explicit register-spill reads/writes | 0 / 0 | 0 / 0 |
| Executed global stores | 458,752 | 229,376 |

SASS confirms `STG.E.ENL2.256` in the candidate. NCU SourceCounters does not attribute sector counts to those instructions, so its zero sector fields are unavailable values, not zero traffic. Raw NCU reports remain on the remote box; raw metric/SASS CSV files are preserved under `../../logs/epi-*-ncu-*.csv`. `resource_summary.json` contains the extracted counts. No additional shared-memory staging or allocation was retained.
