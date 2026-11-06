# W4 transform cutoff — primary CAAC results

The 39-cell primary screen is complete and independently verified. Its 33 retention cells show **+0.159%** overall: decode +0.422%, middle +0.339%, prefill −0.459%. This is not a throughput retention claim. The two strongest adverse prefill observations are being checked in one separately reported, same-GPU ACCA block; no primary row is pooled or replaced.

- Source: actual immutable `2b8eb9d8` control versus only the cutoff patch `cbef9186`, still unstaged. No tactic, clock, compiler, phase/lifetime or arithmetic change.
- Coverage: V41F TP4, K3 TP8 and N3U TP8 × 13 tokens; all 39 rows retained, tokens 1/2 excluded only from the 33-cell retention aggregate. CAAC, 100 CUPTI samples/phase, 10 warmups, cold-L2 CUDA graphs, fixed recorded choices/routes.
- Raw replay: all 15,600 spans/156 phase medians; all 78 measured FC-stage configurations have unchanged driver resources, all 144 loaded functions LOCAL0. Five recorded defaults produce 40 actual stage/resource joins.
- Clocks: 55/624 quartiles have median SM clock !=2032MHz or a nonzero reason; zero unavailable quartiles. No clocks/samples/negative cells removed. Repeat spreads describe two phase medians, not statistical confidence.
- Native gate: 26 paired kernels. Four K640 FC2s remove ULEA+USHF per stage and 3 non-NOP total; K320 removes 2 total. Partial FC1 total instruction counts do not fall. One-stage compare polarity/immediate changes remain explicit; aligned/all-live/Mega paths stay raw-identical where qualified. Resources unchanged, no new occupancy claim from instruction counts.

[All 39 four-phase rows](../../evidence/w4-tail-cutoff-screen/1793393742504067000/report/table.md) · [33-cell matrix](../../evidence/w4-tail-cutoff-screen/1793393742504067000/report/matrix.md) · [component durations/extensions](../../evidence/w4-tail-cutoff-screen/1793393742504067000/report/component-deltas.csv) · [all clocks](../../evidence/w4-tail-cutoff-screen/1793393742504067000/report/clock-quartiles.json) · [independent raw peer](../../audits/w4-tail-cutoff-data-peer.md)

Every negative retention row is shown below. Δ values are candidate minus control arithmetic means of the two per-phase component medians. Durations overlap under PDL; extensions indicate the component’s contribution beyond the previous end, and their separately computed medians need not sum exactly to the E2E median.

| Model | Tokens | Speedup | C spread | A spread | Clock exceptions | Δ FC1 duration / extension µs | Δ FC2 duration / extension µs | Δ combine duration / extension µs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | 256 | -0.021% | 0.090% | 0.056% | 0/16 | +0.087 / +0.096 | +0.120 / +0.016 | -0.000 / +0.000 |
| kimi-k3 | 4096 | -0.927% | 1.340% | 2.483% | 3/16 | +3.439 / +3.456 | +1.664 / +2.399 | -0.624 / +0.424 |
| kimi-k3 | 8192 | -0.764% | 5.153% | 1.022% | 5/16 | +2.384 / +2.231 | +5.256 / +5.456 | +1.792 / +0.592 |
| kimi-k3 | 16384 | -0.226% | 1.567% | 1.234% | 16/16 | +2.607 / +2.598 | +3.215 / +3.911 | +0.848 / +0.472 |
| nemo3-ultra | 4096 | -0.181% | 0.041% | 0.364% | 0/16 | +0.576 / +0.504 | +0.744 / +0.312 | +0.288 / +0.129 |
| nemo3-ultra | 16384 | -0.891% | 1.430% | 0.219% | 12/16 | +9.159 / +9.159 | +5.519 / +4.655 | -1.656 / +0.367 |
| v41-flash | 4096 | -2.368% | 0.392% | 2.679% | 1/16 | +8.448 / +8.408 | +3.632 / +3.960 | +0.793 / +0.480 |
| v41-flash | 8192 | -0.372% | 3.363% | 0.878% | 3/16 | +0.697 / +0.705 | +2.632 / +2.680 | +3.088 / +0.112 |

V41F TP4K and N3U TP16K each have both candidate E2E medians above both controls. Their losses are not erased by repeat-spread or clock caveats; both FC1 and FC2 durations/extensions grow in the primary record. N3U TP4K (−0.181%) and K3 TP256 (−0.021%) remain small negative observations with normal clocks and tight repeats. The remaining prefill cells retain phase drift and clock changes explicitly.

The only authorized follow-up is [two-cell same-GPU ACCA](reverse-prefill/preparation.json): V41F TP4K on GPU2, N3U TP16K on GPU3, identical source/cache/routes/timing. No further repeats or matrix expansion are planned.
