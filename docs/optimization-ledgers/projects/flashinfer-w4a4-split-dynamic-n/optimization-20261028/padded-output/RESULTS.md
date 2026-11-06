# Padded routed output: final unstaged review

The active source is `flashinfer-padded-output-review/`, based on retained `61249e0bbd40dd2c6e583e4e48ff95e055a3c7f8`. Five tracked files remain unstaged; nothing was committed or pushed. The canonical `flashinfer/` checkout and PR body are unchanged.

Final kernel SHA: `ec675177a1cc759c027471c0926aacc8908e28eea656857afcca297945b6dcb8`.

## Implementation

- FC2 writes BF16 output in padded routed order, and combine consumes the existing `expanded_idx_to_permuted_idx`, matching W4A16's storage contract. Blockscaled activations need a separate BF16 output allocation; W4A16 can reuse its BF16 prepared-input allocation.
- Removed `_CompactOutputWorkspace`, `_get_output_workspace`, `_output_workspace`, compact offsets, `dense_indices_ptr`, the prepare prefix scan and FC2 inverse-map writes.
- Bulk FC2 stores use ordinary 2D TMA for every nonempty slab. Partial slabs write only into the route's owned padding; combine never observes those padded rows. No duplicate SIMT-tail epilogue or new shape/tactic switch.
- Narrow SIMT and fused-finalize behavior remain supported. Existing pipeline ownership and release points are preserved. W4A16 tactics and execution behavior are unchanged.
- Diff: **95 insertions / 267 deletions**, net **172 lines removed**, across five files. No repository test or benchmark files were added.

## Validation

- Final source: **208 paired bit-exact output checks**, **104 GEMM codegen pairs**, and **8 existing pytest tests** passed. Coverage includes all four scaled formats, static/CLC scheduling, PDL on/off, one/two CTA, changing routes, poisoned FC2 storage, N16/N64 SIMT, 64-row/two-stage TMA and forced 32-row/one-stage TMA.
- Scoped pre-commit and `git diff --check` pass. Source/protocol review is recorded in [r2/SOURCE-REVIEW.md](r2/SOURCE-REVIEW.md).
- All 52 FC1 SASS streams are unchanged. All 52 FC2 variants have fewer static non-NOP sites; no local-memory or stack spills. Normalized FC2 reductions are 6–623 static sites versus retained head. [Independent three-source gate and codegen audit](r2/independent-gate-review.json). Static instruction counts are not a dynamic performance claim.
- No sanitizer run. Padding values are intentionally unspecified; only routed valid rows are observable.

## Performance versus retained head

Geometric speedup = retained-head latency / final-candidate latency − 1. Positive is faster. Decode uses tokens 4/64; prefill uses 4096/16384. W4A16 sanity rows are excluded from these aggregates.

| Topology | Model | Decode | Prefill |
|---|---|---:|---:|
| EP | All scaled formats | -0.53% | +0.06% |
| EP8 | V3 | -0.14% | +1.37% |
| EP4 | V41F | -0.45% | -1.14% |
| EP8 | K3 | -0.89% | -1.11% |
| EP8 | N3U | -0.73% | +0.84% |
| TP | All scaled formats | -2.70% | +3.51% |
| TP8 | V3 | -1.07% | +5.20% |
| TP4 | V41F | -1.29% | +0.31% |
| TP8 | K3 | -2.45% | +3.35% |
| TP8 | N3U | -5.15% | +3.57% |

**Performance is mixed:** EP prefill is approximately neutral, TP prefill improves, and short decode has a measurable cost. The worst cell is N3U TP8, four tokens, MXFP4x8: **36.34 → 40.26 us (−9.76% speedup)**. The best is N3U TP8, 16,384 tokens, W4A4: **1300.14 → 1188.83 us (+9.36%)**. V41F EP4 / 4096 / MXFP4x8 is the worst prefill cell at −2.23%.

[EP heatmap](r2/plots/padded-output-vs-retained-ep.png) · [TP heatmap](r2/plots/padded-output-vs-retained-tp.png)

[All 144 cells with four absolute latency medians, signed speedups, spread and memory](r2/report/cells.csv) · [Machine-readable summary](r2/report/summary.json)

The bounded N3U MXFP4x8 diagnostic isolates the decode cost to combine's routed reads. For TP8 / four tokens, isolated FC2 improves 16.881 → 16.400 us while combine changes 4.384 → 13.408 us. Separate PDL-on end-to-end timing is 36.417 → 40.385 us. Component measurements disable PDL and cannot be summed to explain the overlapped chain. EP8 has a smaller combine increase. [Attribution, limitations and raw evidence](PERFORMANCE-NOTES.md).

## Method and memory

- Existing two c3 B300 boxes, 15 GPUs used; CUDA 13.2 / `nvcr.io/nvidia/pytorch:26.05-py3`, CuTe DSL 4.8. Persistent native compilation caches preserved.
- Public `benchmarks/bench_moe_deepseek.py` with frozen saved winners/routes, unfused swap-AB, strict CUPTI cold-L2 CUDA-graph timing, 10 warmups and 100 samples/pass. NVFP4 includes input activation quantization. No autotuning and no new TRTLLM/non-swap baseline measurements.
- Final R2: two fresh candidate passes, **288 medians / 28,800 samples**. Reuse the two retained-head control passes from R1, on the same actual GPU UUID for each job. These are **reused controls plus fresh AA**, not a new interleaved CAAC campaign.
- **112 changed-format cells plus 32 unchanged W4A16 sanity cells** across four models and EP/TP. K3 MXFP8 and V41F TP MX remain excluded according to the existing comparator-eligibility matrix. This is a representative screen, not the full token table.
- Fresh candidate passes began 18.09–19.94 minutes after each job's saved closing control; baseline reuse therefore introduces time separation. Unchanged W4A16 geometric shifts: EP decode +0.00%, EP prefill −0.83%, TP decode −0.08%, TP prefill −0.23%. Small prefill differences should not be treated as stable gains or normalized away using these sanity rows.
- BF16 output allocation is `2 * padded_route_capacity * hidden_size` bytes. Measured extra BF16 scratch ranges from **3.52 MiB to 955 MiB**. At the worst decode cell it grows **0.34375 → 5.5 MiB**; metadata savings are not subtracted from this BF16-only figure. Exact per-cell sizes are in the CSV.
- All GPU work is complete and both boxes are idle. [Source-bound execution receipt](r2/validation/execution-receipt.json), [gate evidence](r2/validation/gate-evidence/evidence), [raw candidate timings](r2/validation/perf-evidence/evidence), [saved controls](r1/perf-evidence/evidence).

Reproduce the report from the project root:

```sh
python3 optimization-20261028/padded-output/analyze_perf.py \
  optimization-20261028/padded-output/r2/validation/perf-evidence/evidence \
  --baseline optimization-20261028/padded-output/r1/perf-evidence/evidence \
  --output optimization-20261028/padded-output/r2/report
```

Independent audit: [final timing/source/device verification](r2/independent-perf-review/independent-review.json) checks all 1,052 fresh and 2,037 reused archive files.

Initial R1 results and the reason for replacing its bulk SIMT tail are preserved in [r1/RESULTS.md](r1/RESULTS.md).
