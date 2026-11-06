# Full-table affected scope

Candidate `5e61d045...` changes only the private W4A16 scaled-tanh helper and its two calls under the existing SiTU compile-time branch. It adds no policy or tactic axis. Base is retained `49c91adf`.

The current 468-cell table contains 26 affected cells: K3 EP8 and TP8 W4A16, all 13 token counts. K3 uses gate beta4 and linear beta25. The other 442 cells are outside this source path: 364 swap backend cells have identical source, and the 78 W4A16 cells from V3/V41F/N3U select ordinary SwiGLU or ReLU squared rather than SiTU.

The proposed retention screen runs all 26 affected cells with unchanged recorded routes/tactics, strict native CUPTI, 100 samples, 10 warmups, cold L2 and same-GPU C-A-A-C. Tokens1/2 remain in raw output but outside retention aggregates. There are 24 explicit tactic records and two recorded deterministic defaults, both at16384; the unchanged native configuration observer must qualify default resolution in both arms. No retuning or fallback rewrite.

Source inverse-AST proof establishes that no other W4 kernel behavior changes. Representative non-SiTU FC1, every qualified FC2, and finalizer images are raw PTX/cubin/SASS-identical (14 native pairs); this supports eventual reuse of unaffected table cells, not a claim that every unaffected signature was recompiled. No table overlay or reuse has been published for this unretained candidate.
