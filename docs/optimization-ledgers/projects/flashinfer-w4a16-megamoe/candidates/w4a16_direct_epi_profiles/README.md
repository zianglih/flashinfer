# Held direct-epilogue full NCU capture

Preparation only: no source installation, staging, profiler launch, report import, or GPU work. Wait for the current full AUTO invocation, its source/native/idle closure, and root's retention decision. Then bind the actual retained source and matching preflight in a fresh copy of `binding.template.json`: source7c3d if BAR1 is retained, or removal sourceeb036 if reverted. The template deliberately binds neither source. This is a kernel diagnostic; it supplies no AUTO timing samples.

## Representative workload

Global T1024 means 128 live source tokens per rank on EP8. Use the existing benchmark H7168/I2048/E256/top-k8 workload with BF16 activations and NVFP4 weights, exactly two decode WGs / five total WGs. Both complete historical default controls (owned098c and central57e2) selected this exact T1024 dictionary; their unchanged proof paths and hashes are recorded in the template. This selection is representative and does not claim the pending run chose the same winner.

```json
{"cluster_shape_mnk":[2,1,1],"epi_flag_batch":[2,4],"flag_batch":4,"group_hint":512,"in_kernel_fc2_reduce":false,"load_balance_mode":"atomic_counter","mma_tiler_mnk":[256,64,256],"num_sched_stages":2,"token_back_mode":"epi_warps","use_2cta_instrs":true}
```

One profiled Mega invocation per rank follows the existing three warmups. The command omits `--ncu-metrics`, which makes the current benchmark emit `--set=full`, including the existing Source Counters section. No selected metric filter replaces the full set. The benchmark preserves one NCU process per rank, TCP communicator with eight peers, strict application replay matched by grid, lockstep `stage::MegaMoE/`, and fresh PrefixStore keys on each worker restart. `--warp-sampling-max-passes=1` bounds only adaptive warp sampling; it does not cap full-counter replay passes. Source import and lineinfo remain enabled by the existing benchmark.

## Exact reuse and necessary changes

- `run_ncu_full_t1024.sh` adapts the completed `w4a16_current_best_profiles/run_ncu_full_t4096_0909e.sh`: T4096/N128/reuse becomes T1024/N64/epi; output is `profiles/direct-epi-0910a-ncu-full-t1024-001`; native roots become the observed 0910a roots. Source/preflight/latest native inventory are required launch inputs, not historical literals. The script copies these inputs and the existing native-environment JSON into report metadata and records their hashes.
- `close_full_capture.py` retains the original report-header/count, source inventory, native delta, idle, download-manifest and raw archive logic. It binds `geometry_source_provenance.REQUIRED_FILES` from the selected current manifest because the historical helper's default list still names the deleted shim package. Native roots/before inventory now come from the copied capture inputs. The same existing pure `candidates/cuda132_recovery_0909e/native_inventory.py` is reused; its name is historical, while its inventory function takes the actual 0910a roots.
- `read_full_reports.py` retains the existing full metric/action/section/embedded-source API reader. Its only code change is the required embedded Mega source path: `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py`. Shared decoder source remains `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py`.
- Reuse `candidates/w4a16_current_best_profiles/export_full_csv_0909e.py` byte-exactly. It already accepts any token-shaped report folder and exports every rank in automatic and base units with commands, stderr, return codes, hashes, and a CSV archive.

`helper-files-with-pc.json` is the complete unbound dependency inventory, **not a staging request**; it extends the initial capture/aggregate-export map with the PC analysis steps below. After the retention decision, the runtime owner adds the selected source manifest, matching preflight, actual latest native inventory and completed AUTO/retention receipts to the normal existing stage map. No product or benchmark source change is required. Preserve the installed NCU Python API path: the existing reader uses `/opt/nvidia/nsight-compute/2026.1.1/extras/python`; if the installed tool path differs, bind that path in a fresh reader copy before use. Do not silently import a different API version.

## Capture and download after admission

The runtime owner supplies absolute paths and the selected source ID from the completed retention decision. Use the existing managed devbox transport; the shell below runs on the already admitted node from the project root.

```bash
export PROFILE_SOURCE='<actual retained source ID>'
export PROFILE_SOURCE_MANIFEST='<absolute matching source-manifest.json>'
export PROFILE_PREFLIGHT='<absolute matching preflight.json>'
export PROFILE_NATIVE_INVENTORY='<absolute latest closed native-cache-after.json>'
bash candidates/w4a16_direct_epi_profiles/run_ncu_full_t1024.sh
/usr/bin/python3 -B candidates/w4a16_direct_epi_profiles/close_full_capture.py
```

Before launch, bind and verify these inputs through the existing source/native/idle checks; an AUTO closure for source7c3d does not establish a subsequent reverted sourceeb036. The capture uses a fresh output-owned DSL lineinfo cache, CUDA driver cache and fixed-knob cache; preexisting native compilation caches remain the recorded 0910a roots. Preserve any failed attempt under its original name.

After true exit and closure, download `profiles/direct-epi-0910a-ncu-full-t1024-001-download.tar.gz` and verify its emitted size/SHA and `download-manifest.json`. It contains eight `ep_w4a16_megamoe_t1024.rank{0..7}.ncu-rep` files plus logs, exact command, source/preflight/native input snapshots, versions, hardware UUIDs, timestamps and closure metadata. Driver/DSL cache directories are intentionally excluded, as in the completed helper. CPU-only exports, executed after capture, are:

```bash
OUT=/workspace/flashinfer-w4a16-megamoe/profiles/direct-epi-0910a-ncu-full-t1024-001
/usr/bin/python3 -B candidates/w4a16_direct_epi_profiles/read_full_reports.py "$OUT"
/usr/bin/python3 -B candidates/w4a16_current_best_profiles/export_full_csv_0909e.py "$OUT"
```

Download the full `full-report-verification/` tree and CSV archive as well; preserve their API metric names/counts, details sections, embedded-source hashes, raw/base CSVs, export commands and stderr. Verify that the actual sections include **Source Counters**; do not assume historical metric counts or available counters repeat. Keep distributed rank, NCU peer numbering and CUDA device identity distinct.

## PC extraction and diagnostic ranking

The proven project `extract_pc_samples.py` already reads each metric's correlation IDs and per-PC reason instances, conserves the aggregate sample count, and records `action.source_info(pc)`, `action.sass_by_pc(pc)`, embedded source text/hashes and function starts. The completed full-NCU [export receipt](../../profiles/current-best-056ce-0909e-full-ncu-analysis/export-receipt.json) pins the successful reader/API usage. The local copy changes only source-call tag selection for the relocated owned kernel, its FC2 readiness spin, BAR1, epilogue accumulator waits and relevant generic scheduler/dispatch calls. It adds no NCU API method. `export_ncu_action_sass.py` remains byte-exact and supplies contiguous SASS for checking outlined waits and their callers.

Run these CPU-only steps after the eight reports have finalized, keeping stdout/stderr and the command/SHA receipts with the outputs:

```bash
ANALYSIS=/workspace/flashinfer-w4a16-megamoe/profiles/direct-epi-0910a-ncu-full-analysis
mkdir -p "$ANALYSIS"
/usr/bin/python3 -B candidates/w4a16_direct_epi_profiles/extract_pc_samples.py \
  "$OUT"/ep_w4a16_megamoe_t1024.rank{0..7}.ncu-rep \
  --output "$ANALYSIS/pc-samples.json"
for rank in {0..7}; do
  /usr/bin/python3 -B export_ncu_action_sass.py \
    "$OUT/ep_w4a16_megamoe_t1024.rank${rank}.ncu-rep" \
    --extent 0x20000 --output "$ANALYSIS/rank${rank}-sass"
done
/usr/bin/python3 -B candidates/w4a16_direct_epi_profiles/rank_wait_pcs.py \
  --samples "$ANALYSIS/pc-samples.json" \
  --source-manifest "$OUT/source-manifest.json" --output "$ANALYSIS/ranking"
```

The small final step performs arithmetic on saved JSON only. It ranks source-call groups **within each rank**, retains each exact PC/SASS/source/reason instance, shows a separate native `SYNCS.PHASECHK` / `NANOSLEEP` / `BAR.*` subset, and lists unassigned native wait instructions separately. It also keeps the all-PC ranking, so polling loads or branch stalls are visible even when they are not wait opcodes. Download the complete analysis tree, not just its Markdown summary.

Source-call tags are candidates for interpretation. Optimized line tables can assign arithmetic to a nearby wait; outlined generic helpers may carry no owned caller line at all. For the leading tagged or unassigned PCs, review the captured SASS entry/branch target, barrier address or polled pointer, and return to associate them with the actual owned operation. Do not reuse old numeric PC offsets or force unresolved samples into the nearest source category. This final source/SASS review is required before calling a ranked category a specific owned wait. It is post-capture analysis and adds no timed invocation.

## Source/PC observations to inspect

Use the embedded source matching the selected manifest, then inspect actual native PCs for:

1. Owned FC2 activation readiness in `megamoe_kernel.py:1228–1234`: the `not work.peek_ready` slow path waits on the row's `fc1_done` counter with `fail_sleep_cycles=500`. The dependency is necessary. A poll-delay experiment is only worth considering if actual counters show this path matters.
2. Owned epilogue BAR1 and accumulator waits: distinguish FC1, terminal NEXT and direct FC2 nonterminal PCs using the captured source. The retained source determines whether nonterminal BAR1 exists.
3. Raw-load/decode readiness, decoded-TMEM producer acquire, MMA operand waits, dispatch readiness/pull and communication-tail waits. Map shared helper PCs as well as owned source; source placement alone is not native scheduling evidence.

Report sampling drops/overflow, unavailable counters and unattributed PCs. Sample shares are sampled warp states, not elapsed stall durations. The old T4096/N128/reuse full report is a separate control shape/mode; it does not measure direct-epilogue BAR1 or establish a before/after for this capture.

Local preparation used Python syntax parsing and one `bash -n` check; no runtime imports or report validators were executed. An independent source read confirmed the four benchmark launch/replay functions remain AST-equivalent to the completed056ce capture path, and direct-return mode introduces no different replay protocol.
