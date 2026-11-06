# Candidate 006: ordinary epilogue unroll native review

**PASS for the existing focused runtime validation.** The hint changes both
ordinary kernels, preserves the single final accumulator release and conditional
C-buffer protocol, and leaves the fused control byte-identical. This is native
admission, not a numerical or latency result. No GPU operation, source edit, or
new capture was performed for this review.

## Exact scope and controls

The captured candidate is retained 005 plus
`unroll_full=not self.use_fused_finalize` on the existing subtile loop. Its kernel
SHA256 is `6db190f34bdd7a784b7e208ece965c07f9e749c28bfba1f8c8607ce601e972ad`;
the wrapper is
`aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`.
The immediate 005 control kernel is
`1fe29f6f802508034c2fc5daaf7a24271e35bf98a0ca1b052548bfc955f5f97b`.
The held b90-based proposal has different bytes and is not the captured source.
Use each result's `source_sha256`, not its historical `git_head`, for attribution.

All captures are compile-only, logical M256/N256/K512, eight groups, static
scheduler and PDL disabled. The N64 tactic is MMA128/N64/K256, C1; the N128
tactic is MMA256/N128/K256, C2. Ordinary uses top-k 0/num_tokens 0; fused uses
top-k 2/num_tokens 65. No returned callable was invoked. The extended capture
helper records the MMA and cluster settings; no compiler register override was
introduced.

| Arm | Directory under `native/` | Result SHA256 | SASS instructions |
|---|---|---|---:|
| 005 ordinary N64 | `candidate005-tma-prefix-ordinary0-m256-tile-n64` | `d13f84860aad8052d0004bfd549836773d8251b64d267a4a3270148ea5458c1a` | 1624 |
| 006 ordinary N64 | `candidate006-unroll-ordinary0-m256-tile-n64` | `835cc2833470379fc85e8a2705d40a873e02725da995a001ddce1cc8ad340e46` | 1824 |
| 005 ordinary N128/C2 | `baseline006-ordinary0-m256-tile-n128-mma256-c2` | `1a18261a4b609796154090162054510049f93eed7c0c56b8fee990c3bb703435` | 1736 |
| 006 ordinary N128/C2 | `candidate006-unroll-ordinary0-m256-tile-n128-mma256-c2` | `f99f370da8034400066e73bbfa8b6026e6c2520f08fcc5b18ce371e9ce3a714c` | 2360 |
| 005 fused N64 | `candidate005-tma-prefix-fused2-m256-tile-n64` | `2cc21d7cf8a842dd415cadad1d9b596c54c5e1fb462e67ac2b54ba800a92eadd` | 1568 |
| 006 fused N64 | `candidate006-unroll-fused2-m256-tile-n64` | `0d0b277ccf6a8068d3218f6a7fe89127979f5efdb3b38b49fc679a832ea29e2e` | 1568 |

## Real expansion and final accumulator release

The ordinary epilogue has two straight sequential bodies for N64 and four for
N128; the former inner-loop backedge is absent. Native route thresholds are
32/64 and 32/64/96/128, respectively. Each body retains its TMA/SIMT choice.

PTX line references below are to the sole `.ptx` in each candidate's `dsl/`:

| Fact | N64 | N128/C2 |
|---|---|---|
| TMEM load pairs | 2632/2642, 3047/3057 | 2748/2758, 3163/3173, 3581/3591, 3999/4009 |
| Prefix predicates | 2652, 3080 | 2768, 3183, 3601, 4034 |
| Final `tcgen05.wait::ld.sync.aligned` | 3067 | 4019 |
| Final elected ACC arrival | 3075, local barrier | 4029, cluster-mapped barrier |
| ACC state advance | 3078 | 4032 |

Only the last expansion executes the ACC wait/arrival/advance. N128's later
cluster arrival at PTX 4492 belongs to TMEM deallocation, not a second ACC
release. Earlier epilogue stores consume registers after TMEM reads, so releasing
ACC after the last load preserves the existing ownership contract.

The SASS dependency, rather than the source-attributed NOP alone, establishes
the last-load ordering:

| Case | Final LDTM | LDTM control word | Elected ACC arrival | Arrival control word |
|---|---|---|---|---|
| N64 | `0x4640` | `000e620008120000` | `0x4660` | `0023e200081000ff` |
| N128/C2 | `0x6570` | `000e620008120000` | `0x6590` | `002fe2000810040c` |

Both final LDTMs set write dependency 1; both arrivals wait on mask `0x2`.
The intervening NOP has no wait mask. N128's
`SYNCS.ARRIVE.TRANS64.RED.A1T0` is a cluster barrier arrival, not an output
floating-point reduction.

## C-buffer and output ownership

All expansions share the carried TMA count (`%r1114` for N64, `%r1467` for
N128). Each count increments only in the TMA branch, then selects the same
modulo-two C stage. SIMT branches do not consume a C stage. The following
expansion uses the count resulting from the preceding conditional branch;
unrolling did not reset or replace it with the subtile index.

- N64 increments at PTX 2708/3136; store pairs 2752/2753 and 3182/3183;
  commit/wait-read-1 at 2755/2757 and 3185/3187; final wait-read-0 at 3539.
- N128 increments at 2824/3239/3657/4090; store pairs 2868/2869, 3285/3286,
  3703/3704, 4136/4137; wait-read-1 at 2873/3290/3708/4141, after each commit;
  final wait-read-0 at 4512.

The shared stores, async-proxy fence, pre-TMA CTA barrier, commit/wait and
post-wait CTA barrier remain in each taken TMA body. Source stage stride is
8192 bytes, with the existing two 4096-byte halves. Route coordinates advance
by 32 per expansion; the SIMT fallback retains its per-element route bound.
Thus mixed TMA/SIMT paths retain the original stage lifecycle and disjoint
expert-scratch output ownership.

Ordinary output operations are plain shared-to-global
`cp.async.bulk.tensor` / `UTMASTG.2D`. No output `cp.reduce`, atomic, or PTX
reduction opcode appears. The stored BF16 intermediate and subsequent fixed
top-k-order FP32 `moe_unpermute` are unchanged. This candidate does not introduce
TMA reduction or a lower-precision combine.

## Resources, parameters and fused identity

Both ordinary pairs have identical 23 PTX parameter declarations and resource
reports: REG128, STACK0, LOCAL0, static SHARED1024, CONSTANT[0]1856 and
CONSTANT[2]12. The fused pair has identical 25 declarations and the same resources
except CONSTANT[0]1888. Static SHARED1024 is not a measurement of total dynamic
shared memory; this compile-only helper does not report that total. There is no
source change to stage allocation or launch geometry.

The fused pair's entire raw SASS, including PCs, encodings and scheduling words,
is byte-identical, SHA256
`f83b7182fc53effcb21fd94a6cd14f9c47b6cf683d51f10c9832306e77382e1a`.
Its PTX is identical after removing only `.file` and `.loc` source metadata.
The ordinary SASS hashes are:

- N64 005: `c7eaf31627a4b35da75f5b83b5675e9b426c7f7b588592ed9d2ec6c823f4eeef`;
  006: `e0571e3b5ed80b51b24ad6e023061e17d4247e129b18874b28e3cfa850088958`.
- N128 005: `330f8b8ad01b9b14f7a2bc8859454c8b1a6f20b54dba9cc08d842615876deb66`;
  006: `7331ef7f1da118df66aad8df2d8169b1e05ae65e7a49a92ae1f0be4503185ff8`.

The hint is not a no-op: it adds 200 and 624 static instructions. The benefit
would need to come from removing loop/index overhead or enabling scheduling,
against the larger instruction footprint. No latency claim follows from this
review. The source-only review is preserved in
`candidates/nonfused_epilogue_unroll/INDEPENDENT_REVIEW.md`; focused numerics,
graphs/PDL and timing remain separate executor evidence.
