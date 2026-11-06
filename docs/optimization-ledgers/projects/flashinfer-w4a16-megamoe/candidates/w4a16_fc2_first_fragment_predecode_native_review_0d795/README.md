# First FC2 fragment predecode: matched native review

Both N128 and N64 pairs pass the native quality gate. The candidate performs all 32 fully scaled BF16 values before blocking on the decoded TMEM stage, preserves those values through the wait's slow path, and stores them once after acquiring ownership. This is compilation and dataflow evidence only; no candidate kernel was launched and no numerical or performance result is claimed.

Production owner is `0d795ec767c1a588e4982d6972ef12dcf5b10683f55141310adab96efb6e1e86`. Both arms use the frozen `914b757a` cohort, original `268ac3a` sealed compile helper, identical fake descriptors/options, CUDA hidden, fresh private caches, and native direct compiler extension `bb367e30bb24541faa974ed05ff201171f61c5b18b01df9e46a406bdde5edbba` (DSL 4.7.1, compiler 13.3, CUDA 13.2 host). This is the actual imported shared-module overlay, with class identity and file hashes attested before/after. The shim and shared helper change only in the isolated candidate package.

## N128 pair

Geometry is M256/N128/K256, physical cluster (2,1), 512 threads with two decode groups, H7168/I2048/E256/top8, rank 0 of an EP8 descriptor fixture, maximum tokens per rank 512, flag 4, group hint 512, atomic schedule, epi flags (2,4), epilogue token return. This fixture creates no device tensors, process group, CUDA context or kernel invocation.

| Static result | Control | Candidate |
|---|---:|---:|
| SASS instructions | 5776 | 5784 |
| Initial registers / threads | 128 / 512 | 128 / 512 |
| Stack / local bytes | 0 / 0 | 0 / 0 |
| LDL / STL instructions | 0 / 0 | 0 / 0 |
| MMA / broadcast instructions | 16 / 4 | 16 / 4 |
| Normalized branch entries | 634 | 634 |

Both have the same DEC80/INC176 role redistribution and identical normalized branch/reconvergence topology. The exact opcode difference is eight extra `IMAD.MOV.U32`, four extra `LOP3.LUT`, one extra `LEA`, one fewer `IMAD`, and four fewer `NOP`: eight net instructions. The eight moves gather the second saved 16-value half into contiguous registers for `STTM.x8`. This necessary register placement is retained as an implementation cost, not grounds for a performance conclusion.

Each FC transform K body retains four packed `LDS.128`, two compact scale `LDS`, 64 E2M1 pair conversions, eight E4M3 pair conversions, 32 BF16 pair multiplies, 32 BF16 pair FMAs, and eight `STTM.x8`. No first-fragment conversion is duplicated. FC1's default source specialization is unchanged; its 219-instruction transform body has the identical opcode histogram and the same raw-wait/decoded-wait/first-store/last-store PCs (`0xb4b0 / 0xb510 / 0xb8c0 / 0xc250`). Physical register assignments differ, so this is not a byte-identical FC1 claim.

## Decisive FC2 order and liveness

The candidate raw wait reconverges before scale loads at `0xc400 / 0xc430` and the first packed `LDS.128` at `0xc420`. Sixteen E2M1 pair conversions, two E4M3 conversions and sixteen pair scaling operations all complete by `0xc710`. These 34 arithmetic instructions produce 32 fully scaled BF16 values before the existing decoded-stage fast branch at `0xc720`, retry at `0xc750`, and blocking slow path.

At that wait, the scaled payload occupies `R4–R11` and `R24,R23,R22,R21,R20,R3,R2,R0`. The barrier pointer and phase use `R13/R12`, whose scale-conversion duties have finished. Slow block `.L_x_218` at `0x16190–0x161d0` contains only phase retry, predicated nanosleep, phase wait, loop-back branch and return branch; it writes `P0`, with no general-register payload writes or stores. It returns to the original acquire reconvergence.

The first `STTM.x8` at `0xc970` consumes `R4–R11`; moves beginning at `0xca70` gather the remaining saved pairs before the second store at `0xcb80`. A capture-specific register-tag audit checks all 16 scaled pairs from their packed source words/bytes and scale halves through both stores, in original order. There is no TMEM store before ownership, no local spill, and no duplicate decode. Remaining conversion/store interleaving, fence, raw release, decoded commit and persistent state advancement retain their original source sequence.

`audit_n128.py` reads only the saved artifacts and writes `n128-audit.json`, including all SASS rows, counts, branch mapping, compiler/source attestations, per-phase bodies, the 34-op prologue and payload trace. Its explicit `--geometry n64` option audits the separately observed second pair. It also verifies each phase's final TMEM store precedes the TMEM fence, raw consumer release, and decoded producer commit. These are native static counts and liveness checks, not dynamic instruction totals, latency fractions or a numerical emulator.

## N64 pair and completed scope

The separately authorized N64 pair uses the same fixture and options with M256/N64/K256. This retains the existing three decoded TMEM stages; N128 retains two. Both N64 arms have REG128/512 threads, STACK0/LOCAL0, zero LDL/STL, 16 MMA and four broadcasts. SASS changes from **5448 to 5456**, with exactly the same opcode delta as N128. The 586-entry normalized branch topology is unchanged, and the FC1 body again has an identical opcode histogram. Each FC phase has the same packed/SF loads and conversion/scaling/TMEM-store totals as N128.

N64 scales all first 32 values by `0xc630`, before the acquire fast branch at `0xc640` and retry at `0xc670`. The payload register assignment and both-store sequence match N128. Its independent slow block is `0x14cb0–0x14cf0`, with barrier address `[R13+URZ+0x68]` and phase `R12`; it writes only `P0`. First stores are `0xc890` and `0xcaa0`, at TMEM offsets `0x80/0x88` rather than N128's `0x100/0x108`. `n64-audit.json` preserves the complete separate analysis.

Both runners exited zero; all four captures contain one real `cute.compile` and zero compiled launches, device allocations or collective initializations. All 3,684 production files and 29 frozen cohort inputs remained unchanged throughout. Complete capture folders and logs are preserved in:

- `logs/fc2-first32-predecode-0d795-firstpair-001.tar.gz`
- `logs/fc2-first32-predecode-0d795-remaining-001.tar.gz`

The post-run source/native/process check at **2026-09-08 17:33:13 UTC**, `logs/cu132-fc2-first32-predecode-cohort-post-idle-001.json`, verified source 0d795, frozen inputs and native extension again, with no compiler/cohort children. This was a CPU process check; it made no GPU query or GPU-idle assertion. The owner was told the compilation window was released before subsequent production work.

This cohort covers only direct-compiler N128/N64 epilogue-return fixtures. It does not validate fallback compilation, other geometries or return modes, numerical tails/rings, actual resource allocation after real tensor setup, or runtime performance. Those remain owner-controlled gates. The eight additional payload moves and small arithmetic redistribution must remain visible in any later performance interpretation.

To reproduce only the saved-evidence audits:

```bash
python3 -B candidates/w4a16_fc2_first_fragment_predecode_native_review_0d795/audit_n128.py
python3 -B candidates/w4a16_fc2_first_fragment_predecode_native_review_0d795/audit_n128.py --geometry n64
```
