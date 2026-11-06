# Mixed FC1 epilogue overlap on regular TMA

Independent unstaged source: `flashinfer-mixed-epilogue-overlap-review`, parent
`0c1e00fc3e4f913c8c241796c70a29673737c542`.

This experiment removes the dtype-width gate from FC1's existing compile-time
`overlap_epilogue` policy. The geometry predicate remains unchanged. Mixed
MXFP4 x MXFP8 now uses the same dedicated epilogue organization as homogeneous
formats for those geometries. SMEM stages remain computed from layouts and the
device capacity; accumulator policy, CLC, cache hints, PDL and epilogue math stay
unchanged. No model or token-count condition is introduced.

The previous reason for inline mixed FC1 was a Gather4-era prefill diagnostic
(`scripts/two_cta_experiment/README.md`), not a measurement of the current
regular-TMA/CLC pipeline on V41. Retest this choice independently of channel
reuse so changes have clear attribution. Rejection remains a valid outcome.

Compare current retained source and candidate on the same replacement GPU7,
using the native AUTO benchmark and existing 13-token/10-warmup/100-sample
cold-L2 CUDA-graph CUPTI methodology. Run both V41-Flash EP4 and V3 EP8; exclude
tokens1/2 from retention. Broader numerical validation follows a convincing
performance result. Source receipt is in
`evidence/mixed-epilogue-overlap-r1/source.json`.
