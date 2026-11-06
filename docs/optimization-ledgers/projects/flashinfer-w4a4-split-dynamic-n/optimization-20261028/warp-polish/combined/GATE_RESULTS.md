# Combined warp-pipeline qualification

The frozen candidate combines follower-MMA ownership cleanup, activation-SF
cache priority and compile-time PDL guards. It contains no descriptor prefetch
or epilogue pair-barrier change. The independent review clone is
`flashinfer-warp-polish-review`; its sole source change remains unstaged in
`moe_swap_ab_kernel.py` on base `99f4d0c277746fb706d10a4bb303c98c5f31e0a9`.

- Kernel SHA256: `b45b218b7bece21cf8c967bf88dc0dbfec32a5ebbb7472ac871e8e84ae8a2328`.
- Patch SHA256: `25fc36a44d2d77c964d9e05affac9a17f18f99a9dd199f9aca015cc73ae62f6b`.
- Remote frozen source: `optimization-20261028/warp-polish/polish-combined/source.json`.
- Remote source-receipt SHA256: `9df67d9f4b602c4d6d1f47dfda9e895c792a66cb2aeb305c9aaf34193a86f637`.

The full 11-configuration gate passed 176 source-paired exact final-output
storage-byte graph replays and 88 paired FC1/FC2 kernel captures. It covers
NVFP4, NVFP4 per-token, MXFP8 and MXFP4x8; SiLU/SiTU/ReLU2 representative
configurations; route tiles 16/32/64/128/256; channel tiles 128/256/512;
one/two CTA; static/CLC scheduling; and PDL off/on. Each configuration replays
balanced, skewed, empty and reactivated routing. These small diagnostic
shapes qualify the synchronization contract; they are not the model benchmark
or the exhaustive dtype/geometry cross-product. Private unused SF padding is
not compared.

The same helper's completed clean controls for configurations 0,2,8,9 were
reused. GPU2 collected the remaining disjoint configurations 1,3,4,5,6,7,10.
The merge checks source/head/helper identities, disjoint record keys and exact
full coverage before constructing the reference. GPU3 then ran all candidate
configurations and compared their input/output hashes. `merge-receipt.json`
records both original result hashes without altering either original. Total
controller elapsed time was 291.4 seconds. Both GPUs were verified idle and
released afterward. Persistent native compilation caches were retained.

Codegen and local evidence checks confirm:

- All 44 PDL-off candidate kernels contain zero GDC sites; their controls
  contain 88 sites in total. PDL-on source specialization remains AST-identical
  to the follower-plus-SF candidate for both prefetch settings and signal
  boundaries. Redundant nested `enable_pdl` checks are removed where an outer
  compile-time guard already dominates.
- All 404 activation-SF TMA instruction sites use the existing activation
  evict-last value `0x14F0000000000000`; the 404 control sites use normal 0.
  The payload cache policy is unchanged. The scale cache policy is not a new
  tactic axis or shape-dependent branch.
- All captures have zero stack/local memory and zero LDL/STL spill sites.
  Named-barrier sites, launch geometry, operand/accumulator stages, shared
  memory and TMEM allocation match their controls. There are 40 one-CTA and
  48 two-CTA captures.
- Register deltas range from -6 to +8; 53 of 88 are unchanged. Static non-NOP
  SASS sites sum to 84 fewer, with per-kernel deltas from -32 to +37. These
  static counts are not executed instruction counts or evidence that every
  specialization is smaller.

The follower ownership invariant remains simple: only CTA0 runs the MMA role.
For CLC's CTA-local metadata-empty barrier, leader arrivals are 224 threads
(weight, activation, MMA and four epilogue warps), while follower arrivals are
192 threads (weight, activation and four epilogue warps). The 32-thread local
CLC-response consumer quorum is unchanged. The existing full-CTA joins,
operand/accumulator rings, cluster initialization and peer TMEM-release
handshake remain necessary and are preserved.

Generated `outputs/candidate/config8-clc1-fc1-pdl1.ptx:121` directly initializes
the metadata barrier with the CTA-rank-dependent 224/192 count. At line 1866,
the dispatch excludes follower CTAs before MMA descriptor setup and the first
metadata wait. At line 2390, the shared MMA/scheduler exit still performs its
required dependency wait before the full 256-thread join. The follower skips
all per-tile/K bookkeeping and metadata wait/release operations, while its
required lifetime and dependency joins remain intact. The source proof covers
the same ownership for ordinary scheduling, which has no metadata ring.

The evidence archive is `gate-transfer.tar.gz`, SHA256
`5a50be43ab0a758be742342ff2d7844e40b75b9989e5437a5ca0a8b504da9a6f`.
All 729 listed file hashes were verified locally; the archive includes the
reused controls' PTX/SASS/cubins and raw outputs. `LOCAL_VERIFICATION.json`,
`codegen-summary.json`, `composition-proof.json` and
`pdl-compile-time-guard-proof.json` retain the machine-readable checks.

This gate establishes bounded exactness and generated-code sanity, not a
standalone performance improvement. The isolated follower screen was
aggregate neutral; the parent owns full combined performance retention.
No sanitizer ran, no canonical source changed, and no commit or push was made
by this subtask.
