# Final compile-time dispatch native admission

PASS for the existing focused runtime tests. Read-only review of completed source `dd4ce41601911cea0156546cdc5f17287866f7887cda7f06b728e48efea14c06`, manifest `a8e7f20bf1ef7f486c35cb908f6ff2bbbe7dc298eace4b2a10cff6478b811867`, epilogue `68674590` and scheduler `a8127cb3`. No capture, comparator, validator or GPU launch was repeated by this reviewer. This is native admission, not numerical or performance evidence.

Paths below begin `profiles/cu132-recovery0911c-static-dims-final-candidate-` and end `/codegen/`. All four actual results record one compile, zero launches, REG96/640 threads, STACK0/LOCAL0 and static shared1024. Stages and dynamic shared match the preceding capture; two decode WGs and five total WGs remain.

| Case | Result SHA256 | Dynamic SMEM | Raw/B/D/S |
|---|---|---:|---|
| `m128c1-f4-direct-i2048` | `44cd5314d6433fdac782f045abbff915a4ef80d8b0bc502a2ebe7936c5e4393b` | 194048 | 5/3/3/3 |
| `n64-f4-direct-i2048` | `754344e3133fe35c3cf9c6e83788dc74334ee08e7870e8d66ce3f093ec1b1595` | 200064 | 5/3/3/2 |
| `n128-f4-reuse-i2048` | `d9b64486025ac2ca6c49867175b4f02a10ea219cffa9a9f351873c4e3d7de16a` | 230784 | 4/3/2/2 |
| `n64-f4-reuse-i2112` | `6fb4dcc04e866324331a104c75264f9b9d6e1d28774bb64e2ebd581f9a0f7936` | 200320 | 5/3/3/2 |

## Emitted checks

- **Full H256/H7168:** router code no longer subtracts the feature base from H or clips the extent. Full-hidden predicates also disappear. N64/direct PTX5925–5945 goes from the hidden-base shift to metadata addressing and the live token guard, then the guarded metadata load. N128/reuse PTX6448–6483 computes the local row/hidden bases, waits for ACC and retains the live subtile-token guard; the hidden clips are absent. C1 has the same specialization. Source-level proof remains H divisible by128*C, not merely128.
- **Full I2048:** FC1 output stores retain token checks, but no feature comparison against2047. N64 token guards remain at PTX5541/5844; N128 retains four half-subtile token guards at5502/5794/6089/6388; C1 retains its token guards at5069/5370.
- **Partial H7200/I2112:** PTX5876–5879 still emits `7200 - tile_m*128`, max0 and min128. FC1 PTX5505–5521 retains both token and feature2111 predicates before the store body. More strongly, its complete `sass.txt` is byte-identical to preceding source846c: SHA256 `31093c73b985a4a1d5f9ff6b4ba1e42b188e616b62906e1a35d7c1cabe901bdc`. Final source therefore preserves the existing partial-case instructions, encoding and scheduling.
- **C1 signed quotient/remainder:** PTX787–790 and1428–1431 selects shift5/1 and mask31/1. The quotient uses `shr.s32`; SASS `0x1c00` and `0x3420` are `SHF.R.S32.HI`, followed by the low-bit remainder mask. This is floor division for signed Int32, including negative values. No merged general division remains at these sites.
- **Mixed and nonpower fallbacks:** final N64/full PTX990–1009 and1747–1766 preserves signed `>>4` plus mask15 for FC1, and `/28` multiply-high with negative-nonmultiple correction and remainder for FC2. N128/full has the same operations at985–1004 and1748–1767. Partial I2112 retains the selected17/29 signed division and floor correction at978–988/1722–1732, also covered by the whole-SASS identity above.

No changed source or emitted evidence indicates a movement of scratch reads, accumulator release, completion publication, metadata visibility or output stores. Live phase/token/partial predicates remain; only shape-proven work was specialized. Existing numerical/graph coverage is still required and was released to the sole executor after this review.

## Exact evidence

Sole `dsl/*.ptx` SHA256s, table order:

- C1: `5c5ebea5bc8587bb07e4f6f7c25a263ad9d4b67cda2d74d0816a90c5ac5bd7ca`
- N64/full: `a995f5799b3397c00374348d158f63d75685e3d76d388e7d325cdf4c3238be41`
- N128/full: `ac41025bbd5bd4e660dc93d049799a9f76255b8a684ee053f85afb362b5de14e`
- N64/partial: `92d84a5d43613f2210176d4ee05c5f779a909df4e373d475349f8aa702f49cfe`

Source/native/idle closure: `logs/cu132-recovery0911c-static-dims-final-native-closure-001.json`, SHA256 `0ab800740fbcdcec6d33a4344c43f2ee692804fb0cc0d2ab9f2834bc668acd06`. The preceding846c review remains separately preserved in `NATIVE_REVIEW001.md`; it is not substituted for this final-source review.
