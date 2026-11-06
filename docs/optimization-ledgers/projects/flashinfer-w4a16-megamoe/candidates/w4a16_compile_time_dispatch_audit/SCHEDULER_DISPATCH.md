# Retained scheduler compile-time audit

Scope: clean `586994d8a054470a17c3dab05be8209c75a33128`, owned
`nvfp4_w4a16/fc1_fc2_fuse_sched.py`, retained source `2e3b651a`.
Read repository CLAUDE.md and code-review guidance. Initial audit used saved source/PTX/SASS only.

## Static versus dynamic

- Frontend `_ensure_compiled` supplies Python `(experts_per_rank, 2*I, H)`,
  geometry, padding, group hint, mode and scheduler depth. Base params preserve
  Python integers; `_mlir_fields` excludes static expert dimensions. Derived FC1/FC2
  feature-block counts at scheduler lines398–403 are already Python constants.
- Mode/storage selection and `_first_advance_pending` are already compile-time.
  The latter intentionally distinguishes first trace from loop trace; preserve it.
- Expert receive sizes are direct runtime loads. Group boundaries, residual expert
  walks, atomic/static claims, phase, token blocks and clipped tails depend on those
  values. Do not turn their conditions/loops into constexpr or remove explicit
  state carries/rebindings. Pipeline-state reconstruction remains per-field.

## Approved cached padding reuse

At old lines676–678 and760–762, reuse `current_token_block_count` when
`token_padding == cluster_tile_m`; otherwise preserve the original ceil quotient.
This equality is compile-time. No new state, serialization field, helper or knob.

Invariant: the cached count equals `(current_this_expert_token_cnt +
cluster_tile_m - 1) // cluster_tile_m`. Its only assignments are paired zero
initialization (376–377), a pair from one size load (684–693), and paired zeros at
FC2 rewind (725–726) and group prime (820–821). Residual drain refreshes state
before the final group push. Multiplying this cached quotient by the equal padding
therefore matches the old Int32 arithmetic, including its signed/wrapping behavior.

Public frontend line199 chooses padding=mmaN. The base swaps CTA/cluster axes once,
and supported clusters have original N-axis extent1; thus scheduler cluster_tile_m
is the same mmaN for all public M128/M256, N64/N128, C1/C2 geometries. The low-level
kernel also permits smaller padding divisors (kernel179–180), so preserve the
compile-time unequal-padding fallback.

Saved native shows this is not merely redundant Python: the retained static
M128/C1 capture's source-correlated `.sass` has75 instructions attributed to old
line677 across unrolled sites and17 to line761. These are emitted instruction
counts, not predicted savings or cycles. N64/C2 PTX likewise retains signed-floor
rounding before padded-row increments.

## Approved phase-divisor specialization

Source already branches on dynamic FC1/FC2 phase. In retained static M128/C1
H256/I2048, LLVM merges the two static divisors32 and2: PTX lines712–721 and
1286–1295 select a denominator then issue `div.s32`. Source-correlated SASS has
28 first-site and31 steady-site instructions attributed to division line851,
including IABS/I2F, MUFU.RCP, F2I and quotient/floor correction. These counts include
moves and predicates attributed by line information; they are not cycle counts.
N64/C2 H7168/I2048 instead retains constant-specialized /16 and /28.

A runtime phase cannot become constexpr. The applied change keeps both phase
arms and tests the existing `self._num_*` fields directly with `const_expr`:
the divisor must be a positive Python integer with exactly one set bit. For that
case only, use `local_id >> Int32(divisor.bit_length() - 1)`. Non-power-of-two and
dynamic divisors retain the original `//`; the existing `local_id - quotient *
divisor` remainder is unchanged. There is no new field, helper, runtime divisor
classification or tactic knob.

The arithmetic follows the existing pattern in
`flashinfer/flashinfer/attention/prims_ts/kernels/mla_decode/helpers/tile_scheduler.py:40–54`.
For signed Int32 x and positive `d=2**s`, arithmetic right shift gives
`floor(x/d)`, including negative x. The native check must establish signed
`shr.s32`/arithmetic SASS lowering, not unsigned shift or truncating division.
The maintained caller supplies Python static expert dimensions; base params
preserve them, and the existing derived fields remain constants through
serialization. The Python-int guard retains the former dynamic-dimension path.

Final scheduler SHA256:
`a8127cb3fff080b0f1964d8eb927f3d7b0db303592a0cefc5c8dc5002a3a1aac`.
`divider.patch` SHA256:
`ca34ea00bd2ffeb19407417e12d5203f7b8084625ebbebae88d307b8b6c69db3`.
This patch is against the prior frozen padding+epilogue scheduler; an AST
comparison confirms only `_decode_inside_expert` differs. Scoped pre-commit
(including mypy/Ruff) and `git diff --check` passed. Native confirmation remains
pending; no instruction-count or timing benefit is claimed from source alone.

## Validation

Current combined epilogue/padding/divider patch has AST, diff-check and scoped hooks PASS.
Native candidates should cover full N64/C2 H7168/I2048 direct, partial N64/C2
H7200/I2112 reused return, static M128/C1 H256/I2048, and N128/C2 full.
Check actual removed width input/bound/rounding, dynamic phase/tail behavior,
REG96/640 and no spills, stage/SMEM identity. Existing reference/tail selections
and C1 routing helpers cover both returns, partial H/I, static/atomic and
empty/skew/refill. No new tests, performance replay, source commit or push in this audit.
Specifically inspect the C1 `/32` and `/2` paths for signed shifts and removal of
the merged dynamic divide; full C2 `/16` versus `/28` and partial C2 `/17` versus
`/29` preserve mixed and non-power-of-two fallback coverage. These are scheduled
native checks, not completed results.

Saved evidence directories:
- `profiles/cu132-recovery0911c-retained5869-before-m128c1-f4-direct-i2048/codegen`
- `profiles/cu132-recovery0911b-epilogue-constructor-cleanup-candidate-n64-f4-direct-i2048/codegen`

The latter capture is historical node15, same retained source; the former is node59.

Final native follow-up: `NATIVE_REVIEW002.md` records source dd4ce416 PASS with
the same a8127cb3 scheduler. C1 now emits phase-selected signed shifts5/1 and
masks31/1 (SASS `SHF.R.S32.HI`); mixed `/16`–`/28` and nonpower `/17`–`/29`
retain floor-correct fallbacks. All resources/stages remain unchanged. Numerical
tests were released after native admission; this note makes no timing claim.
