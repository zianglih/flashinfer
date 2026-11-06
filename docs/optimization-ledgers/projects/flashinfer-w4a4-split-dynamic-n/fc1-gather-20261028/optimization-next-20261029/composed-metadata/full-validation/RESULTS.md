# Full metadata composition results

**Retain.** The full fixed-winner screen confirms the focused metadata result. All model×topology aggregates are positive against both the original gathered source and retained7106.

Kernel`3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`; base`7106faf3082f63f3c94a4dc04b7fd0a77388f209` plus metadata-only patch`43f4d19ad016afcfca0b90bc7d0c759cdfad934c85bba4ba36c00140374a5b80`. Source remains unchanged after measurement.

- Fifteen exact checks passed:7focused repository cases +8M512 local checks, no failures/errors/skips.
-15jobs/468rawcells,30fresh candidate phases,93,600new strict-CUPTI samples. Reused93,600original same-GPU fb66control samples; no new control measurements.100samples/phase, coldL2,10warmups, fixed original winners/routes, noAUTO; NVFP4 includes inputquantizer, swapABunfused.
- Thirty runtime-guard receipts /854compilation observations passed; all430gathered FC1 observations have zero local bytes. Normal compilation options unchanged; nine persistent native-cache links retained.
-541artifact hashes verified; envelopeSHA256`f7029299663f5a896947a453f2cd095f28560d72880da906343101c3dc6c0e97`.
- GPU4/6/7 on C3 B300, CUDA13.2, image`nvcr.io/nvidia/pytorch:26.05-py3`. No sanitizer.

## Aggregate changes

308affected displayed cells exclude1–2tokens and unchanged W4A16 diagnostics. Percentages are geometric mean latency ratios. Both columns reuse earlier same-GPU samples and are not newly interleaved CAAC. The second column isolates metadata from the retained112+SFsource.

| Group | vsfb66 | vsretained7106 |
|---|---:|---:|
| All | +0.533% | +0.370% |
| Decode4–64 | +0.157% | +0.076% |
| Middle128–512 | +0.131% | +0.087% |
| Prefill4096–16384 | +1.570% | +1.145% |
| v3 EP | +0.365% | +0.269% |
| v41-flash EP | +0.319% | +0.173% |
| kimi-k3 EP | +0.619% | +0.246% |
| nemo3-ultra EP | +0.969% | +0.593% |
| v3 TP | +0.259% | +0.232% |
| v41-flash TP | +0.293% | +0.273% |
| kimi-k3 TP | +0.441% | +0.380% |
| nemo3-ultra TP | +0.882% | +0.717% |

## Interpretation

N3U EP W4A4 improves+12.00% at4K and+5.86% at16K againstfb66; incremental metadata gains are+8.80%/+1.25%. N3U TP W4A4 at16K gains+5.12% incrementally, with both pairs repeating within0.003%. K3 TP per-token at8K gains+3.80% incrementally.

The largest incremental negative is K3 EP per-token16K−4.47%, but candidate phase spread is8.34%. V41F EP MXFP4x8 at16K is−2.44% versus7106 (old0.43%/new1.25%spread), and−0.68% againstfb66. V41F EP MXFP8 and V3 EP MXFP4x8 at16K also have substantial phase drift. These limitations remain in the full CSV; no cells were selected out. The general instruction simplification and positive full-model aggregates justify retention under the accepted slight-prefill tradeoff.

## Evidence and next step

Full468-cell rawphase medians and differences:`report/cells.csv`(fb66),`report-vs-retained7106/cells.csv`(7106). AllrawCUPTIsamples and source/route/winner/UUID receipts:`evidence/perf/`. Exact checks:`evidence/validation/`. Baseline samples remain in`../../composed/full-validation/evidence/perf/`.

Native retuning is separate: evaluate every supported prefill arm using only the existing tactics at4096/8192/16384. Reuse this campaign’s final-source old-winner AA passes; no source change or new tactic axis.

Retained as `c0c0bc41c70100c694ac55585990971aba8b7fb9`: all measured source hashes match the clean canonical `flashinfer-fc1-gather-review`. The superseded composed review copy was removed after the cp.async experiment froze its independent source. Remote measurement/tuning source remains immutable.
