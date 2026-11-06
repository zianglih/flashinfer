# Fast-divmod scheduler native review

PASS for the existing focused numerical tests. Reviewed only completed saved native artifacts; no capture, compiler, GPU, saved-validator or comparator rerun. Source range/candidate proof is in `SCHEDULER_RANGE_REVIEW.md` (`c1c1a8bb0ff2dc890a15cd4567a7aa823299f659be0ba7310583019ee0645441`).

Actual candidate source `3da04028baeabd5355011c52b70d01225ec47d0c3656a3c83b9f60cd3a221fd3`, manifest `58c83c6c6180382a957d6aef277690ce40f1e7f1c5338394c0f99e6fc42262ba`, scheduler `9d26c662949e7d41f4fb1190e8ebbaebcdf98baef7df03fc97ce5a4396234d19`. Closure `logs/cu132-recovery0911c-division-fastdiv-native-closure-001.json` SHA256 `34789b17d85c371682fc7e33df9245ab8a9e8cf12a329b2d8654529d6ebbc1e7` records source/native/idle completion. Each fixture records one actual compile, zero compiled launches/device allocations/collective initializations.

Artifact prefixes, relative to project root:

- Candidate: `profiles/cu132-recovery0911c-division-fastdiv-candidate-CASE/codegen/`.
- Exact corresponding control: `profiles/cu132-recovery0911c-static-dims-padding-revert-candidate-CASE/codegen/`, source `e470f255`.
- PTX and source-correlated SASS are in each `dsl/`; raw disassembly is `sass.txt`.

| CASE | Raw SASS instructions e470 → candidate | Dynamic SMEM bytes | Raw / activation / decoded / scheduler stages | Scheduler-source max explicit R |
|---|---:|---:|---|---:|
| m128c1-f4-direct-i2048 | 5056 → 5056 | 194048 | 5 / 3 / 3 / 3 | 30 |
| n64-f4-direct-i2048 | 5424 → 5408 | 200064 | 5 / 3 / 3 / 2 | 33 |
| n128-f4-reuse-i2048 | 6120 → 6104 | 230784 | 4 / 3 / 2 / 2 | 33 |
| n64-f4-reuse-i2112 | 5720 → 5680 | 200320 | 5 / 3 / 3 / 2 | 44 |

All four retain REG96, 640 threads, STACK0, LOCAL0, 1024 static shared bytes, the same cluster/grid, stage records and workspace/tensor descriptor shapes. PTX contains no local-memory loads/stores. Scheduler-source register references are below the existing control-role cap80; this is a source-correlated register check, not a new full-CFG liveness analysis. Redistribution caps remain unchanged.

## Both mapper sites lower as intended

- **Partial `/17` and `/29`:** candidate PTX 899–924 and 1580–1605 first subtract the current expert start from the claim, then execute the phase-selected fast quotient and original scalar remainder. `/17` uses `mul.hi.u32` with immediate `-505290270` (unsigned bits `0xe1e1e1e`); `/29` uses immediate `444306962` (`0x1a7b9612`). Each quotient follows `hi=mulhi(x,M); q=(hi+((x-hi)>>1))>>4`. The remainders use `x-q*17` or `x-q*29`, then the existing CTA coordinate conversion. SASS confirms predicated IMAD.HI.U32, subtract/LEA/SHF and scalar IMAD at `0x23e0–0x24a0` and `0x3cb0–0x3d50`. The two general signed divisions present at control PTX 903/1569 are absent from these mapper sites.
- **Full C2 `/16` and `/28`:** N64 PTX 914–929 and 1587–1602; N128 PTX 908–923 and 1591–1606. `/16` is unsigned shift4 with remainder mask15. `/28` uses immediate `613566757` (`0x24924925`) in the same multiply/subtract/shift/add/shift quotient form and scalar `x-q*28`. Source-correlated SASS confirms both expansions; N128 uses IMAD.HI.U32 at `0x2360` and `0x3bf0`.
- **Static C1 `/32` and `/2`:** PTX 708–715 and 1273–1280 selects shift5/shift1 and mask31/mask1. The signed shift from e470 becomes an unsigned shift, which is equivalent on the proved nonnegative domain. Unchanged instruction count does not imply byte identity.

Other existing signed divides remain later in transport/router code. This review claims removal of the two scheduler `/17`–`/29` divides, not removal of every divide in the Mega kernel.

## Setup, interface and state

The fast-divmod multipliers/shifts appear as immediate constants at the two existing decode sites. No divisor preparation, reciprocal setup, additional state load/store or extra call is emitted for their construction. The saved host IR contains no FastDivmod setup. Every candidate retains one PTX entry and has a byte-equal parameter declaration list to its matching e470 PTX. Tensor descriptors and actual stage observations compare equal. The source diff adds no scheduler fields, serialized values, queue/state storage or host ABI parameters; current workspace sizes/resources also remain equal. Constant creation therefore does not introduce per-work setup beyond the quotient arithmetic itself.

The phase and interval comparisons still precede the quotient, and both decoded quotient/remainder paths feed the same token/feature index and tail clipping code. Native lowering is consistent with the range proof; actual routed numerics and launch lifecycle are the next independent checks. No latency or promotion conclusion follows from this review.

## Pins

| CASE | result.json SHA256 | PTX SHA256 |
|---|---|---|
| m128c1-f4-direct-i2048 | `04ad99f84affedfbe40260f720e5682f0a85c4f5013533e9759ca91ba5987512` | `8c12b90db4eec5157c0a33bd0863d1d3787b47b9fce3fc313a06d34b98673e7f` |
| n64-f4-direct-i2048 | `67e8a1f08afa4f806eddc0f650799b1458ac67d624f3de6085e6c22de858a82d` | `19d58ee6688bfde240ffd28b47cccff05db60d0ca7713ece8c9290451407831a` |
| n128-f4-reuse-i2048 | `07c8753ee5cdc377643e95107a7fefb0ed95ae2063fabbceeba9382e0e7f72aa` | `3c4915e67a09f24eb3d6a2c7c6fef404156a596e4fbc1be81ce54910d435350a` |
| n64-f4-reuse-i2112 | `4112c8a559cd76b2b9d20687eee08440fbdbefa9f592133accb1529d482df2e5` | `3cef1fb2015f5016b1d93060fc79e8e7f39e0c65c4360d38ed75968923087719` |
