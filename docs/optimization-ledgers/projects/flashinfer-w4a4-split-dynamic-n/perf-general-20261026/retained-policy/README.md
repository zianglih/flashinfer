# Composed policy candidate

Based on `0def601d6603df828ea39679b41ccbce64f7f09e`. Local source is `../../flashinfer-retained-policy-20261026`, with unstaged changes in four files. The canonical PR branch is unchanged while final retention runs execute.

Components:

- Share the operand buffer-release ring between TMA and cp.async scale producers, retaining separate ready barriers and the two-CTA scale join. The single UMMA owner releases/drains the stage. Source-paired coverage: 126 exact replays, 84 core variants, zero spills; redundant narrow UTCBAR commits disappear. Fixed CAAC screens are neutral for NV and improve MX by a few tenths of a percent. See `../../scripts/shared_empty_20261026/`.
- Quantize only the live routed prefix using the device count already produced by sorting. Read it after the PDL wait and preserve the scale layout's final atom padding. Bound the row grid by SM count and the existing compiled occupancy budget; each CTA loops over its assigned rows. The initial quantizer uses the same grid policy with its ordinary host-known row count. No model/dtype thresholds or host count synchronization. See `../../scripts/route_count_quantizer_20261026/` and `../../scripts/row_grid_quantizer_20261026/`.
- Preserve the existing cache-name introspection contract by making `has_valid_rows` explicit in the name helper. Generated cache names are identical to the screened candidate across 1,152 static cases. This metadata-only correction was made before full retention and does not alter device instructions.
- Documentation-only changes wrap the quantizer class docstring and state the shared empty-ring ownership contract.

Final retention uses the public benchmark's native AUTO search, PDL, 10 warmups and 100 cold-L2 CUPTI CUDA-graph samples. V3 EP8, V4.1-Flash EP4, Kimi K3 EP8; all 13 token counts, with 1/2 excluded from decisions. NV includes initial quantization. Both public families run in full, including matching TRTLLM controls. Fused CuTe finalize is disabled.

The first remote staging attempt (`retained-policy-r1`) was not benchmarked: the launcher raced an unfinished clone, and the cache-name audit then found the metadata contract issue above. Corrected source is deployed as `retained-policy-r2`. C++ artifacts are reused only after exact native source/header validation; changed CuTe modules have a private persistent Weka cache. No control AUTO cache is loaded for final retention.

Other candidates remain excluded: wider quantizer loads and early epilogue scalar loads had only small sub-percent screens; FC2 CLC is undergoing its own causal tests and is not part of this source. Rejected experiments and their raw evidence remain in the project ledger.
