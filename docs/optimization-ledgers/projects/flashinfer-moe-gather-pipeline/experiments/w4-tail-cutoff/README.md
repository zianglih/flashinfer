# W4 transform K-tail cutoff

Unstaged experiment on retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`. Exact/native qualification passed; the 39-cell CAAC and independent raw audit are complete. The separate two-cell ACCA diagnostics and independent raw peers also passed; all GPUs are released and the primary campaign remains unchanged. Initial CPU-ready documentation, whose hash is retained in `cpu-ready.json`, is preserved verbatim as `README.cpu-ready.md`.

The existing partial-group specialization recomputes `k_tile * mma_k + group_idx * group_k < consumed_k` in every K stage. Four retained 2b8 FC2 captures (K640, MMA K256; N16/64/192/256, one/two CTA, static/CLC) still emit `ULEA`, `USHF.L`, `UISETP` and the existing branch for this check. They have 128 registers and zero local memory. See the exact source-bound PTX/SASS paths, hashes and PCs in `source-proof.json`; this is retained codegen evidence, not candidate codegen.

The candidate computes a per-group stage cutoff once under the same constexpr partial-group condition:

```python
transform_k_tiles = k_tile_cnt - cutlass.Int32(
    transform_group_idx >= cute.ceil_div(tail_k, group_k)
)
```

The existing predicate location then compares `_k_tile < transform_k_tiles`. Both uses of `transform_valid` and all waits, copies, stores, releases, arrivals, state advances and trace scopes remain unchanged. Full-K and tails that touch every transform group keep the existing constexpr-elided predicate. Mega supplies its padded consumed-K extent, so this specialization stays elided there as well; native byte identity remains a qualification check.

For stage width S, group width H=S/G, consumed K=Q*S+R and 0<R<S, group g has Q complete stages plus a live final stage iff g<ceil(R/H). Therefore its cutoff is ceil(K/S)-Int32(g>=ceil(R/H)). The false path is still possible only in the last stage. No group-count constant, public/private argument, policy, loop split, clipped view or new branch was added.

`source_proof.py` evaluates the actual source expressions in 1,677,744 stage/group cases across G=1/2/3/4/8 and H=16/32/64/128/256. Reversing the setup relocation and predicate substitution restores the entire retained module AST. Python syntax, `git diff --check`, and scoped pre-commit hooks pass. The patch is 8 insertions / 6 deletions in the W4 kernel only.

The native gate must establish a net instruction benefit, not assume it: the cutoff setup can cost instructions or a longer-lived uniform register, especially with one K stage. Keep strict native resources, full-K/Mega identity, partial-K exact checks and actual compare placement explicit. No performance or retention claim is made from the retained instruction count.

Current native gate: `qualification-summary.json` binds26 pairs:14 fresh exact calls and6 reused retained controls from the identical release-library cohort. Resources are unchanged/LOCAL0. Four K640 FC2s remove ULEA+USHF per stage and3 non-NOP total; K320 FC2 removes2 total. Partial FC1s move one arithmetic operation into setup with unchanged total count. One-stage H128 changes only the comparison immediate and branch polarity. Full-K/all-live FC2 and Mega padded-K binaries remain byte-identical. Primary33 retention cells: +0.159% overall, +0.422% decode, +0.339% middle, −0.459% prefill; all8 negative retention rows and55 clock exceptions remain. See RESULTS.md. Recommendation is retention with the explicit adverse prefill tradeoff, pending parent integration; canonical source remains untouched.
