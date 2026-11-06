# TMEM startup V2 gate — e1f42b2a

- **Passed:** 64 source-paired exact CLC replays and 24 static replays, spanning 32 CLC and 12 static FC1/FC2 × PDL core pairs. The static configurations cover 1CTA inline,1CTA overlap and2CTA overlap. Input, routing, output and artifact hashes agree with clean `9b4721b0` controls.
- **Resources:** all 44 core pairs have zero stack/local-memory bytes and no local load/store sites. Storage, pipeline stages, geometry, TMEM columns and UMMA commits are unchanged. Register deltas are −4…+2 for CLC and −2…0 for static.
- **Code size:** CLC static SASS increases by 209 instructions over 32 cores (per-core +2…+19); static increases by 60 over 12 cores (−1…+9). These counts are not execution-cost or speedup claims.
- **Provenance:** CLC controls reuse the original immutable same-GPU artifacts; static controls are fresh paired runs with the extended three-case probe. All 415 collected files are SHA-verified and both local validators exactly reproduce the remote validation JSON. `gate-v2-validation.json` includes both modes and the helper-repair record.
- **Helper repair:** the first static attempt rejected new config 8 through a stale `<8` bounds guard before compilation/replay. Its source/logs remain preserved. The repaired helper derives bounds from `len(configs)` and runs in a separate frozen directory/output. Its SHA is `c9177aef87dd3bd5b41653f649671799855acded26276877513503d12fde4234`. Completed CLC work was not rerun.

## Emitted dependency structure

`audit_barrier_contract.py` verifies all 44 candidate cores, with exact sites in `barrier-contract.json`:

- Inline epilogue: two distinct reader-role wait sites, each count 160; no separate allocator arrival. Every participating thread executes one wait, not both sites.
- Overlap: one nonblocking allocator-warp publication with count 192, followed by two distinct reader-role wait sites with count 192. The four epilogue warps and one MMA warp wait; the allocator warp only arrives, and other producers/scheduler do neither.
- Every 1CTA kernel has the independent initialization barrier0 before allocation. Two-CTA kernels retain the existing cluster join. Final all-thread barrier1 and 128-thread barrier2 retain their original counts.
- Pointer reads remain inside reader roles and final free, after the required synchronization. No common pointer read exists on the scheduler/pure-producer startup path.

Representative 2CTA overlap `gate-v2-clc-gpu6/candidate/config1-fc1-pdl0`: PTX 158 retains the cluster wait,165 emits `barrier.arrive 3,192`,380/1126 emit the two reader waits. SASS 357 is `BAR.ARV`;669/1825 are the two count 192 `BAR.SYNC.DEFER_BLOCKING` sites. Static 1CTA overlap `config8-fc1-pdl0` has initialization at PTX 111, publication118, reader waits296/1020. Full instruction/resource deltas are in `codegen.json`.

**Compiler spelling caveat:** source explicitly calls SDK 4.7.1 `arrive_unaligned()`/`wait_unaligned()`. Emitted PTX retains `barrier.arrive` but prints legacy `bar.sync` for reader waits in every core. The exact replay gate establishes the tested behavior, not why that lowering occurred or a universal alignment guarantee. Independent review found no new blocker: matching SASS publication/wait sites and exact replay coverage are consistent with compiler canonicalization. Intermediate IR was not captured, so the specific pass is unconfirmed; do not describe the emitted PTX waits as unaligned.

No sanitizer or end-to-end speedup claim follows from this focused gate. Model timing is recorded separately in `screen-v2`; both variants are rejected after neutral timing. The completed local source copy was removed only after exact frozen-source verification; all useful evidence remains.
