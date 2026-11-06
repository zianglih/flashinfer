# W4 prefill attribution through c1ac8ce7

This extends the [earlier commit attribution](w4-prefill-regression-trace.md) through the currently retained PR9 head. Historical heat-map differences and fresh same-session commit effects have different denominators; they must not be added together or substituted for one another.

| Commit | W4 change | Fresh prefill evidence |
|---|---|---|
| [02de7785](https://github.com/zianglih/flashinfer/commit/02de7785c10847b3528340840bed40bd405d85b4) | Fold scale-byte selection into the existing byte permutation. | Fresh 24-cell EP/TP prefill isolation is +0.434% geometric mean. It does not reproduce the broad historical V3/N3U losses. K3 EP16K changes sign between the primary and separate reverse-order block, with clock variation; attribution remains unresolved. |
| [bf072d26](https://github.com/zianglih/flashinfer/commit/bf072d26b163e71458e7e4dfb12e615b19bd2c9a) | Skip unused final dequantization groups. | Six TP prefill observations lose 0.24–0.75%. Phase spread and clocks limit attribution, particularly against the larger historical red cells. N3U TP16K is the clearest small adverse direction. |
| [49c91adf](https://github.com/zianglih/flashinfer/commit/49c91adf47d30fc2049c76cbaf34d0ccf3291434) | Swap-AB output-store change only. | No W4 source change; all 104 W4 rows were reused unchanged. |
| [2b8eb9d8](https://github.com/zianglih/flashinfer/commit/2b8eb9d8f72ceda3952fbb05054fee97173fc9c7) | Packed W4 SiTU arithmetic. | All six own K3 prefill primary comparisons are positive. Their controls were already slower than the historical parent baseline. |
| [c1ac8ce7](https://github.com/zianglih/flashinfer/commit/c1ac8ce7341039db65195b99445fcdeb193cf226) | Compute the transform-tile cutoff once instead of rebuilding its coordinate each stage. | Primary TP prefill geometric mean −0.459%; seven of nine prefill rows negative. N3U TP16K loses 0.891% in CAAC and 0.966% in separate ACCA. V41F TP4K changes sign (−2.368% / +1.445%). Retained with the prefill tradeoff explicit for the tight +0.422% decode result and simpler per-stage work. |

The newest cutoff change therefore contributes an observed roughly 1% N3U TP16K adverse signal; it does not explain earlier EP deficits, which were not affected by that source change. Its other prefill losses remain visible with their repeat and clock limits. No claim of a general prefill improvement was made when retaining it.

Evidence: [cutoff primary and reverse-order results](../experiments/w4-tail-cutoff/RESULTS.md), [integration receipt](../experiments/w4-tail-cutoff/integration-receipt.json), [published current comparison](../publication-w4-tail-cutoff/report/table.md). The original raw CAAC/ACCA records remain separate and unchanged. No revert was requested or performed.
