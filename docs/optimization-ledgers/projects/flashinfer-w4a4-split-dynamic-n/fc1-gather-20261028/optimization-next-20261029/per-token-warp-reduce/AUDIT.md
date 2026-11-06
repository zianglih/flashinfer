# Independent one-warp quantizer evidence audit

The one-warp reduction bypass has a valid exact gate and a positive standalone-quantizer microbenchmark. Its broad E2E retention campaign was still running when this audit was fetched; no E2E conclusion is drawn here. No GPU work, source edits, clock changes, or GitHub writes were performed for this audit.

## Evidence and source boundary

- Hash-verified archive: `audit-evidence.tar.gz`, SHA256 `4ef4e7184d1f9c6d2025b0069e9c6d5a7353a9ae47e23dd3b1745ebf61400990`; 646 files. `audit-evidence/manifest.json` verifies every byte size and SHA256 before transfer and after extraction. The immutable candidate source/patch/HEAD guard passed. Both `broad` and running `broad-r1` were deliberately excluded.
- Measured quantizer SHA256 `9960490f0d26786ab3c4491b9591cd126db944ec3e19a39bc3480e31ae2ab8f7`; final formatted SHA256 `0d86930d3e74122009ba1f87c3c9c0068b989532a239050fc5817089238eafa3`. The fetched measured file and final local file were independently parsed: their ASTs are equal. The source gate had 514 guarded files; this is the one-warp bypass on the retained CTA-width policy, not the rejected narrower-wide-row policy.
- Micro control quantizer SHA256 `2bb9ed15d2ba33520c6c8b015e43fe2d9d8a01fa08541dc7384c9163842ad0dc` is the retained f63 source. Old gate-r3 used `311c7c021f975bf15cbeca5f5900a88c60192868f219ae4dc7d55eab91013362`; the subsequent edge cleanup changes only the K0 policy. `../per-token-width-475/full-evidence/edge-verification.json` proves equality for 40,960 positive-K policy inputs and a byte-identical K640 cubin. The compared gate cases all have positive K.

## Exact gates

- Existing gate: **80 passed, 0 failed/error/skipped**. The selected test IDs exactly match old gate-r3. These include precise/fast recipes, all SF layouts, FP16/BF16, wide rows, scale folding, and MoE SwiGLU/GeGLU/SiTU paths. See `audit-evidence/primary/gate/{receipt.json,junit.xml,selected.json,stdout.log}`.
- Direct-r1: **52 direct exact cases, 208 CUDA-graph replays, 4 routed-hole cases**. The reference is the same arithmetic with 128-thread reduction; candidate uses the retained policy, with forced 32 threads only at K8192/K16384 to exercise the two-pass path. Graph replays vary valid-row counts 0/1/129/4097 and verify live payload, row scales, and padded scale-factor zeroing. Routed rows preserve 64-logical/128-physical SF ownership. See `audit-evidence/primary/direct-r1/{receipt.json,progress.json}` and `direct_gate_r1.py`.
- The earlier failed helper attempt is retained in `audit-evidence/primary/direct.log` and `quant_guard_plugin.py`: accessing `compiled.library` failed because that compile wrapper exposed no runtime library handle. It failed before any exact result was asserted; direct-r1 replaces only the diagnostic recorder and succeeds. No failure is silently recategorized as a kernel result.

## Generated-code proof

Old gate-r3 captured 82 quantizer compiles and the new gate 85. Every fetched cubin was checked against its recorded SHA256. Pairing uses K, CTA width, blocks per thread, register-resident/two-pass mode, SF layout, recipe, fast-math setting, and the full function symbol (including input dtype).

- **36 uniquely matched multiwarp cubins are byte-identical**. The three additional new-only records are multiwarp configurations missing from the old capture; no binary-equivalence claim is made for those three.
- **All 46 single-warp candidate captures remove 2 BAR, 1 LDS, and 1 STS instructions.** Of these, 34 have unique old/new metadata matches. The other 12 form six same-symbol pairs from output-scale-fold variants; the recorder omitted that fold flag, so they remain grouped instead of inventing pair identities. Every member shows the same barrier/shared-memory removal.
- Unique single-warp instruction deltas range **−23 to +5 non-NOP instructions**, GPR deltas **−7 to +1**. Removing shared reduction is established, but not every precise recipe has fewer total instructions.
- **Qualification:** eight unique precise-error recipe pairs increase an existing stack by 8 B (six 24→32 B, two 8→16 B). They add 3–9 LDL and 2–3 STL static sites. Two K512 precise-MAE variants gain 5 total instructions. These recipes pass exact tests but have no dedicated timing in this micro campaign; do not claim universal spill-free or universal instruction-count improvement.
- All 14 directly captured default 32-thread configurations with the benchmark MSE/256/error-fast-math recipe (K16/80/256/384/512) have zero stack/LDL/STL. Direct-r1 also contains deliberate 128-thread controls at K8192/K16384 with existing local storage; those forced reference widths are not the default candidate policy.

Full per-pair resources, raw digests, instruction counts, unmatched cases, and folded groups: `audit-analysis.json`; extraction code: `audit_analyze.py`. The source-level synchronization proof remains in `../relay-scope/COMPANION_REVIEW.md`: one physical warp has no cross-warp reduction or shared-buffer reuse dependency after the shared reduction is omitted; multiwarp synchronization and PDL publication are unchanged.

## Standalone quantizer microbenchmark

Same B300 GPU, stock clocks, C-A-A-C; 10 warmups and 100 strict CUPTI samples per phase with cold-L2 CUDA graphs. FP16/BF16 correctness is gated; the measured micro input is BF16 with MSE/256/error-fast-math, main FP4 fast math disabled, PDL enabled. Width override is absent. All 40 phases (4,000 samples) have identical payload/SF/row-scale hashes across arms. Metric: `100*(sqrt(C1*C2/(A1*A2))-1)`.

| Rows | K | Threads | C1 µs | A1 µs | A2 µs | C2 µs | Change | C/A repeat spread |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 256 | 32 | 2.8160 | 2.6565 | 2.6560 | 2.8160 | +6.014% | 0.000/0.019% |
| 4097 | 256 | 32 | 5.5680 | 5.5670 | 5.5680 | 5.5680 | +0.009% | 0.000/0.018% |
| 4097 | 384 | 32 | 5.5680 | 5.5680 | 5.5680 | 5.5680 | +0.000% | 0.000/0.000% |
| 4097 | 512 | 32 | 5.6000 | 5.5680 | 5.5680 | 5.6000 | +0.575% | 0.000/0.000% |
| 4097 | 528 | 64 | 8.0485 | 8.0320 | 8.0320 | 8.0000 | -0.097% | 0.606/0.000% |
| 16384 | 256 | 32 | 13.5040 | 12.5120 | 12.5125 | 13.5360 | +8.054% | 0.237/0.004% |
| 131072 | 256 | 32 | 90.8320 | 85.0240 | 85.1045 | 90.7845 | +6.753% | 0.052/0.095% |
| 262144 | 384 | 32 | 184.2725 | 171.4405 | 171.5370 | 184.1930 | +7.431% | 0.043/0.056% |
| 262144 | 512 | 32 | 190.7210 | 179.7930 | 179.6490 | 190.7220 | +6.121% | 0.001/0.080% |
| 360448 | 640 | 64 | 395.3310 | 394.9945 | 395.1070 | 395.2030 | +0.055% | 0.032/0.028% |

Eight affected 32-thread cases: geometric mean **+4.317%**. Two unchanged 64-thread controls: **-0.021%**. This is a standalone micro result, not a full MoE speedup.

All NVML samples fully contained in the measured phase windows report SM 2032 MHz, memory 3996 MHz, event-reason mask 0. There are 16–306 samples per measured window. Sampling is discrete and does not prove absence of unsampled transients; no frequency normalization or fixed-clock values are used. The whole-run telemetry, including initial idle/startup samples, remains in the archive. All raw 100-value CUPTI arrays and output hashes are retained; `audit-micro.csv` provides the four phase medians and repeat spreads.

## Rejected wider-row width experiment (separate)

The register-width probe is preserved under `audit-evidence/rejected-register-width`; it is not the bypass candidate. Forcing 32 threads at K3072 spills 96 B (32 LDL/32 STL), K3584 spills 128 B (50 LDL/38 STL); forcing 64 threads at K7168 spills 128 B (48 LDL/36 STL). The same widths are not adopted by this candidate. Exact agreement among tested widths does not imply acceptable resource usage or performance.

## Remaining boundary

Wait for the completed broad-r1 E2E CAAC campaign before a performance retention claim. No sanitizer was run by this audit. Precise-error recipe timing is not covered by the MSE/error-fast-math microbenchmarks; the small stack/instruction regressions above must remain visible in the retention notes. No changes to the already published PR body or heatmaps were made.
