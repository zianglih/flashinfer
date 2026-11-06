# Automatic FC2 PDL prefetch ownership audit

Read-only CPU review of clean adf02fdd4a8fd2a5d4d2ca54b6969cd65572d93d. No source edits or GPU validation.

## Minimal policy

Remove the public FC2 `prefetch_weights_before_wait` parameter. Resolve it inside the FC2 launcher from `enable_pdl and not is_rubin and not use_fused_finalize and a_per_token_scale is None and mma_tiler_mn[0] == 128 and cluster_shape_mn == (1, 1)`. Existing validation already rejects localized Blackwell calls; FC2 already uses static scheduling. Keep the direct behavior knob in the private launcher/kernel/cache key. The existing narrow SFA-FIRST and B-LAST selection should consume this same resolved flag, preserving the retained chain policy.

Every Blackwell PDL FC1 should privately select `publish_routing_before_signal=True`, including standalone FC1 calls. The core already implements all-thread dependency wait, then only warp0 GPU release before the first startup signal. All CTAs, including two-CTA FC1 clusters and zero-live-work CTAs, execute this publication. Remove `_moe_core_impl`'s duplicated admission expression and paired public kwargs. Removing FC1's public publication argument too is a coherent cleanup; its private direct knob remains.

Relevant locations: FC2 public signature/docs/admission at `blockscaled_contiguous_grouped_gemm_finalize_fusion.py:586–760`, resolved cache policies/private call at880–943; FC1 public flag at467, Rubin rejection627 and private forwarding895; high-level duplicated selector642–651 and kwargs750/878. No benchmark policy exists after the retained public API refactor.

## Dependency proof

The common core initializes storage/TMEM and partitions immutable weight descriptors before the wait. Its prefetch branch (1209–1234) reads only live-count and first-expert metadata plus immutable A/SFA, priming `min(actual operand stages, ceil_div(K,tile_k))`. B/SFB remain after the unconditional all-thread wait1240. The ordinary producer skips precisely those already-acquired first-work stages; later persistent tiles and ring wraps use ordinary acquisition. Automatic policy changes do not require altering this code.

FC1 waits for prepare, which waits for routing ancestors. A GPU release before FC1's first PDL signal cumulatively publishes those completed routing writes; same memory synchronization domain is required. All FC1 CTAs must preserve the release-before-first-trigger ordering, not merely add a later release after another warp has signaled. Existing warp0-only publication does this.

No-work FC2 CTAs skip prefetch but still execute the unconditional wait; producer_exit then republishes routing before combine's early metadata reads. Zero-work does not bypass synchronization or TMEM teardown.

## Fallbacks and API boundary

- PDL off: resolved prefetch false; ordinary stream ordering remains.
- Per-token activation: `a_per_token_scale is not None` keeps prefetch false. The intervening NVFP4 per-token quantizer waits at1033 but does not GPU-release routing before its trigger(s)1058/1172/1247. `convert_sf_to_mma_layout` is view/permute only, so it is not a synchronization relay. No quantizer change is needed for this minimal cleanup.
- Fused finalize, two-CTA FC2, Rubin/localized: resolved false and current paths remain. Blackwell FC1 always publication changes only startup release/trigger ownership; no shape-specific branch is needed.
- Standalone built-in FC1→FC2: safe automatically once FC1 always publishes. Deprecated FC2 aliases call the generic API and inherit its policy without new arguments.
- Arbitrary custom preceding PDL producer: enable_pdl alone cannot prove that num_tiles/expert_idx is ready. Document that metadata and weights must already be ready for early launch, or the preceding same-domain producer must GPU-release completed metadata before its first PDL signal. Existing enable_pdl=False is the fallback. Pure host geometry inference cannot preserve arbitrary asynchronous metadata-producer behavior while also reading metadata before wait.

This ready-routing obligation matches the existing public combine, which reads mapping/scales before its wait (`blackwell/moe_finalize.py:130–141`) and relies on FC2's producer-exit release (core1492–1502). Do not imply that arbitrary producer metadata is automatically safe merely because PDL is enabled.

## Focused validation after implementation

Reuse existing changing-route/data exact gates for all three formats and N16/N128. Ensure direct public FC1→FC2 calls use no publication/prefetch kwargs; include all-local→zero-local replay, persistent SM2, two-CTA FC1→one-CTA FC2, and PDL off. Assert host admission false for per-token/fused/two-CTA FC2/Rubin. Generated code should preserve FC1 warp0 release before first trigger and FC2 A/SFA before wait with B/SFB afterward. Existing retained supported-chain constructor inputs should remain identical; newly automatic standalone and extra FC1-publication cases are the actual changed scope.
