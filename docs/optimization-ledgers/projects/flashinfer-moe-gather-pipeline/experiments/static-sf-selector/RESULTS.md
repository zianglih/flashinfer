# Compile-time MMA scale-byte selector

Base `82254e20`; candidate kernel SHA `8677cf213ca1dcb55ec9547116038ccf22e8b217f46435e28c4078c3ca8818c9`.

The independent arithmetic/layout review is in `../../audits/static-sf-peer.md`.
The 30-cell CAAC screen is effectively neutral: -0.055% overall, +0.166% decode,
+0.010% middle, -0.341% prefill. This is an instruction simplification candidate,
not an established throughput gain. K3 EP MXFP4x8 16K remains an unresolved
negative with substantial within-pass drift; its full samples are retained.

Fresh exact qualification totals ten calls (five control/candidate pairs),
30 loaded kernels. All pass with zero local memory. The additional two pairs
exercise K96 N256, including one CTA with full and partial token slabs and two
CTAs with partial K. Their FC1 non-NOP counts fall by 13/30 and FC2 by 18/19;
register counts and finalizer binaries are unchanged. The original MX FC2
capture increases registers from116 to118, still zero LOCAL and compatible
with the existing one-CTA target. No new register or stage policy is introduced.

Fresh correctness uses the ordinary scheduler after the test's bounded SM
budget resolves the requested CLC flag to false. Do not describe those calls
as fresh CLC coverage. The layout proof covers byte selection independently
of scheduler state. Historical broad checks remain supporting evidence only.

Artifacts: `fetched/evidence`, `fetched-wide/evidence`, `codegen-summary.json`,
`codegen-wide-summary.json`, and `wide-proof.json`. The first wide harness
attempt stopped before GPU execution because the remote nine-case helper
lacked the newly requested case index. The retry used a separately sealed
helper copy; no source/test implementation was changed to obtain a pass.
