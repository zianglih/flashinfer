# W4 raw-ready lookahead versus the new swap proposal

Read-only follow-up using the already source-bound N3U TP W4A16 profile at
`02de7785`. This is historical native evidence, not a new compile or timing run.

W4 already has a substantial instruction window between its raw-ready probe and
the next use of that predicate. In the captured FC1 image, the first raw probe at
`0x2a70` executes 147,264 times; the loop consumes P3 at `0x2aa0` 1,178,112 times.
The next raw probe is at `0x2d30`, before the remaining decode/store instructions;
the decoded-slot lookahead occurs later at `0x37d0`. The raw fallback probe at
`0x2ac0` executes only 1,179 times. The loop predicate consumer has 4,399 sampled
observations, but those observations cannot be identified as removable query
latency when a long useful instruction window already exists.

This differs from swap's immediate query/predicate-consumer pairs in the new
N3U MXFP4x8 decode capture. Replacing W4's existing TRY with TEST is not justified
by that swap signal. A faster false TEST could merely introduce more fallback
queries; it does not remove any required raw-data dependency. Keep W4 unchanged
while evaluating the separate swap lookahead candidate.

PTX TRY may wait before returning a result, while the native instruction can
still have independent instructions scheduled before its predicate is consumed.
Do not equate the PTX wording with unconditional native issue blocking. The new
swap policy deliberately uses TEST for guaranteed nonblocking progress with a
one-slot ring; that safety argument does not establish a performance win from
changing an already useful W4 lookahead.

Evidence: `profiling/n3u-tp-w4a16-16k/evidence/fc1-pc/source-sass.csv`, its loaded
ELF and `pc-proof.json`, `summary.json`, and `audits/w4-n3u-profile-peer.json`.
No source edit, extra tuning policy, or GPU experiment follows from this audit.
