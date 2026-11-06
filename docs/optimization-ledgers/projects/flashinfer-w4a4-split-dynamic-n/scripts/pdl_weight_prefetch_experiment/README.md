# First-weight-stage PDL experiment

The isolated `flashinfer-pdl-weight-prefetch-review` copy is based on clean retained `853aaf69d706b291afee477f738956b997033f53`. Its two-file unstaged patch and all 83 source hashes are frozen in `evidence/pdl-weight-prefetch-r1/source.json` (patch SHA256 `b4ac8987f5d221c579ea42f1a46b017a6591d59b23d854f4bdb35084e4126a44`). Production is untouched.

## Admission and publication proof

Two direct compile-time knobs default to false: `publish_routing_before_signal` and `prefetch_weights_before_wait`. The private host launcher caches both independently. Public FC1/FC2 call signatures and their default behavior remain unchanged. The task-local harness enables publication only for the known complete non-per-token split chain, then enables prefetch only for static one-CTA unfused FC2. The core rejects prefetch on FC1, fused finalize, effective CLC, and two-CTA configurations; publication requires a startup signal.

1. The complete chain is sort → input prepare → FC1 → FC2 → deterministic combine. FC1's existing all-thread dependency wait completes its prerequisite prepare, which itself waits for sort. The routing count and expert IDs are immutable for the rest of that invocation.
2. FC1 executes a GPU release fence after that wait and before its first startup trigger. All launches in this diagnostic use the same default memory synchronization domain; no custom domain or cross-stream producer is admitted.
3. CUDA 13.2's [PTX9.2 griddepcontrol contract](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#parallel-synchronization-and-communication-instructions-griddepcontrol) explicitly makes this release-before-trigger synchronize with dependent-grid start at GPU scope in the same domain. The release relation is cumulative, so routing writes already made visible by the ancestor waits precede FC2 startup reads. The generic high-level PDL trigger by itself would not supply this guarantee.
4. FC2 reads only the published live count/expert ID and immutable weight/SFA inputs before its dependency wait. The wait remains on every path and every relevant thread, including idle CTAs and zero live routes. Activation B/SFB and output-dependent work stay after it. Generated routing loads are ordinary `ld.global.b32`, not noncoherent texture loads.
5. With PDL disabled, ordinary stream launch dependencies complete the producer before FC2; the same guarded preload remains safe. Arbitrary standalone FC2 producers retain default-false prefetch. Per-token quantization's intervening nodes are deliberately outside this diagnostic admission contract.

The experiment uses the already existing `a_pipe`: first producer state is stage0/phase1; startup acquires its full transaction expectation once and issues A/SFA only. The first regular `(tile==block,k==0)` iteration skips another acquire/expect and completes B/SFB after wait. Subsequent stages and persistent work tiles are unchanged. Zero-work CTAs never acquire a stage. No extra queue, storage, or stage is added.

## Gate and generated code

`gate2.json` records 162 exact full-chain captured replays on B300 GPU0: NVFP4, MXFP8, mixed MXFP4×MXFP8; N16/N128; baseline, prefetch with PDL on, prefetch with PDL off; nine changes to routes, input bytes, and route weights per case. Patterns repeatedly shrink the expert set and then route everything outside the local EP shard. All outputs match exactly and all zero-local-route outputs are zero. K384 also exercises the existing K padding. First helper revision passed54 NV cases before a Torch FP8 `roll` limitation; the helper was changed to roll its byte view, with no source/kernel change.

`codegen-gate.json` plus `codegen-codegen.json` bind separately named PTX/SASS to six compiled FC1/FC2 knob combinations, avoiding dump filename collisions. Another27 exact graph replays passed. Independent generated-code review found:

- FC1 PTX139/141/143: wait → `fence.release.gpu` → trigger. SASS ACQBULK0x580 → MEMBAR.GPU0x5e0 → PREEXIT0x650.
- FC2 first expectation is45056 bytes (PTX163); weight3D TMA174/182 and SFA4D190 precede wait193. Activation B begins306/314 and SFB355+, after the wait. PTX248–249 skips duplicate first-stage expectation265. The no-work branch143–144 targets the wait label191.
- SASS agrees: early UTMALDG0x880/890/8a0 → ACQBULK0x8e0 → B at0xf40/0xf50.

These locations refer specifically to the N16 NV diagnostic artifacts. Generated code identifies NVVM13.3.27/PTX9.3; system nvcc is13.2.78, while the Torch container CUDA runtime is13.2. These are distinct compiler/runtime layers.

## Performance screen

The completed fixed screen uses full model V41 EP4, T32/128/512, all three formats, unchanged native10 warmup/100 cold-L2 CUDA-graph CUPTI medians and exact fresh-B300 routes. Both GEMMs use the original N16/M128 tactic. Same GPU0 order is C1 / Off1 / On1 / On2 / Off2 / C2. C is clean853, Off is candidate with publication true and prefetch false, On enables both. This separates shared-helper/publication overhead from early weight movement. Source hashes, routes and loaded tactics are asserted for every arm. No broad AUTO retention claim follows from this diagnostic.


The completed screen and all repeat ratios are in `evidence/pdl-weight-prefetch-r2-fixed/summary.{json,md}`. All9 affected points improved in both repeats (paired clean/prefetch1.001826–1.005403×). The public-wiring proposal is in `public-wiring-proposal.md`; production is unchanged and native AUTO retention remains pending.
