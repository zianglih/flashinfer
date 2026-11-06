# Small-N FC1: gather original linear SF while retaining regular B TMA

Isolated actual source copy `flashinfer-small-n-linear-sf-review`, base
`98fd3566b5f945c100f48cddacf25deb2432cbc2`; three unstaged files. No production
change, public API change, tactic addition, or arithmetic/stage change.

For FC1 routeN16/32/64, the existing cp.async SF producer reads original linear
SF directly. A valid route maps through `token_mapping[route_start+row]//top_k`
once per tile/row before the K loop. SF byte offset is source_token*(K/sf_vec)
plus channel/sf_vec. The four-byte copy retains row<valid/channel<K predicates;
legal K is a multiple of four SF groups. Its tensor extent is original
num_tokens*(K/sf_vec), not routed capacity. Original per-token scales are unchanged.

Payload preparation still copies valid rows with LDG/STG256, and B uses regular
TMA. Small-N prep skips all SF copying/padding and returns the original SF tensor
as an alias; diagnostic code must not poison/fill that alias. Invalid payload
remains untouched, matching retained98fd numerical masking (not an initcheck
claim). FC2 and routeN128/256 preserve canonical SF and the existing SFB TMA path.
All decisions are compile-static by phase and route geometry, not token/model
shape. Preparation workspace is still per invocation; no global tensor cache.

Prior closed SF vector/publication and canonical-tile experiments were checked:
none tested skipping canonical SF preparation while retaining prepared regular
B TMA. This is separate from the old payload Gather4 path.

## Bounded gate

`probe_exact.py` imports each actual source checkout in its own process and pins
all three files. Initial five NV cases: K64/384, per-token off/on, live17 routes
with reversed/repeated source mapping and poisoned invalid metadata, plus zero
active tiles. Full output/SF bytes are compared across processes; original SF
prefix/suffix and invalid output rows remain unchanged.

`probe_native_source.py` is byte-identical to the established actual-source
harness. `run_source_pairs.py` changes only98fd checkout identities, private cache,
defaultGPU3/T32/N16, and ABA/BAB orders. Whole native chain including preparation
is timed with10warmups/100cold-L2 CUDA-graph CUPTI samples. Inputs, routing,
weights, and final bytes must match every arm; all samples are retained. This is
a fixed-tactic diagnostic, not AUTO retention or a new primary baseline.

Source/codegen behavior outside the bounded gate remains unvalidated. Source
comment/docstring cleanup is intentionally deferred until a measured gain.
