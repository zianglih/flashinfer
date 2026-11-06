# Native MMA K-tail predication

Independent unstaged source: `flashinfer-mma-k-tail-review`, parent
`0c1e00fc3e4f913c8c241796c70a29673737c542`.

The existing TMA tile and capacity-derived stage count stay unchanged. For
nondivisible reduction sizes, compile time computes the native instruction K
extent from the fragment count. Only instructions whose full K interval lies
beyond the valid reduction are predicated off in the final tile. All other
instruction sites emit their previous unpredicated MMA form. No model name,
token threshold, special reduction dimension or alternate K-tile policy is used.

This differs from the rejected experiment that reduced FC2's K tile and changed
pipeline fitting. For example, K2304 with a512-element tile has a final256-value
tail. It can skip the remaining padded MMAs while preserving the same producer
schedule and load descriptors. K2048 with that tile has no new predicate.

Initial status: Python compile, Ruff lint/format and diff checks pass. GPU
correctness, generated-code inspection and native paired timing are pending.
The zero-padding accumulation numerical contract must be checked before
retention. Source receipt: `evidence/mma-k-tail-r1/source.json`.
