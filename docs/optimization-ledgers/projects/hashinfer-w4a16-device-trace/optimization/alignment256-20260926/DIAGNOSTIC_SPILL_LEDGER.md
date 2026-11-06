# Fixed native diagnostics: source-bound spill and instruction audit

Independent audit passed all nine source variants, 36 rank reference checks and 36 rank finite/repeat checks. Every arm used the same H6144 / I2048 / E256 / top8, EP4, uniform 128 global tokens (32 local) fixture and exact native catalog tactic index 6: N64/G1024/epilogue returns. All ranks and arms produced identical bit hashes for inputs, weights and outputs. Both native PTX and CUBIN/SASS target SM103a. These are fixed-tactic diagnostics; none of their timing samples establishes AUTO selection or performance retention.

The compound `1c6ba01ee64fdbfa68b365fa92a43bb77ae170fb` removes every LDL/STL site and reports STACK 0 in all four exports. It keeps the payload instruction reduction. Late preparation and the all-WG tail register restoration address complementary compiler state: the former removes early cross-role state; the latter removes payload spills.

## Native instruction/resource comparison

Counts below normalize payload accesses to the same 16 BF16 outputs per lane. Eight routed vectors feed each output. At 128-bit width, two workers are needed for 16 outputs; at 256-bit width, one is needed. Score-prefetch issues are reported separately per eight FP32 scores and are not included in the payload counts. Whole-kernel LDG/STG counts are not used as the reducer comparison.

| Variant | Payload bits | Payload LDG/16 outputs | Output STG/16 | Score bits/issues | REG | STACK bytes | LDL sites | STL sites |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| before | 128 | 16 | 2 | 128/2 | 96 | 0 | 0 | 0 |
| width 8-control | 128 | 16 | 2 | 128/2 | 96 | 0 | 0 | 0 |
| payload-candidate | 256 | 8 | 1 | 128/2 | 96 | 40 | 10 | 17 |
| late-candidate | 256 | 8 | 1 | 128/2 | 96 | 24 | 4 | 9 |
| rebalance-candidate | 256 | 8 | 1 | 128/2 | 96 | 40 | 10 | 17 |
| all96-candidate | 256 | 8 | 1 | 128/2 | 96 | 16 | 6 | 13 |
| score-candidate | 256 | 8 | 1 | 256/1 | 96 | 40 | 10 | 17 |
| score-only-candidate | 128 | 16 | 2 | 256/1 | 96 | 0 | 0 | 0 |
| late-all96-candidate | 256 | 8 | 1 | 128/2 | 96 | 0 | 0 | 0 |

No audited PTX contains explicit `ld.local`/`st.local`. Where SASS contains LDL/STL, these are assembler spills. LOCAL 0 by itself does not imply a spill-free kernel; STACK and actual SASS are the evidence. REG 96 is the binary resource report and does not mean every role uses 96 throughout compute.

## Which WGs execute spills

For width 16, `num_workers=32*(6144/16)=12288`. Each strip spans `148 CTAs*128 threads=18944`; strips are WG3, WG4, WG0, WG1. WG2 is excluded. For slot s, CTA c and local thread t, `worker=(s*148+c)*128+t`. Exactly WG3 CTAs 0..95 execute the payload, with all 128 threads active. WG0/WG1/WG4 have no payload. The stride 75776 exceeds the entire worker count, proving exactly one iteration per active lane and no next-worker prefetch/store.

For width 8 controls, 24576 workers activate all 148 WG3 CTAs and WG4 CTAs 0..43, still one iteration each. Those binaries have no local-memory sites.

All five spill-bearing native binaries have complete exact-PC maps in `fixed-diagnostics-wg-maps-v1.json`, with per-site SASS instruction, source-state interpretation, predicate PCs and CTA sets. These are static CFG plus finite fixture enumeration predictions, not hardware sampled instruction counters.

| WG and CTA range | Payload/rebalance/score STL/LDL per warp | Late STL/LDL | All96 STL/LDL | Compound STL/LDL |
|---|---:|---:|---:|---:|
| WG0, all | 6/1 | 3/0 | 6/1 | 0/0 |
| WG1, all | 6/1 | 3/0 | 6/1 | 0/0 |
| WG2, all | 3/0 | 0/0 | 3/0 | 0/0 |
| WG3, CTAs 0..95 | 10/10 | 7/4 | 6/6 | 0/0 |
| WG3, CTAs 96..147 | 4/3 | 3/0 | 4/3 | 0/0 |
| WG4, all | 4/3 | 3/0 | 4/3 | 0/0 |

Each 64-bit LDL/STL is one instruction in this table. The relevant guards and no-repeat drain paths were inspected independently in each native SASS. No local-memory instruction occurs inside the main MMA, scheduler, TMA or transform per-K loops in these fixed binaries. Initial shared zero stores and transform-tail stores are bookkeeping around retirement, not evidence that the MMA loop is spilling.

WG3 already has 96 registers during compute in the original policy. Thus the productive payload spill cannot be attributed directly to WG1 only having 80. The retired-tail rebalance (WG0 down to 96, WG1 up to 96, dispatch still 64) changes neither the 40-byte stack nor local-instruction sites. Restoring 96 for every WG after the common tail barrier reduces the stack to 16, consistent with a conservative shared-tail compiler register bound; exact compiler causality remains an inference. This restores 96 only after roles retire, not throughout MMA/epilogue compute.

## Remaining state in the two component variants

Late moves first reduction preparation after compute/drain and the common barrier. It removes all local traffic from dispatch and the earlier cross-role worker-count/token/tile state. It retains token/tile slots at 0x4/0x0, worker_idx at 0x8, and a 64-bit hidden element offset at 0x10: 24 bytes including padding. Only participating WGs execute the three initial stores; only active WG3 executes the payload spills. The updated-worker store executes after the final iteration, even though next-worker preparation is skipped.

### late-candidate

SASS SHA256 `d021eb06f9747a201ad2fe3352edce2036c07f93d4622f5a746c54d19cb5601b`.

| PC | Instruction | State | Executing WGs at this fixture |
|---|---|---|---|
| `0x10f00` | `STL [R1+0x8], R8` | save worker_idx | WG0,WG1,WG3,WG4 all CTAs |
| `0x10f30` | `STL [R1+0x4], RZ` | zero token_idx | WG0,WG1,WG3,WG4 all CTAs |
| `0x10f40` | `STL [R1], RZ` | zero hidden_tile_idx | WG0,WG1,WG3,WG4 all CTAs |
| `0x10ff0` | `STL [R1+0x4], R4` | save prepared token_idx | WG3 CTAs 0..95 |
| `0x11050` | `STL [R1], R2` | save prepared hidden_tile_idx | WG3 CTAs 0..95 |
| `0x110a0` | `LDL R2, [R1]` | load hidden_tile_idx | WG3 CTAs 0..95 |
| `0x110b0` | `LDL R0, [R1+0x4]` | load token_idx | WG3 CTAs 0..95 |
| `0x110d0` | `STL.64 [R1+0x10], R2` | save hidden_tile_idx*16 | WG3 CTAs 0..95 |
| `0x11bb0` | `LDL.LU R43, [R1+0x8]` | load worker_idx | WG3 CTAs 0..95 |
| `0x11bf0` | `LDL.LU.64 R40, [R1+0x10]` | load hidden_tile_idx*16 | WG3 CTAs 0..95 |
| `0x122b0` | `STL [R1+0x8], R43` | save updated worker_idx even after final iteration | WG3 CTAs 0..95 |
| `0x123a0` | `STL [R1+0x4], R6` | save next token_idx | none |
| `0x123f0` | `STL [R1], R2` | save next hidden_tile_idx | none |

All96 eliminates score, worker-index and hidden-offset payload spills. Its 16-byte frame retains token_idx at 0x0, num_workers at 0x4 and hidden_tile_idx at 0x8, plus padding. The early common initializers, transform retirement and retired WG0/WG1 preparation still materialize these slots across role branches. The compound delays this state until after the uniform 96-register tail and eliminates it entirely.

### all96-candidate

SASS SHA256 `4328d47377863c444c811e857cbf2d8246707486080d14e8c8fab9632a87f370`.

| PC | Instruction | State | Executing WGs at this fixture |
|---|---|---|---|
| `0xe220` | `STL [R1+0x4], RZ` | zero num_workers | WG0,WG1,WG2,WG3,WG4 all CTAs |
| `0xe250` | `STL [R1], RZ` | zero token_idx | WG0,WG1,WG2,WG3,WG4 all CTAs |
| `0xe260` | `STL [R1+0x8], RZ` | zero hidden_tile_idx | WG0,WG1,WG2,WG3,WG4 all CTAs |
| `0x10ab0` | `STL [R1+0x4], R3` | save num_workers | WG3,WG4 all CTAs |
| `0x10b90` | `LDL R14, [R1]` | load old token_idx | WG3,WG4 all CTAs |
| `0x10bb0` | `LDL R15, [R1+0x8]` | load old hidden_tile_idx | WG3,WG4 all CTAs |
| `0x10be0` | `@P1 STL [R1], R14` | save prepared token_idx | WG3 CTAs 0..95 |
| `0x10bf0` | `@P1 STL [R1+0x8], R15` | save prepared hidden_tile_idx | WG3 CTAs 0..95 |
| `0x11350` | `STL [R1], RZ` | zero token_idx | WG0,WG1 all CTAs |
| `0x11360` | `STL [R1+0x8], RZ` | zero hidden_tile_idx | WG0,WG1 all CTAs |
| `0x11410` | `STL [R1+0x4], R0` | save num_workers | WG0,WG1 all CTAs |
| `0x114d0` | `STL [R1], R3` | save prepared token_idx | none |
| `0x11520` | `STL [R1+0x8], R0` | save prepared hidden_tile_idx | none |
| `0x115d0` | `LDL R0, [R1+0x4]` | load num_workers for no-work guard | WG0,WG1,WG3,WG4 all CTAs |
| `0x11650` | `LDL R2, [R1+0x8]` | load hidden_tile_idx | WG3 CTAs 0..95 |
| `0x11660` | `LDL R88, [R1]` | load token_idx | WG3 CTAs 0..95 |
| `0x124b0` | `LDL R38, [R1+0x4]` | load num_workers | WG3 CTAs 0..95 |
| `0x12910` | `STL [R1], R3` | save next token_idx | none |
| `0x12960` | `STL [R1+0x8], R0` | save next hidden_tile_idx | none |

## Evidence and reproduction

- `fixed-diagnostics-audit-v3.json/.md`: all original eight arms, immutable inputs/helpers, four rank closures and complete WG maps.
- `fixed-diagnostics-compound-audit-v2.json/.md`: compound independently verified against the previous audit's before source/fixture/output hashes; all previous input hashes rechecked.
- `map_fixed_diagnostic_spills.py`: exact SASS-hash bindings, reviewed PC/predicate map and exhaustive ownership/one-iteration check.
- `fixed-diagnostics-wg-maps-v1.json`: every LDL/STL PC in all five spill-bearing variants; full map includes payload/rebalance/score as well as the detailed component variants above.
- Frozen fixed probe SHA256 `f0873341c2aedd225db72fd8a8e59b2390f35e4d17fc3df4ddcdd5bfaae99ea3`. Worker/driver/export helper hashes are in the audit JSON. None was edited by this audit.
- The full ABBA runner and auditor validate named campaign/source/receipt fields and tolerate the extra `source_arm_rebindings` history metadata without a benchmark-helper change. Each completed A receipt must still match source A. Full native AUTO ABBA evidence remains necessary for retention.

Use a fresh report prefix when rerunning; audit outputs intentionally refuse overwrite. From the project root:

```bash
python3 -B optimization/alignment256-20260926/audit_fixed_diagnostics.py \
  --diagnostics optimization/alignment256-20260926/fixed-diagnostics-v1-artifacts \
  --wg-maps optimization/alignment256-20260926/fixed-diagnostics-wg-maps-v1.json \
  --output-prefix optimization/alignment256-20260926/fixed-diagnostics-audit-v4
python3 -B optimization/alignment256-20260926/audit_fixed_diagnostics.py \
  --diagnostics optimization/alignment256-20260926/fixed-diagnostics-compound-v1-artifacts \
  --source-manifest optimization/alignment256-20260926/compound-diagnostic-sources.json \
  --expected-order late-all96-candidate \
  --reference-audit optimization/alignment256-20260926/fixed-diagnostics-audit-v3.json \
  --output-prefix optimization/alignment256-20260926/fixed-diagnostics-compound-audit-v3
```

## Original 128-bit contract controls

Two later controls retain the original 128-bit payload path while adding tail-register restoration, with or without late preparation. Independent audit `fixed-diagnostics-original128-audit-v1.json/.md` verifies their exact manifest package hashes, frozen helpers, fixed tactic, eight rank reference/repeat checks and bitwise fixture/output parity against the same before arm. Both report REG 96, STACK 0, no LDL/STL, and no explicit PTX local memory. Per 16 outputs, both retain 16 route loads and two stores; scores use two 128-bit loads. These controls provide correctness/codegen evidence, not retention timings.

| Control | Source commit | Stack bytes | LDL/STL sites |
|---|---|---:|---:|
| original128-all96-candidate | `240ead0a94b4dd56eb712dc4ddc1f9f501e907c6` | 0 | 0 |
| original128-late-all96-candidate | `af145b603fe4f542a644693c9bd2ef78f725e3bb` | 0 | 0 |
