# One-CTA CLC review and grid-bound correction

Reviewed the complete three-file CLC diff against `fca8462cbd9096059d0019a206aa760fb34ca8c4`, using `docs/code_review_guidance.md`. The measured source remains frozen in `flashinfer-clc-single-cta-review`; the host-only correction lives unstaged in the independent `flashinfer-clc-single-cta-grid-review` clone.

## Finding resolved before integration

The CLC launch maps allocated route tiles directly to grid Y. The installed CuTe scheduler defaults to `swizzle_size=1` and `raster_along_m=True`; its grid-shape helper returns the multidimensional problem shape unchanged. A read-only driver query on the actual B200 returned grid limits X=2147483647 and Y=Z=65535. Neither the previous host admission policy nor `can_implement` bounded route capacity.

For example, T=131072, top-k=8, 32 local experts, and route tile N16 allocate `(131072*8 + 15*32)//16 = 65566` route tiles. The new CLC grid would exceed grid Y even though the previous bounded persistent scheduler could represent the workload. This is a statically established invalid launch; no oversized allocation or kernel launch was needed to establish it.

The correction adds `_CUDA_GRID_Y_MAX = 65_535`, matching the existing naming precedent in `flashinfer/cute_dsl/attention/monolithic/mla_decode.py`, and falls back to the existing static scheduler when `routes // route_tile` exceeds it. It neither rejects the public shape nor introduces a model/token threshold. X would overflow only above approximately 275 billion output channels at the smallest supported M128 geometry; this is outside practical allocations, and no unrelated X policy was added.

Evidence: `guard-only.diff`, `guard-equivalence.json`, `host-audit.log`, and `../clc-single-cta-r1/{sdk-params-source.txt,device-grid-limits.txt}`. The host AST check admits exactly the new constant and predicate, then proves the remaining AST equal to measured source. All other 82 pinned source files are byte-identical. Resolved constructor arguments and in-memory compile-key components remain unchanged for measured inputs; this does not claim unchanged source-fingerprinted disk-cache identity.

## Synchronization and resource review

- Existing producer, epilogue, and MMA warp IDs are retained. The scheduler warp is appended only when CLC is enabled. The all-CTA TMEM retrieve/drain barriers include it; the producer-only TMEM free barrier remains 128 threads.
- Metadata producer participation is 32 lanes and consumers are every non-scheduler thread. The scheduler acquires the next metadata slot before requesting another cancellation. It consumes the CLC response with the full warp, copies metadata into consumers' registers before releasing the slot, and publishes a terminal sentinel which every consumer role consumes and releases.
- Padded route-capacity tiles do not read expert/limit arrays and do not enter the metadata queue. They continue cancellation until valid work or termination. Zero-live and padded cases are covered in the existing focused exact probe.
- Ordinary shared metadata loads precede `PipelineAsync.consumer_release`, which uses the ordinary release mbarrier operation; no additional async-proxy fence is required for those generic loads. The producer fence and 32-lane publication barrier remain. Named barriers 1/2/3/5/6 serve distinct participant groups.
- Additional metadata/response/barrier storage is included before automatic SMEM stage fitting. The prior actual-layout audit covered 360 policies at depths 1/2: no input-stage or bulk-TMA policy changes; maximum actual storage 230400 bytes versus queried SM100 capacity 232448 bytes. The retained caller uses depth 1.
- Existing wide-geometry resource comparisons show no local spills or occupancy loss and preserve one CTA per SM. Those detailed resource captures concern M256/M512 geometries; narrow M128 execution is covered by exact/performance probes, without a separate retained M128 register-count claim.
- The explicit `sm_count` reservation policy is preserved: requesting fewer than the hardware SM count selects the bounded static launch. The new grid guard composes with that policy.

No additional synchronization, tile-index, sentinel, or layout correctness blocker was identified. This is a focused source review supported by existing probes, not exhaustive sanitizer or dtype/architecture coverage.

## Static-path behavior and maintainability

The approximately 246 added lines mostly implement necessary scheduler ownership, metadata storage/pipeline, the CLC response pipeline, and terminal handling. The knobs `use_clc_scheduler` and `num_tile_info_stages` describe direct compile-time behavior. The FC1 caller requests CLC only for one-CTA geometry; FC2 explicitly disables it. No phase policy is inferred from the activation function.

The shared compute loops changed from `for` to `while` plus `next_work` even when CLC is disabled. This is a real static FC2 code-generation change: all 12 recorded FC2 resource pairs changed generated code, with registers ranging from -6 to +4, no spills, and unchanged stages/SMEM/occupancy. Therefore static two-CTA performance changes must not be attributed solely to CLC load balancing. Prior fixed controls did not establish a consistent regression; full-chain retention incorporates the final static code as well.

Safe future comment-only improvement: explain the acquire-before-cancel ordering beside the scheduler loop, because it limits work hoarding. The fourth word of each metadata record is padding for a 16-byte slot; documenting that is clearer than shrinking it. Neither cosmetic change was applied to the measured kernel.

Other apparent simplifications are not free: extracting scheduler helpers can affect DSL inlining/register allocation, restoring the old static `for` loop would duplicate or reorganize the three compute-role bodies, and deleting compile-time two-CTA support narrows a validated private capability for little runtime benefit. These should not be included as unmeasured cleanup. The retained depth-1 choice has direct evidence: fixed V3 T16 depth-2 trials regressed NVFP4/MXFP8/mixed latency by approximately 3.13%/3.19%/9.27%.

The one-CTA paired campaign supports retention of modest decode improvements without a stable prefill regression, as recorded in the parent's independent paired summary. The scheduler complexity is justified by measured improvements and shared structure with the existing W4A16 design, rather than by line count or a claimed universal scheduling win.

## Source and validation handoff

- Base: `fca8462cbd9096059d0019a206aa760fb34ca8c4`.
- Measured one-CTA patch: `6b3f1c4f532addca0a44a59c6b0b64207bff7a8c88819834f101e891773a1775`.
- Guarded patch: `a5e9283a7021e563c991d125a140379bb7049135705fcc0e7608c727f832fd86`.
- Common kernel SHA256: `bc36c575f8ae044818d5365198c0b016828dc630886b874caffd4edb11737882`.
- FC1 host SHA256: `1cd92c6c6460532ddd43697d0e745c89781951f8b43504a1ad0ff6ebbd5fdcdc`.
- Guarded shared host SHA256: `47024e3042a824528c86e981c96197da542b3b497698901c5533028c39015e4b`.
- Scoped precommit: all applicable hooks passed (`precommit.log`).
- Host policy: all 156 observed A1/A2 model/dtype/token dispatches unchanged, capacities 6–1055. All 338 model/token/tactic combinations unchanged, maximum capacity 8222. Boundary 65535 stays CLC; 65536 falls back to static. Explicit SM reservation remains honored.
- No additional GPU kernel or benchmark was launched for this host-only correction. The parent will run the final focused suite and final CLI tables on the committed source.

Remaining boundaries: rigorous sanitizer testing and broad dtype/per-token activation coverage remain deferred as requested; Rubin uses a separate implementation. Large-grid fallback is established by host-policy/SDK proof, not a giant end-to-end allocation. Paired prefill noise and static-path codegen changes limit attribution of small prefill differences.
