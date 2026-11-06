# W4 transform K-tail cutoff

CPU-ready, unstaged experiment on retained `2b8eb9d8f72ceda3952fbb05054fee97173fc9c7`. No GPU compilation, numerical test, or timing has been run for this candidate.

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
