# W4A16 weight producer acquire

Base: retained `9037f6d46fcb45eac04be04c182104336c8b1e7c`.
One W4 kernel file, 14 deleted lines. The weight TMA producer keeps a normal
`producer_acquire(state)` instead of precomputing a try-acquire token immediately
before it. The first peek only precedes loop control; the following peeks only
precede the loop backedge and optional diagnostic markers. There is no useful
independent work in that interval. The direct acquire retains the same empty
stage dependency and expected transaction accounting.

All weight/scale copies, cache hints, barriers, producer commits, advances,
counter resets, scheduler metadata, PDL publication and terminal drain remain
unchanged. Dequantization peeks are untouched: those have different overlap
opportunities. No public API, tactic, stage-count or model/dtype policy changes.

The source remains unstaged in `flashinfer-w4a16-weight-acquire-review`.
`source.json`, `candidate.patch` and `local-source-manifest.json` bind the change.
The remote control is the immutable 514-file source used by the concurrent
`retained9037-full` refresh; its native data links and compilation caches are
reused without changing that source or its benchmark process.

Initial qualification is paired codegen only on GPU0 for native winners:
K3 EP8/4096, V3 TP8/8, N3U TP8/16384, V41F EP4/4096. The capture compiles both
FC1 and FC2, substitutes a no-op for the FC1 compiled callable, then exits after
FC2 compilation. Neither MoE kernel launches. Source, frozen cache, cache-hit,
loaded resource and no-local-memory guards apply. This is not numerical or
performance evidence; numerical validation and timing depend on the resulting
instruction comparison.
