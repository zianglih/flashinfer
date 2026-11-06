# PR #7290 cleanup archive, squash and upstream rebase

Completed on 2026-10-26. Both `../flashinfer` and
`../flashinfer-generality-review` are clean at
`24da0138fd67dc7172ef3dd9e6d1358e2b059a53`, whose only parent is upstream
`215f83cb27e39b6b973c0691b93fc378a53a10e4`. The PR has exactly one commit.

## Preserved history

1. Committed the audited cleanup as
   `6c3fdea87500227a66c7b8ed3cdcd2127c43293b` and pushed it to the PR branch.
2. Published and verified `zianglih/flashinfer` branch
   `archive/pr7290-pre-squash-20261026` at that cleanup commit. All 41 commits
   above original merge base `a65d5b09` remain reachable, including earlier
   removed benchmark scripts.
3. Published annotated tag `archive-pr7290-pre-squash-20261026`, also pointing
   at the cleanup commit. Its annotation includes the as-published PR body,
   title, draft state and diff metadata. The old body line-count table was
   explicitly marked as predating cleanup; it was preserved as historical text.
4. Squashed the code and rebased it, then pushed using an explicit lease against
   the cleanup head. No force update touched either archive ref.

Evidence: [archive-receipt.json](archive-receipt.json),
[archive PR snapshot](pr-archive.json), [final-source.json](final-source.json),
[publication.json](publication.json).

## Integration decisions

- Inherit upstream `quant_mode="mxfp8"` and unified MXFP8×MXFP8 wiring;
  remove the unmerged `w8a8` spelling from API/tuner/benchmark/test/trace paths.
- Keep upstream activation preparation, the shared row-major scale converter,
  and its weight-quantization closure. Preserve the replacement kernel's
  Blackwell up16/gate16 layout and Rubin up64/gate64 layout.
- Fully supersede the old Blackwell gather/FC2 implementation. The remaining
  FC1 module is a 78-line capability adapter into the new shared core. None of
  the legacy N192 implementation was restored.
- Preserve upstream Rubin deterministic-finalize forwarding/kernel and remove
  its old test skips. Blackwell and quantizer device sources are byte-identical
  to the archived cleanup; the Rubin kernel is byte-identical to upstream.
- Expose the replacement's existing MX SiTU/unfused support through upstream's
  unified runner. Update its capability table and existing support tests.
- Adapt upstream MXFP8 numerical tests to M256/M512 partial-channel tiles,
  retaining its ReLU2/2688 workload and existing numerical references.

Upstream advanced during the work; the final two additional commits changed
Frost Ampere/Hopper and SM12x GDN paths, with no overlap in this PR's changed
files. These were inherited without modification. Initial partial-object
fetch failures were resolved with a direct `git fetch --refetch --filter=blob:none`;
no source history was discarded to bypass them.

## Validation and limits

- Scoped pre-commit, syntax/conflict/diff checks pass for all changed sources.
- 32 real CPU Torch trace preprocessing cases pass with exact expected tensors;
  only the architecture query is stubbed.
- 12 existing host tactic invocations / 360 JSON roundtrips, 6 actual capability
  assertions, both unified MX SiTU/unfused acceptance checks, and both Rubin
  rejection checks pass using the bounded CPU harness.
- Canonical-mode/tuner execution passes; the unmerged name is rejected. Current
  host/tuner executable ASTs differ from the archive only by the requested mode
  spelling. Upstream API and unrelated preparer/runner code are preserved.
- The benchmark executable AST is unchanged after the canonical mode rename.
  Blackwell device code is byte-identical; no new numerical/performance claim
  is made for the rebase. GPU/JIT integration and the adapted upstream numerical
  tests were not rerun. Broader sanitizer testing remains deferred.

Receipts and code review: [wiring-static.json](wiring-static.json),
[kernel-integration-validation.json](kernel-integration-validation.json),
[tests-integration-checks.json](tests-integration-checks.json),
[trace-cpu.json](trace-cpu.json), [final-review.md](final-review.md).

## PR body

Updated component counts are **+5,825 / −8,227, net −2,402**, across 25 files.
All six raw benchmark blocks are byte-preserved and explicitly attributed to
measured source `74388819` in the archive. The body records the CPU/static
rebase validation separately. PR #7196 is still open/unmerged and remains the
stated merge-first dependency. The PR remains draft; no comment was posted.
