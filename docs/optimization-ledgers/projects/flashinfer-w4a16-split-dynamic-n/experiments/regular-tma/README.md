# Regular-TMA W4A16 preparation experiment

Publication follow-up: the selected candidate below was committed and pushed as `97e8d0c8bb86b352ccb42f2654ddc2ab9a8e6939`. The subsequent user-authorized fresh full-PR ABBA comparison is recorded in [pr-refresh-20261025](../pr-refresh-20261025/RESULTS.md): 1.042566629× overall, 1.037349850× decode and 1.056606659× prefill versus the original pre-PR baseline on the same GPU. The earlier experiment ledger and its historical controls below remain unchanged.

Scope: keep the existing regular-TMA grouped GEMM mainloop and optimize the standalone BF16 permutation for split CuTe DSL W4A16. Preparation variants change `blackwell/moe_w4a16.py` and the new `blackwell/moe_w4a16_prepare.py`. The isolated static-M/K variant additionally specializes the GEMM wrapper in `blackwell/moe_w4a16_kernel.py`; its mainloop bodies remain unchanged. The separate `flashinfer-regular-tma/` checkout starts at `36740c36a32a6c6d1c7d8162823fe823912de741`. After selection, the user requested the combined candidate in the main workspace: `flashinfer/` now contains identical measured sources unstaged, and the preceding Gather4 source/diff is archived in `../gather4/workspace-before-regular-tma/`. See `final-candidate/WORKSPACE_INTEGRATION.json`. No commit, index update, or PR edit is part of this experiment.

## Original-input alignment

The combined candidate keeps a 32-byte fast path and an explicit 16-byte fallback. This is host dispatch between separately compiled copy widths; the fast kernel does not contain a runtime alignment branch. The existing native permutation checks BF16 `hidden_size % 8 == 0` in `csrc/nv_internal/tensorrt_llm/kernels/cuteDslKernels/moeUtils.cu:115`, then uses `uint4` pointers at lines 91–94. It does not check the original activation pointer or strides. Dense rows and 16-byte base alignment were implicit preconditions, not a complete public validation contract.

The W4A16 runner validates dtype and dimensions but forwards the original activation tensor. GEMM construction does request 32-byte alignment for its activation pointer, and FlashInfer's `make_ptr` wrapper asserts the supplied alignment; that pointer is the newly allocated routed workspace, not the caller's original activation tensor. Normal supported weight geometry makes row width sufficiently aligned, but row width cannot guarantee the original base address.

A contiguous BF16 view offset by eight elements from a 32-byte-aligned allocation has a 16-byte-aligned base, and `.contiguous()` leaves an already-contiguous view unchanged. Requiring 32-byte original-input alignment would reject this case without improving the existing wide-copy kernel. The retained helper therefore checks input/output addresses and row bytes explicitly: 256-bit copies when all are 32-byte aligned, 128-bit copies when all are 16-byte aligned, and a clear error otherwise. The completed 48-case byte probe includes offset views and 32 native-contract comparisons. No stronger alignment contract or new GPU run was introduced during workspace integration.

## Environment

New C2/infra devbox `w4a16-regular-tma-1025`, explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, remote root `/workspace/flashinfer-w4a16-regular-tma`. The image catalog was rechecked before requesting the box. Setup reproduced Torch `2.12.0a0+5aff3928d8.nv26.05`, CUDA13.2, CuTe DSL4.7.1, CUPTI Python13.4.0/library13.4.58, and compiler/NVVM distribution13.3.73. Runtime and selected distribution paths are recorded separately from the global DSL4.4.2 metadata still visible in the system-site-packages environment.

The allocated host is again `hu-pdx-7`; all GPU UUID/model/power records match the historical evidence. GPU0 is `GPU-edf3141e-7e43-ff20-2c4e-a0e11b5ae000`, NVIDIA B300 SXM6 AC, 1100W. Strict same-device comparison is therefore available. GPU identity checks remain strict. Compiler installation fingerprints differ only in the independently audited generated entrypoint records described below; any unaudited metadata difference fails. A future different-host run would need an explicitly labeled descriptive report, not a silent fallback.

Setup logs: `logs/setup-remote.log`, `logs/sync-setup.log`; remote `logs/setup.log` and `environment.json`. The remote baseline clone and candidate worktree both start at the pinned HEAD. Third-party headers are shared by project-local symlinks; candidate Python sources are independent.

## Reused controls and measurement

Both controls come from the preserved Gather4 `results/split-v3` report: `before-r1/r2` are the original HEAD baseline, and `after-r1/r2` are the final uniform Gather4 candidate. The evidence is copied unchanged into remote `experiments/regular-tma/history/gather4-split-v3`. Neither control is rerun. This is a comparison against historical sweeps on the same GPU, without a fresh trailing control to bracket drift.

Native `benchmarks/bench_moe_deepseek.py`, H7168/I2048, simulated EP8 on one GPU, 256 experts/32 local, top-k8, SwiGLU, unfused finalize, PDL1, seed42. Timing remains 10 warmups plus 100 native cold-L2 CUDA-graph CUPTI samples per row, with independent AUTO. The helper extends only runtime source-hash metadata to include the new preparation file.

Screens use T16/T512/T4096/T16384 and have no aggregate retention metric. A directed full campaign runs candidate R1/R2 over 1,2,4,8,16,32,64,128,256,512,4096,8192,16384. T1/T2 are reported and excluded from retention. Primary full-grid ratios use `sqrt((ReferenceR1 * ReferenceR2)/(CandidateR1 * CandidateR2))`; overall, decode T4–512, and prefill T4096/8192/16384 geometric means are reported separately against both saved controls.

## Helpers and commands

- `setup_remote.sh`: pinned environment and independent remote source worktree setup.
- `run_initial_screen.sh`: deploy v1, exact boundary check, then screen if exact passes.
- `run_variant_screen.sh`: deploy a specified saved variant, exact boundary check, then screen; refuses existing output names.
- `run_probe.sh`: candidate-only subset with strict runtime/GPU identity checks against saved evidence.
- `run_followup_campaign.sh` / `run_campaign.sh`: candidate R1/R2 only; the baseline reuse argument is mandatory.
- `snapshot_sources.py`: full source hashes, untracked helper bytes, complete addition patch, and untouched Git index.
- `summarize_results.py`: strict full-campaign checks against HEAD, with exactly the two preparation paths allowed to differ by default. The separate `--allow-wrapper-specialization` flag permits the GEMM file for the isolated static-M/K candidate; `compare_historical.py` requires the same explicit flag for that candidate.
- `compare_historical.py`: full raw medians and comparisons against both saved controls, complete active-token cache records and cumulative caches kept separate, source/UUID/runtime checks, and no overwrite.
- `capture_prep_codegen.py`: separate preparation-kernel codegen evidence; do not overlap compilation with timed sweeps.
- `archive_native_jit.py`: inventory completed native JIT targets, then archive only explicitly selected targets with native source/compiler/ABI provenance after all benchmarking finishes.

Example remote screen and historical comparison after the candidate is ready:

```bash
project=/workspace/flashinfer-w4a16-regular-tma
history="$project/experiments/regular-tma/history/gather4-split-v3"
bash "$project/experiments/regular-tma/run_probe.sh" \
  "$project" "$project/candidate" "$history" <new-label>
"$project/.venv/bin/python" "$project/experiments/regular-tma/compare_historical.py" \
  "$project/experiments/regular-tma/probes/<new-label>" "$history" --kind probe \
  --compiler-record-audit <saved-audit-receipt>
```

Example full campaign, only when directed:

```bash
project=/workspace/flashinfer-w4a16-regular-tma
history="$project/experiments/regular-tma/history/gather4-split-v3"
output="$project/experiments/regular-tma/results/<new-label>"
export W4A16_CONTAINER_IMAGE=nvcr.io/nvidia/pytorch:26.05-py3
bash "$project/experiments/regular-tma/run_followup_campaign.sh" \
  "$project" "$project/baseline" "$project/candidate" "$output" "$history"
"$project/.venv/bin/python" "$project/experiments/regular-tma/summarize_results.py" "$output" \
  --compiler-record-audit <saved-audit-receipt>
"$project/.venv/bin/python" "$project/experiments/regular-tma/compare_historical.py" \
  "$output" "$history" --kind full --compiler-record-audit <saved-audit-receipt>
```

## Execution ledger

V1 exact24 started at 2026-10-25 12:15:41 UTC. Its initial 300-second bound expired at 12:20:42 during native FlashInfer routing compilation, before numerical output. The initial log/exit124 are preserved as `smoke-prep-v1-initial-timeout.*`. The surviving compiler children were allowed to finish; their commands and CPU times are preserved in `logs/native-orphans-1224.log` and `logs/native-orphans-followup.log`. They compile only `sm_103a`. After all orphan children cleared, exact24 resumed with a 900-second bound at 12:26:41. Native source/build lists remain unchanged; all compilation time is outside benchmark medians.

The separate GPU1 V1 codegen capture completed with exit0 before the exact retry; the screen is gated on its completion marker to avoid compilation overlap with measured sweeps. All five candidate screens below completed and passed exact24. Their comparisons passed source, device, runtime, routing, and timing validation with the explicitly audited compiler-record equivalence below. The initial four screens proceeded sequentially: V1, early-PDL V2, isolated 256-thread preparation, and isolated static-M/K. The last two are based on V1, not combined with V2. A fifth screen combines 256 threads with early PDL. Each requires exact24 before timing and preserves a full source snapshot. See `EARLY_PDL_AUDIT.md` and `FOLLOWUP_VARIANTS.md`.

## Compiler installation provenance

The new venv path changes hashes in the generated `tvm-ffi-config`, `tvm-ffi-stubgen`, and `run-iket` entrypoints, and therefore two distribution RECORD digests. An independent read-only audit verified all 361 recorded files in those two distributions and reconstructed the exact historical whole-stack fingerprint using only those three shebang/RECORD hash-and-size replacements in memory. Both `direct_url` values remain null. Installed files and raw cache metadata are unchanged. The old venv is absent; historical `.pyc` or unrecorded modifications are outside the original fingerprint boundary.

The comparison helpers accept this specific equivalence only with `--compiler-record-audit evidence/setup/compiler-record-relocation-audit.json`, SHA256 `20e561ef5b3e8f8fdde8fcfef981df986bd806c6e4054a2ab70499891fd00aa8`. The receipt is embedded in reports; exact old/new fingerprints are pinned, every other metadata field must match, and missing receipt, unrelated fingerprint changes, and changed GPU metadata were checked to fail. This is not a generic normalization rule. See `audit_compiler_record_relocation.py` and the saved receipt.

## Completed screens

Each value below is one native sweep median in microseconds. The four historical columns are unchanged saved data; each candidate column is a separate fresh AUTO screen. These four points have no aggregate retention metric. Complete source receipts, raw logs, per-token tactic records, cumulative caches, and both historical comparisons are preserved in each `probes/<label>/HISTORICAL_COMPARISON.json`.

| T | HEAD R1 | HEAD R2 | Gather4 R1 | Gather4 R2 | Prep V1 | Early PDL V2 | Threads256 | Static M/K | Threads256 + early PDL |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 76.9610 | 76.9605 | 72.4490 | 72.3370 | 77.0400 | 74.4650 | 75.3920 | 77.9050 | 73.8885 |
| 512 | 159.7130 | 159.7135 | 161.2170 | 160.6090 | 158.4975 | 158.1295 | 157.5690 | 158.1445 | 157.1850 |
| 4096 | 301.7310 | 300.4825 | 329.8745 | 329.3465 | 297.4905 | 296.1300 | 295.3470 | 293.6340 | 296.3540 |
| 16384 | 1235.8340 | 1202.2180 | 1215.5460 | 1205.3705 | 1175.5770 | 1203.3375 | 1155.4815 | 1218.0740 | 1197.5295 |

All five candidates passed the same exact24 boundary node. V1 took 506.00s including native build; subsequent exact24 runs took 17.25s (V2), 16.84s (threads256), 16.56s (static M/K), and 16.73s (threads256+early PDL). Complete raw pytest logs are in `logs/smoke-<label>.log`. Initial timeout124 and compiler provenance remain preserved separately.

All five candidates selected identical complete active-token records at T512 (M256/N32/C2), T4096 and T16384 (M256/N192/C2), for both FC1/FC2. T16 selected different tactics across screens, so small-token changes cannot be attributed solely to preparation scheduling. T4096 records match all historical arms; T512 matches saved HEAD; T16384 matches saved Gather4 but differs from saved HEAD. Full record comparisons, including cumulative-cache differences, are in the JSON reports.

Static M/K is excluded from the full campaign: this screen showed no broad benefit to justify extra specializations. Threads256+early PDL improves T16/T512 relative to threads256 while losing T4096/T16384 in the one-screen comparison. Both proceed to interleaved full grids; no minimum is selected or pooled across screens.

## Full campaign and retained local candidate

The two new preparation candidates completed A1,B1,B2,A2 in `results/interleaved-v1/`: A=threads256, B=threads256+early PDL. Each executes two complete 13-token sweeps with the established 10/100 cold-L2 native timing. `executed-order.txt` and timestamped `execution.log` record global order; each candidate subfolder includes unchanged copied historical HEAD arms and its two new arms. No historical HEAD or Gather4 timing is rerun. Per-arm complete source snapshots must match within each candidate. The regular-TMA GEMM source and 23 offered tactics remain unchanged. T1/T2 are reported and excluded from aggregate decisions.


B (256 threads plus early PDL) is retained locally for review, with its exact measured preparation SHA256 `e569c3ac37560d07beb4ad86efb9f992ab418bae580ae1606f813f46cd92c606`. Source remains unstaged; no PR write is part of this experiment. All four arms completed at 12:55:36 UTC. Full validation passed the source/device/runtime/routing/timing checks with the explicit compiler-record receipt.

The paired overall speedup is 1.021576946× versus saved HEAD (+2.1577%) and 1.013725720× versus saved Gather4 (+1.3726%). Both HEAD-relative overall repeats improve (1.020547827× and 1.022607103×). Against Gather4, B is 0.994156641× on decode (Gather4 remains about 0.59% faster) and 1.067813789× on prefill (B is 6.78% faster). There is no uniform decode-win claim. The modest gains and historical-control drift boundary remain explicit.

T8192 has identical complete FC1/FC2 tactics in all eight historical/new arms: M256/N128/K256, cluster 2. A regresses versus HEAD in both repeats. B is effectively flat in the paired ratio 0.999164976×, with mixed repeat ratios 0.985007272×/1.013526171×. At T16384 B improves in R1 (1.037935072×) and loses 0.42% in R2 (0.995772049×). Direct interleaved A/B favors B overall by 1.1904%, with both aggregate repeat directions positive; B is 0.31% slower than A at T16384. No minimum selection or pooling is used.

| Comparison | Group | R1 | R2 | Paired |
| --- | --- | ---: | ---: | ---: |
| Saved head / B | Overall | 1.020547827× | 1.022607103× | 1.021576946× |
| Saved gather4 / B | Overall | 1.013025507× | 1.014426416× | 1.013725720× |
| Saved head / B | Decode | 1.022339214× | 1.027332486× | 1.024832809× |
| Saved gather4 / B | Decode | 0.992298815× | 0.996017945× | 0.994156641× |
| Saved head / B | Prefill | 1.015786126× | 1.010112069× | 1.012945125× |
| Saved gather4 / B | Prefill | 1.070437878× | 1.065196134× | 1.067813789× |
| A / B, fresh interleaved | Overall | 1.010041399× | 1.013770404× | 1.011904184× |
| A / B, fresh interleaved | Decode | 1.012468614× | 1.017029959× | 1.014746724× |
| A / B, fresh interleaved | Prefill | 1.003597237× | 1.005129237× | 1.004362945× |

Complete raw native sweep medians in microseconds follow. T1/T2 are shown but excluded from aggregate decisions.

| T | HEAD R1 | HEAD R2 | Gather4 R1 | Gather4 R2 | A1 | A2 | B1 | B2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 33.6640 | 33.2800 | 29.5045 | 29.5365 | 33.0560 | 32.1600 | 30.7525 | 31.5520 |
| 2 | 39.6165 | 40.2560 | 36.0000 | 35.7120 | 39.5200 | 38.5600 | 36.8800 | 36.6240 |
| 4 | 54.4000 | 54.3680 | 51.2960 | 51.4885 | 53.6000 | 53.6485 | 51.2960 | 51.0410 |
| 8 | 68.6730 | 68.0005 | 66.7045 | 66.7205 | 67.2330 | 67.8565 | 66.2885 | 66.8490 |
| 16 | 76.9610 | 76.9605 | 72.4490 | 72.3370 | 75.4570 | 76.2085 | 75.5050 | 74.5280 |
| 32 | 109.2010 | 110.2410 | 105.7935 | 106.5125 | 109.4560 | 109.4730 | 108.3365 | 107.6170 |
| 64 | 143.7135 | 145.7610 | 139.4090 | 140.0495 | 143.8725 | 143.8885 | 141.6335 | 141.8570 |
| 128 | 146.5935 | 146.7530 | 143.6490 | 143.3290 | 146.4970 | 145.8570 | 145.2015 | 144.5125 |
| 256 | 154.7530 | 155.3130 | 152.0965 | 152.2570 | 153.5850 | 153.3130 | 152.8970 | 152.7060 |
| 512 | 159.7130 | 159.7135 | 161.2170 | 160.6090 | 157.0090 | 157.1210 | 156.6410 | 156.5775 |
| 4096 | 301.7310 | 300.4825 | 329.8745 | 329.3465 | 295.7620 | 295.6340 | 294.3220 | 294.2425 |
| 8192 | 603.4125 | 594.6130 | 656.6770 | 634.5170 | 616.9965 | 595.9250 | 612.5970 | 586.6775 |
| 16384 | 1235.8340 | 1202.2180 | 1215.5460 | 1205.3705 | 1189.1615 | 1201.2900 | 1190.6660 | 1207.3225 |

Reports: `results/interleaved-v1/CANDIDATE_COMPARISON.md` contains direct A/B repeat ratios for every token. Both candidate subfolders contain `RESULTS.md/json` versus HEAD and `HISTORICAL_COMPARISON.md/json` versus both saved controls. Full raw cache records and checksums remain available; historical evidence was not rewritten.

## Native build reuse

The first full arm incurred a second native build because the original screen wrappers used `FLASHINFER_NVCC_THREADS=4`, while the full runner inherited the native default 1. That changes ninja's command even though native source is identical. The active build was allowed to finish without changing source/build lists or starting duplicate compilers. This is an avoidable setup invalidation, outside measured samples. Initial wrappers and the exact executed full runner are preserved in `evidence/initial-runners/` and the campaign artifacts.

Future local setup/screen/campaign helpers explicitly use `FLASHINFER_NVCC_THREADS=1` and `MAX_JOBS=32` consistently. This later helper correction does not rewrite the already running campaign or its receipts. `preflight_native_cache.py` requires explicit thread 1, captures complete cached ninja commands, checks the expected source path, and performs `ninja -n` on explicitly selected targets before a new campaign. It refuses active compilers and flags a dirty or incompatible cache so its build can be completed before timing. Native dependency checks remain enabled. The four useful completed targets were inventoried and archived after all GPU work: `moe_utils`, `fp4_quantization_103`, `dsv3_fused_routing`, and `trtllm_utils`. Their 47 files occupy 39.98MB uncompressed and 14.38MB compressed. Exact native source, compiler, ABI, path, and command provenance is in `native-jit-cache/MANIFEST.json`; restoration boundaries and commands are in `native-jit-cache/RESTORE.md`. The final dry-run preflight passed every target. A future restoration is not yet tested and must repeat those checks.

## Final validation and cleanup

Selected B passed the existing 24 exact MoE boundary cases before timing and 48 post-timing preparation byte/canary cases at H7168. The latter cover top-k3/8, 32-byte and exactly 16-byte input/output alignment, PDL off/on, zero/three active tiles, zero capacity, and untouched padding/unused capacity/prefix/suffix. 32 cases also match the native preparation kernel byte-for-byte; 16 zero-capacity cases verify no compilation and unchanged allocation bytes. Receipt: `validation/selected-B-alignment.json`. This is focused exact and boundary coverage; no sanitizer run was performed.

All four selected-B codegen specializations completed after timing. Top-k3/8 × 256/128-bit copies use 256 threads, 28/32 registers respectively, zero local bytes, and 8 driver-reported active CTAs/SM. Actual 256-bit loads/stores are present on the aligned path; the exact16-byte path uses 128-bit operations. Full PTX, compiled and reassembled cubins, SASS, compiler diagnostics, and driver resources are preserved under `codegen-selected-256threads/`.

The final selected source manifest exactly matches measured B. All 525 files in the complete remote evidence bundle and all 47 native-cache archive members were SHA-verified locally; see `evidence/FINAL_ARTIFACT_VERIFICATION.json`. `evidence/final-remote/` retains the remote experiment/log/environment files, including source snapshots and original executed runners. All useful task artifacts were fetched before cleanup. The task devbox `w4a16-regular-tma-1025` was deleted from C2/infra; `logs/devbox-delete.log` records the successful deletion. Local source changes remain unstaged and the Gather4 checkout remains unchanged.
