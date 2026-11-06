# Native AUTO tactic audit for 13ca1475

All 39 measured sizes have an exact token bucket in their saved AUTO cache. All earlier profiles are preserved unchanged in each mode's final T16384 cache (`tactic-audit.json`). Thus none of these reported points reuses a tactic from a different nearest token bucket. The final cache has 22 profiles: the 13 reported sizes plus the intermediate hybrid buckets 768, 1024, 1280, 1536, 1792, 2048, 2560, 3072, and 3584. The measurement method and native tuning configuration are unchanged.

The actual tradeoff is that native AUTO profiles deterministic synthetic, balanced approximately maximum-load routing, while the primary benchmark measures its seeded actual routing. The profile remains cached as later token counts are added. A separately tuned or fixed native-input run can therefore choose differently even at the same token count; it cannot replace the full-sweep result or its timing.

- NVFP4 decode uses one-CTA M128 with N16/N32. T4 selects N32, whereas T8/T16 select N16. The T4/T8/T16 regressions are present with exact-size profiles, so they are not explained by nearest-bucket reuse.
- All modes select M256/N256 FC1 and FC2 at T4096.
- All modes select the new FC1 M512/N128 tactic at T8192/T16384. NVFP4 pairs it with FC2 M256/N128; MXFP8 and mixed pair it with FC2 M128/N128. The paired K8 and NB2 phase work is therefore represented in native AUTO selection. Replacing the measurements with phase minima would hide the remaining full-pipeline cost.
- Existing fixed-tactic d907 phase diagnostics establish that catalog pruning alone did not close the earlier gap. Those older measurements do not quantify the current 13ca checkpoint's exact minimum. The latest primary screen improves overall over 7829 by 1.042862x NVFP4, 1.053057x MXFP8, and 1.081501x mixed, while NVFP4 still trails the original B1.

## Sparse decode implications

The primary NVFP4 histograms have 7 active local experts at T4, 10 at T8, and 13 at T16. With FC1 channels4096/M128 and FC2 channels7168/M128, that is respectively 224/320/416 FC1 tiles and 392/560/728 FC2 tiles. The persistent grid is 148 CTAs, so these retention points already require roughly 2–3 FC1 waves and 3–5 FC2 waves. Skipping completely idle CTAs is not a substantive mechanism for these points. The excluded T1/T2 rows have 2/4 active experts and are more affected by idle startup.

The existing small-N dedicated-epilogue change was measured and retained earlier; simply reverting its nine-warp structure to five warps would replay a known loss. Before another role-layout change, separate per-tile startup/metadata/barrier overhead from cache pressure under the current K8 stages. The newly requested W4A16-style cache retest is the first current-checkpoint experiment on that axis. Keep actual native routing and whole-chain timing because hints can protect data across FC1/FC2 boundaries.

No new tuning buckets, profiling inputs, retention exclusions, or benchmark substitution is proposed. Detailed current cache and resource-policy evidence belongs in `scripts/cache13_experiment/`.
