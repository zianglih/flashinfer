# Candidate007 useful-subtile native review

**PASS for the existing focused runtime gates.** The changed ordinary N64 and
N128 paths and separate fused/N16 control comparisons pass. This is native
admission evidence, not a numerical or performance claim. No remote
operation, source edit or new native capture was performed for this review.

## Captured source and ordinary fixtures

The actual source is 005 plus the held007 bound, without the rejected006 unroll
hint. Kernel SHA256:
`ae6ef44ce1aa0c64bdad284e8ecae69977709bd125f397683c012639f25b3e72`.
Wrapper SHA256 remains
`aa446d91adfd1335d59bf30acb8ed240f6b592bd78724d02f230cde7806fd90d`.
Use these result-file source hashes; the helper's historical `git_head` is not
the overlaid candidate identity.

| Case | Directory under `native/` | Result SHA256 | Instructions |
|---|---|---|---:|
| 005 ordinary N64/C1 | `candidate005-tma-prefix-ordinary0-m256-tile-n64` | `d13f84860aad8052d0004bfd549836773d8251b64d267a4a3270148ea5458c1a` | 1624 |
| 007 ordinary N64/C1 | `candidate007-useful-subtiles-ordinary0-m256-tile-n64` | `a62c7d312b34b3031a8bce44aea662c82636fc4b014a9e7af76513921c5833ee` | 1632 |
| 005 ordinary N128/C2 | `baseline006-ordinary0-m256-tile-n128-mma256-c2` | `1a18261a4b609796154090162054510049f93eed7c0c56b8fee990c3bb703435` | 1736 |
| 007 ordinary N128/C2 | `candidate007-useful-subtiles-ordinary0-m256-tile-n128-mma256-c2` | `8d39adff4dfaeb253757b3537ee11c1aeb150f3ea04e2c85c8879245b91ff7f3` | 1744 |

Both ordinary captures are compile-only logical M256/N256/K512, eight groups,
top-k0, num_tokens0, static scheduler and PDL disabled. N64 uses MMA128/N64/K256,
C1; N128 uses MMA256/N128/K256, C2. The callable was not invoked. Runtime route
metadata remains dynamic despite the fixed compile-only fixture.

## Bound and runtime final release

PTX references are line numbers in the sole `.ptx` under each candidate `dsl/`.

| Fact | N64 | N128/C2 |
|---|---|---|
| Clamp | 2607–2608: max(D,1), min(...,64) | 2707–2708: max(D,1), min(...,128) |
| Ceiling count | 2610–2611: add31, `shr.u32` by5 | 2710–2711: add31, `shr.u32` by5 |
| Last index | 2613: count−1 | 2713: count−1 |
| Loop initialization | 2622: index0 | 2722: index0 |
| Last-index predicate | 2650, skip-release branch2652 | 2750, skip-release branch2752 |
| TMEM-load wait | 2654 | 2754 |
| Elected ACC arrival | 2664, local shared barrier | 2766, cluster-mapped shared barrier |
| ACC advance | 2667–2671 | 2769–2773 |
| Loop index increment | 2674 | 2776 |
| Backedge | 3088–3089: next index!=count | 3190–3191: next index!=count |

The clamp guarantees count1..2 or1..4 before adding31, so the added arithmetic
cannot overflow even for arbitrary private Int32 D. The ceiling division emits
no general divide, remainder, reciprocal or runtime divisor setup: SASS uses
two `VIMNMX`, `VIADD 0x1f` and `SHF.R.U32` by5. These are genuine runtime bounds,
not compile-time unrolling.

There is exactly one executed final wait/elected arrival/ACC advance per work
tile, guarded by the runtime `index == count-1` test. D<=0 still performs one
TMEM-read iteration. Output predicates continue to use original D, not clamped
D, so this private case takes fully masked SIMT stores. For public positive D,
only wholly invalid suffix slabs disappear; the final partial slab remains.
No change is made to MMA's full-tile computation or number of consumers.

Actual SASS establishes read-to-release dependency before branching:

| Case | Last LDTM | Control word / write dependency | Following branch | Control word / wait mask | Elected ACC arrival |
|---|---|---|---|---|---|
| N64 | `0x39a0` | `000ea40008120000` /2 | `0x39b0` | `004fea0003800000` /0x4 | `0x3a00` |
| N128/C2 | `0x3e50` | `000ee40008120000` /3 | `0x3e60` | `008fea0003800000` /0x8 | `0x3ef0` |

The source-attributed TMEM wait is represented by a NOP plus the surrounding
scoreboard scheduling; the NOP alone is not the proof. Both branch paths wait
for the final load dependency, and only the last iteration enters the elected
release block. N128's `SYNCS.ARRIVE.TRANS64.RED.A1T0` is a cluster barrier arrival,
not an output floating-point reduction.

## C stages, precision and drain

The carried C count is initialized outside the persistent work loop and changes
only in the TMA branch: `%r976` at N64 PTX2734 and `%r1031` at N128 PTX2836.
The same modulo-two calculation follows each increment. The SIMT branch leaves
that count untouched; both branches join before the runtime backedge. Omitting
an entirely invalid suffix therefore removes neither a C-stage increment nor
a TMA operation that the original path would have performed.

N64's plain TMA store pair is PTX2780/2781, followed by commit2783,
wait-read-1 at2785 and the post-wait CTA barrier2788. N128's corresponding pair
is2882/2883, commit2885, wait2887 and barrier2890. The original shared stores,
async-proxy fence and pre-TMA CTA barrier also remain. Both use the existing
8192-byte shared stage stride and two4096-byte halves. Route coordinates retain
the subtile index times32; the fallback preserves its per-element route bounds.
Final C drain remains wait-read-0 at N64 PTX3148 and N128 PTX3269.

Output opcodes remain plain shared-to-global `cp.async.bulk.tensor` /
`UTMASTG.2D`. Neither ordinary PTX has an output `cp.reduce`, `atom.*` or `red.*`
operation. BF16 expert-scratch conversion/storage and the unchanged external
ascending-top-k FP32 `moe_unpermute` preserve the existing precision contract.

## Resource and parameter cost

Each ordinary candidate adds eight SASS instructions. Their 23 PTX parameter
declarations are exact matches to their immediate controls. All four ordinary
reports have REG128, STACK0, LOCAL0, static SHARED1024, CONSTANT[0]1856 and
CONSTANT[2]12. This static SHARED count is not total dynamic shared memory; the
compile-only helper does not report that total. There is no source stage or
launch-geometry change.

Candidate SASS SHA256:

- N64: `91c5a10bce9556f78013de3e3b174cd8bba050185acfb9a74930d5fee2165292`.
- N128/C2: `7802e312af1e4af9b371aa656a3c3b6f5286aaa507759133f7ab26009b5428db`.

## Separate control identity and runtime scope

Integration independently compared only the excluded controls, with completed
evidence sealed in [CANDIDATE007_UNCHANGED_CONTROLS.md](CANDIDATE007_UNCHANGED_CONTROLS.md),
SHA256 `a0a910d8c3cb9ae7f88c82c04c9af84a351066c9703eb6dae761d0721afa4a01`.
That comparison was not replayed here.

- Fused N64 stays1568 instructions, entire raw SASS byte-exact including PC,
  encoding and scheduling, SHA256
  `f83b7182fc53effcb21fd94a6cd14f9c47b6cf683d51f10c9832306e77382e1a`.
  Candidate result is
  `055cf1bfb3578d58040f6bf69179dfcb82d7f8296e3635f49148ace4eb5f469f`.
- Ordinary N16 stays1640 instructions, entire raw SASS byte-exact, SHA256
  `7ff0bbc86b16c047d0ff7e21baf38015423434f3e38d45ffe2d511a0bd04455a`.
  Candidate result is
  `aef6532661a6e5e669f958eb51afca8119b682d32288ea877438434a1629130c`.
- Both control PTXs are exact after removing only `.loc` directives, including
  parameter declarations and `reqntid`512. Resource dumps are byte-identical:
  REG128, STACK0, LOCAL0, static SHARED1024, CONSTANT[2]12, with CONSTANT[0]1888
  for fused and1856 for ordinary. Dynamic shared-memory totals are not exported.
  N8/N32 are source-excluded too, but no separate native captures are claimed.

The source-only bound proof remains sealed at
`candidates/nonfused_skip_invalid_subtiles/INDEPENDENT_REVIEW.md`
(`e1920c49` prefix). The private-zero helper review is separately saved at
`candidates/nonfused_skip_invalid_subtiles/PRIVATE_ZERO_INDEPENDENT_REVIEW.md`
(`0556ca71` prefix). Runtime progress, bitwise equality, existing numerical/PDL
tests and the full sweep are separate executor gates; native code alone proves
none of those results.
