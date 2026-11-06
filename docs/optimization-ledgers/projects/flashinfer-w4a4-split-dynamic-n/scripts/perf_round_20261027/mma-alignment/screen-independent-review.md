# MMA-N alignment: independent screen review

Source: clean control `2995bfda8338ca6ae623fbc2657d44e35e665627`; candidate patch `21ff3ce88e093f0900a564c87fcd009f928dc0dc55df0b4a7c0e8bf64fb60bc1`.

Verified all 267 collected hashes, 48 cells and 19,200 raw samples. Same-GPU C–A–A–C ordering, routing, input-quantization contracts and saved tactics match. Native AUTO is disabled for this bounded retention screen; no new GPU run was performed.

| Model / format | Decode | Prefill | Overall |
|---|---:|---:|---:|
| kimi-k3 / CuteDSL MXFP4x8 | 1.000336x | 1.000235x | 1.000285x |
| kimi-k3 / CuteDSL MXFP8 | 1.000103x | 1.004943x | 1.002520x |
| kimi-k3 / CuteDSL PER-TOKEN | 1.000761x | 0.998664x | 0.999712x |
| kimi-k3 / CuteDSL W4A4 | 0.999084x | 1.007448x | 1.003257x |
| v3 / CuteDSL MXFP4x8 | 1.000041x | 1.008492x | 1.004257x |
| v3 / CuteDSL MXFP8 | 0.999595x | 1.001620x | 1.000607x |
| v3 / CuteDSL PER-TOKEN | 1.000740x | 0.995991x | 0.998363x |
| v3 / CuteDSL W4A4 | 1.000321x | 1.000893x | 1.000607x |
| v41-flash / CuteDSL MXFP4x8 | 0.999969x | 1.007606x | 1.003781x |
| v41-flash / CuteDSL MXFP8 | 1.000407x | 1.004538x | 1.002471x |
| v41-flash / CuteDSL PER-TOKEN | 0.999204x | 1.000140x | 0.999672x |
| v41-flash / CuteDSL W4A4 | 0.999780x | 1.001838x | 1.000809x |

Overall 1.001360x; decode 1.000028x; prefill 1.002694x. The worst point is K3 per-token T4096: 0.990153x with controls 0.444402/0.445330 ms and candidate 0.449762/0.448819 ms. V3 per-token T16384 is 0.994212x; its two control measurements are also close. These small regressions are real observations, not discarded outliers.

The largest favorable rows also have some control/sample drift (for example V3 MXFP4x8 T16384 controls differ by 2.7%). Treat the end-to-end result as neutral, not a stable speedup claim.

**Recommendation: retain under the instruction-sanity criterion.** The hardware-derived eight-columns-per-CTA rule removes unnecessary padded one-CTA MMA columns without a new tuning axis or shape branch. The independent exact/codegen gate established 96 exact replays/source, unchanged instructions/control words/resources except descriptor constants and one harmless uniform-register allocation permutation, unchanged two-CTA encodings, and no spills. The bounded screen finds no material broad regression; the small per-token prefill losses fit the explicitly accepted tradeoff. Final public AUTO tables remain a separate refresh on the final committed source.

Gate proof: `../mma-alignment-source/independent-gate-review.json` and `../mma-alignment-source/independent-review.md`. Raw timing proof: `screen-independent-review.json`.
