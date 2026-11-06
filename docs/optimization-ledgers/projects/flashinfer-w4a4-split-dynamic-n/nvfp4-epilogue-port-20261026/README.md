# Standalone NVFP4 epilogue arithmetic port

Separate pushed commit: `0def601d6603df828ea39679b41ccbce64f7f09e`, parent
`65c2c5c4635257d920ddb7524096f2e67bfcc9e3`.

The 11-line production change in
`flashinfer/fused_moe/cute_dsl/blackwell/utils.py` exactly matches
[PR #7372 commit 5ead7268](https://github.com/flashinfer-ai/flashinfer/pull/7372/changes/5ead7268e7e3756abcc3c4ca129da42c818de3c2).
It reuses `_nvfp4_standard_quant_from_amax` for standard SF16/E4M3 NVFP4 output,
retaining FP32 activation values through FP4 conversion. Existing helper
dependencies already match the donor. No reference or test files were added.
The public per-token pipeline still uses its standalone quantizer; MXFP8,
MXFP4x8 and Rubin device code are unchanged by this port.

`provenance.json` and `source-production.patch` pin donor and destination source.
Scoped pre-commit and `git diff --check` pass. Canonical and current review
checkouts were advanced to the same clean head after pushing.

Validation uses eight existing tolerance-based tests on a dedicated c3 B300
devbox, `fi-moe-nvfp4-port-1026` in namespace `infra`, image
`nvcr.io/nvidia/pytorch:26.05-py3`. `remote_validate.py` records the tested source,
dependencies and complete command. `collect_validation.py` is read-only remotely
and accepts completion only with eight executed tests, zero skips/failures/errors,
a successful process exit, and unchanged clean source. Validation completed: **8 passed, 0 skipped, 0 failures, 0 errors**. The source stayed clean at `0def601d`, and its epilogue SHA matched before/after. Raw log, JUnit XML, launch/result JSON and verified file hashes are saved in this directory.

Existing six benchmark tables were measured at `eb141478`; they are preserved
without relabeling them as measurements of this arithmetic follow-up. The
published PR body is `pr-body-draft.md`; `pr-published.json` and
`publication.json` verify its exact readback at the two-commit head.
