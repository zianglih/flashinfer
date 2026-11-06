# Independent routing-weight native review

Native safety/resource admission **PASS** for the three saved captures. Numerical execution may proceed. The intended load/store separation exists on the ordinary full-warp path; generated election-recovery paths can wait for the load earlier, so this is not an unconditional overlap claim. No throughput conclusion follows from these captures.

Source: `b9db4c19d57fff531a64b90683a5cd9c33be5134624156b3f1f9d2efd63d9826`; held patch `c2c36243ff9a5b4a405d345ae966c56ed018321100bf75cc60dad516a6865488`. Review used saved PTX, SASS including encoding words, compile records, and the owned transport source. No compilation, launches, tests, numerical validation, or profiler runs were performed for this review.

## Load/result ordering

PCs are function-relative hexadecimal. Each weight LDG is unpredicated and has write-dependency barrier 5. There is no explicit use of its destination register between this load and the listed lane-0 STG. On the main path, the first `0x20` dependency wait is attached to that STG.

| Case | Weight LDG | Input TMA / input wait | Prior full wait | Pool TMA / provenance / commit | Weight STG (first result use) |
|---|---|---|---|---|---|
| N64/F4/direct | `11640`, R6 | `11770` / `117e0` | `11820` | `11950` / `11960` / `11970` | `119b0` |
| N128/F8/reuse | `132f0`, R8 | `13440` / `134b0` | `134f0` | `13660` / `13670` / `13680` | `136c0` |
| N64/F1/direct | `11620`, R6 | `11750` / `117c0` | absent | `11910` / `11920` / `11930` | `11970` |

The N64 LDG encoding ends in `000562000c1e1900` (write barrier 5, address-read barrier 2); N128 ends in `000362000c1e1900` (write barrier 5, address-read barrier 1). The early address-register-reuse waits `0x04`/`0x02` do not wait for the scalar result. The main-path prior `DEPBAR.LE SB0, 0` has encoded wait mask zero and names SB0, not the scalar load's barrier 5. The input-mbarrier slow loops also use only `0x04` and `0x02` waits.

**Explicit limit:** the compiler's `BRA.DIV` recovery for the full-mask pool-store election contains `WARPSYNC.COLLECTIVE` and `ENDCOLLECTIVE` with mask `0x24`, which includes barrier 5. These are N64/F4 `15430/15460`, N128/F8 `17d10/17d40`, and N64/F1 `151d0/15200`. Source control is warp-uniform at the election: the route-selection termination, work loop, prior batch count, and election member mask are shared by all 32 lanes; elected and lane-0 blocks rejoin before the next collective. The ordinary election path has no early result dependency. This review does not establish a dynamic frequency for the generated recovery path or claim its wait is absent.

## Protected ownership and resources

- The actual PTX retains full `-1` masks for every election, the same full/read wait instruction sequence, and all 20 CTA `bar.sync` operations. Per-case warp-barrier counts remain 11/12/10; release-atomic/reduction counts remain 13/14/12; mbarrier initialization counts remain 34/30/34. Register names change in some PTX sequences; whole-kernel instruction equivalence is not claimed.
- Weight publication now follows pool TMA, provenance STG, and commit, and still precedes every ready-flag path. F4/F8 retain the full-completion wait plus warp synchronization before batch publication, the read-only wait on nonpublication iterations, and the final full-completion wait plus synchronization before partial-tail publication. F1 retains its one per-token full wait, no read-only wait, no prior-write drain, and no partial-batch branch.
- Actual F4 publication full wait / GPU release / tail full wait / tail GPU release: `11a00 / 11c10 / 11d20 / 11e00`. F8: `13710 / 13920 / 13a30 / 13b10`. F1: full wait `11980`, release `11b00`. Existing post-tracker and final synchronization remain. Unchanged source ordering therefore still protects ordinary weight/provenance stores and scratch reuse.
- Retained dequant ordering is visible in both phases: final TMEM store, raw-slot arrival, TMEM completion fence, decoded publication. N64 landmarks remain `7020/7040/7050/7060` and `8040/8060/8070/8080`; N128 is `6f70/6f90/6fa0/6fb0` and `7f90/7fb0/7fc0/7fd0`. No pipeline design or stage-count change was introduced.
- Actual configuration, selected stages, launch dimensions, and resources match each paired control: REG 96, 640 threads, STACK/LOCAL 0, grid `[2,1,74]`, C2. N64 raw5/B3/D3 with dynamic SMEM 200064; N128 raw4/B3/D2 with 230784. Each capture records one compile and zero launches/allocations/collective initializations.
- Code-size cost is real: N64/F4 5472→5496 instructions (+24), N128/F8 6176→6208 (+32), N64/F1 5424→5448 (+24). No register or spill increase, but this is additional native control/address work, not a free instruction deletion.

## Saved artifact pins

Candidate directories: `profiles/cu132-recovery0910b-dispatch-weight-after-payload-default-candidate-{case}/codegen/`. Paired controls use `profiles/cu132-recovery0910b-dispatch-pull-barriers-default-candidate-{case}/codegen/`. Result records bind their actual PTX/cubin and compile resources.

| Case | Control result SHA256 | Candidate result SHA256 | Candidate SASS SHA256 |
|---|---|---|---|
| n64-f4-direct | `18e79242df6051bdd83dc9381c358d9082ea48803570f47449b1b929e9985285` | `c97528e07ab70d7787929dd4530c51dd788715e97eb1fbaf75950a13dfc38c69` | `6551a523d84c55c0fc934971cac2cf3bd61a212ad41270a4f880c3f8465cb2da` |
| n128-f8-reuse | `387162e2201b7df5236cf17f7e225a41453c4c56797e29bb85b5cdad262c10e1` | `85b7ca2081991e5ccd7dc084a6aba4d200aba450a82393424fa9282d0b8ff25e` | `96383b1ce638247d0637ceb651e554ad4ecc6099ec460cbd0b19f7908e78c0da` |
| n64-f1-direct | `52c7ffc496631e673822f5dfd663ec788d0976d2cf2b4f4b550db86dfb73f869` | `6377b1b4cd1c0ebf86f015ca59d84b1541504ba5203ad2570186cb0be1ec8023` | `62d5ac1373e40cfd23df0d2a9da6fdc621427d7d545cd0a24496cbd418a447f9` |
