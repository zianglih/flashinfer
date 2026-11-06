# Frozen combined producer qualification

This diagnostic combines descriptor prefetch, activation-SF cache priority and
compile-time PDL guards on clean99f4d0c277746fb706d10a4bb303c98c5f31e0a9. It
does not establish performance retention for the combined changes. Individual
descriptor measurements did not demonstrate a benefit; the parent is deciding
retention separately. The source remains frozen and unstaged in
`flashinfer-producer-combined-review`.

GPU5 ran configurations0,2,8,9 against the scheduler agent's shared clean99f4
control. All64 source-paired storage-bit graph replays passed, covering NVFP4
and MXFP8, one/twoCTA, static/CLC, PDL off/on and balanced/skewed/empty/reactivated
routing. Both FC kernels were captured for32 matched specializations. This
bounded subset does not replace the full11-configuration gate across all four
formats; no sanitizer ran.

Codegen checks confirmed:

- Identical register/shared/stack/local resources for all32 pairs; no spills.
- Four descriptor-prefetch sites per candidate kernel.
- Zero GDC instructions in every PDL-off candidate kernel.
- All136 candidate SFB TMA instruction sites use evict-last
  `0x14F0000000000000`, versus normal0 at all136 control sites.
- Unchanged launch geometry, operand/accumulator stages and TMEM allocation.

The source SHA is
`f784ddc6b953ae7f6e2b6e686b2c6bc3bca9e65d9514e3b551614be6aa20fc87`.
The fetched archive SHA is
`ce4d536c74e50f7008d5c04cc09d2efd18c6df24c99b1ab87deef11d02162bb5`.
All275 file hashes in `evidence/evidence-manifest.json` were locally verified.
See `LOCAL_VERIFICATION.json`, `transfer-receipt.json`, the frozen source receipt,
and the raw candidate/control artifacts under `evidence/`.

Persistent native compilation caches were reused. GPU5 was idle after the gate
and released to the parent. No GPU job remains active from this subtask.
