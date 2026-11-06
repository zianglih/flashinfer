# Finalizer ownership audit

Read-only source, generated-code and historical-experiment review. No kernel
change or GPU work is part of this audit. The preparation SF-preload candidate
remains frozen for the composed retention campaign.

## Critical-path evidence

`../DIAGNOSTICS.md` records matched public-chain traces at 16,384 tokens:

- V3 MXFP4x8: swap-AB graph 684.052 us versus legacy fused 599.076 us. The
  standalone deterministic-combine critical extension is 86.144 us; the GEMM
  critical spans are close. This is a material combine target, although the old
  fused reduction has a different contract.
- N3U NVFP4: swap-AB combine extends the chain by 54.752 us, versus 53.600 us for
  legacy unfused. The old finalizer's 242 us total duration overlaps FC2; its
  total duration must not be mistaken for a 242 us critical bottleneck.

## Current ownership

`blackwell/moe_finalize.py` assigns each thread eight adjacent BF16 values per
vector. Payload loads and output stores are 128-bit; routing metadata is loaded
before the PDL dependency wait and payload loads follow it. Each output uses
original slot zero's separate multiply and ascending later-slot FP32 FMAs,
followed by one BF16 conversion. Invalid routes are masked before payload reads.

The reduction has slot as its outer loop and vector as its inner loop. Its
`(4, vectors_per_thread)` Uint64 accumulator keeps all vectors live through the
whole reduction; only then does a separate vector loop convert and store them.
This is present in generated SASS, not merely apparent in the Python source:

| Existing generated case | Packed accumulator pairs | Registers | LDG128 / STG128 | FMUL2 / FFMA2 |
|---|---:|---:|---:|---:|
| H2048, top-k22, two effective vectors | 8 | 58 | 44 / 2 | 8 / 168 |
| H7168, top-k8, seven vectors | 28 | 80 | 56 / 7 | 28 / 196 |

The first case is `../finalize/codegen/0.sass`: R6/R8/R10/R12/R14/R16/R18/R20
hold the eight pairs across all slots; conversion starts at 0x2c30 and both
stores occur at 0x2ce0/0x2cf0. The second is the retained packed-arithmetic
`scripts/perf_round_20261027/packed-combine-scalar/exact/compile-145.sass`, with
its parameters/resources recorded in that directory's `codegen.json`. Neither
has stack, local memory or spills. The latter uses 56 FP32 accumulator registers
before accounting for metadata, addresses and payload temporaries.

## One fresh direction: finish each vector before starting the next

Interchange the independent loops to vector outer, ascending slot inner, with
conversion and the existing 128-bit store immediately after that vector's
reduction. A single vector needs four Uint64 accumulators rather than keeping
every vector's accumulators simultaneously live. Preserve the same thread/grid
geometry, vector width, 16-byte alignment contract, metadata loads, PDL wait,
masking and arithmetic helpers. This requires no tactic or workload policy.

Each individual output still executes the same slot-zero multiply, the same
ordered valid-slot FMAs, and the same conversion. It changes neither reduction
association nor the original-slot-zero signed-zero rule. Input/output storage
must remain separate as required by the existing contract. The current
single-vector cases should compile identically.

The opportunity is lower register pressure and potentially more memory-latency
coverage. It is not a speedup claim: the current multiple-vector layout also
provides useful load/math instruction overlap and shares route-valid branches.
Interchange may duplicate that control/address work, retain routing metadata
longer, or reduce useful per-thread concurrency. Earlier profiles were already
near 69–71% of peak DRAM bandwidth, so a register reduction may be neutral.

## Why this is distinct from closed work

The geometry/vector experiments rejected wider 256-bit loads, broad CTA-width
changes, one-warp ownership, selective scale loads and warp-coalesced metadata.
The earlier prefetch candidate in `scripts/finalize_geometry_experiment/build.py`
loads all vectors for a slot before computing that slot; it retains slot-outer
reduction and all vector accumulators. The retained raw-pair packed arithmetic
removed conversion instructions while retaining the same accumulator ownership.
The current vector-cap diagnostic was codegen-identical because the compiler
already eliminated unused vectors. Searches of experiment Markdown/Python for
loop interchange, vector outer, slot inner and serial vector found no prior
trial of this specific lifetime change.

## Gate before timing

After the composed campaign is launched, any separate trial should first compare
generated code for one-vector, native seven-vector and top-k22 small-hidden
cases: actual register reduction, no spills, same payload load/store counts,
preserved packed arithmetic, and branch/instruction cost. Exact-byte comparison
must include masked original slot zero, all-masked rows, signed zero/subnormal/
NaN cases, expanded and permuted input, all supported scale dtypes, PDL on/off,
partial tails and 16-byte-only alignment. If codegen supports the hypothesis,
two fixed-winner public-chain CAAC cells (V3 MXFP4x8 and N3U NVFP4 at 16K) plus
their critical-tail traces are enough for an initial decision. No broader
campaign is justified without that evidence.
