# Packed FC2 timing: independent review

Recommendation: retain as a small instruction-efficiency cleanup under the requested tolerance for slight prefill losses. This screen does not establish an end-to-end speedup. The candidate removes 64–256 non-NOP instructions per tested FC2 specialization, halves the targeted multiply issue count, preserves its scale shuffles, and adds four net source lines. It adds no policy, layout, tactic or synchronization branch.

All 86 collected hashes pass. The eight cells contain 3,200 raw samples, with 100 cold-L2 CUDAgraph CUPTI samples and ten warmups per leg. C-A-A-C source order, exact frozen sources, separate CuTe DSL caches, native winners, expanded routing identities, model/quantization contracts, preparation cache keys, actual FC1/FC2 dispatches and PDL flags match. All 160 cache accesses hit; no AUTO search or new admissions occurred. NVFP4 input quantization is included and finalize is unfused. The control production source is byte-identical to d02; the candidate changes only the paired bulk scale loop.

|Model|Tokens|C0 µs|A1 µs|A2 µs|C3 µs|Speedup|Control drift|Candidate drift|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|v3|128|143.073|142.913|142.944|142.913|+0.045%|-0.112%|+0.022%|
|v3|16384|674.772|675.299|676.948|674.084|-0.251%|-0.102%|+0.244%|
|v41-flash|128|271.778|271.858|271.810|271.906|+0.003%|+0.047%|-0.018%|
|v41-flash|16384|799.589|803.141|806.405|798.884|-0.688%|-0.088%|+0.406%|
|kimi-k3|128|306.082|306.194|306.210|306.178|-0.023%|+0.031%|+0.005%|
|kimi-k3|16384|1101.926|1079.399|1099.015|1089.206|+0.586%|-1.154%|+1.817%|
|nemo3-ultra|128|145.489|145.184|145.184|145.473|+0.204%|-0.011%|+0.000%|
|nemo3-ultra|16384|917.765|915.013|915.269|918.053|+0.302%|+0.031%|+0.028%|

Geomean overall 1.00021689× (+0.022%); decode 1.00057082×; prefill 0.99986310×. Positive means candidate faster. Ratios use geometric means of the two per-source medians; they do not pool raw samples across legs.

All four decode winners use route N16/N32. The source requires route N≥128 to select the changed bulk path, so these are unaffected controls; Nemo decode +0.204% is not an attributable gain. At prefill, both V3 candidate legs are slower than both control legs (−0.251% combined), and both V41 candidate legs are slower (−0.688%). Treat those small losses as observed, not dismissed as noise. Both Nemo candidate legs are faster than both controls (+0.302%). K3 +0.586% is not stable: the control and candidate repeats drift by −1.154% and +1.817%, and the late paired comparison reverses sign.

Clock snapshots show 3996 MHz memory throughout and 2032 MHz SM at all leg ends. Several opening controls begin with idle SM clocks (120–652 MHz); other endpoints are at 2032 MHz. Temperatures stay36–39°C, with similar ending power near244–246 W. These are process-boundary snapshots, not in-window clocks; they do not explain or invalidate the measured differences.

The recommendation relies on the verified instruction reduction and small, maintainable source delta, not the nominal +0.022% aggregate. The stable V41 prefill loss is the explicit tradeoff. This differs from the rejected amax tree, whose compiler baseline already emitted the same eight instructions and whose larger source did not improve decode. No further GPU runs were performed or requested by this review. See `independent-review.json` for the exact-output/mapping/codegen proof and `timing-summary.json` / `timing-raw-samples.csv` for the complete recomputation.
