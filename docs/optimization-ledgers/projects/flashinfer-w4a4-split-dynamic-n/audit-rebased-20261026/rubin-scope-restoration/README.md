# Restore out-of-scope host plumbing

The requested `a_per_token_scale_ptr = make_ptr(...)` block was originally shared
host plumbing. With the Blackwell replacement, the two wrappers return through
`_run_blockscaled_gemm` before reaching that block. It is now on the Rubin-only
tail; Rubin still rejects per-token scaling in its compilation factory. Restoring
the block preserves the upstream structure without adding Rubin per-token support.

The two restored tails match upstream `215f83cb` ASTs exactly, including pointer
creation, compile-factory arguments, tile selection, conditional pointer omission,
and runtime stride arguments. The factory signatures/cache-selection forms also
match upstream. The old Blackwell constructors are **not** restored: attempting
to use these factories without Rubin tilers raises the existing error before
compilation. The new Blackwell early-return launcher remains unchanged.

All four convenience wrappers now use upstream public geometry defaults, matching
the primary public wrappers restored earlier. Their default documentation was
corrected too. Private Blackwell defaults remain unchanged.

## Source and evidence

- Measured source: `eb141478505103f4bc65d10fb655f3deb3cd71dc`.
- Final source identity and clean/dirty status: `proof.json` (updated by the
  verifier after the parent's amendment).
- Exact delta from measured source: `restoration.patch`.
- Frozen measured/upstream/final wrapper sources: `before-*.py`, `upstream-*.py`,
  and `final-*.py`.
- Scoped formatting/type/lint checks: `precommit.json` and `precommit.log`.

Revalidate from the project root:

```sh
python3 audit-rebased-20261026/rubin-scope-restoration/verify.py
```

The verifier checks:

1. The whole tracked diff from measured source contains only the two wrappers.
2. Every Blackwell-reachable statement through its unconditional return is
   AST-identical; the common launcher and all other module statements match after
   normalizing only the explicit restoration regions and documentation.
3. Seven kernel files and all 64 active device/JIT functions are unchanged.
4. All six public wrapper signatures/defaults exactly match upstream.
5. Both Rubin tails and factory interfaces exactly match upstream; no obsolete
   Blackwell constructor call exists in the restored factories.
6. 416 gather and 128 finalize factory cases match measured and upstream behavior,
   including constructor/compile arguments, cache keys, cache hits and errors.
7. The benchmark, fused-MoE and tuner sources are identical to measured source.
   All four ordinary/localized phase calls explicitly forward selected geometry.
   Every model/family uses the same public whole-MoE benchmark implementation;
   TRT and W4A16 do not call these blockscaled wrappers.

These are CPU/source-equivalence checks, not emitted-code or GPU checks. The
six running tables and focused runtime tests remain attributed to **eb141478**.
The final wrappers have different source hashes and may affect source-fingerprinted
compilation caches, even though the measured Blackwell execution path is unchanged.
No remote source or running measurement was modified.

The earlier `../kernel-final-receipt.json` remains a historical receipt for the
completed eb141478 audit; this directory records the subsequent restoration.
