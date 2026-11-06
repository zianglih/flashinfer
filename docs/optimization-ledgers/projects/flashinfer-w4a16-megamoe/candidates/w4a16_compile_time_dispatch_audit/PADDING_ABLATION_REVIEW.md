# Padding-only ablation review

Read-only follow-up to the complete dd4ce416 candidate. Original source, native reviews and performance artifacts remain unchanged. Root restored only the two cumulative-padding ceil expressions; epilogue shape specializations and signed power-of-two division remain.

## Source scope

Independent source review PASS. Scheduler SHA256 `30c35c2b3d3c0d1dc7050d8c19411702b8ad9dcace5388b5043df6e4127e68b8` has only the `_decode_inside_expert` signed-divider hunk relative to retained586994d8. Both cumulative-padding functions, including their surrounding branches/state updates, match retained source exactly. Epilogue SHA256 remains `68674590e949b5d56b7375fa20fd9b98cdf5f109e45ad23570809aa1a9512fd9`. No source edits or hooks were run by this reviewer for the root-owned ablation.

The replacement uses the same values as retained: each cumulative-data update rounds the preceding expert's actual token count to `token_padding_block`, while cumulative-token-block updates continue to use `current_token_block_count`. This restores the original expression/dependency structure, without changing claims, phase/group transitions, sizes loads or record publication. A source restoration alone does not establish byte-identical native scheduling; the other retained changes can still affect compilation.

## Completeness of the preceding cached-padding native evidence

The dd4ce416 capture did emit the intended cached-count reuse. In
`profiles/cu132-recovery0911c-static-dims-final-candidate-n64-f4-direct-i2048/codegen/dsl/*.ptx`, the ordinary expert advance at769–773 shifts cached `%r2688` by6 and adds it to the data prefix, then adds that same cached count to the token-block prefix. The final group push at794–798 uses the same pattern and cached value. No fresh ceil sequence occurs at either site. N128 uses shift7; C1 and partial N64 use shift6. These are existing immutable artifacts, not a new capture.

Size loads still compute the necessary token-block counts elsewhere, and the compiler can combine residual-expert prefix additions across unrolled iterations. Thus this confirms local ceil elimination at the two selected updates; it does not imply that all scheduler ceil calculations disappeared, nor that reusing the count improved latency. The bounded ablation tests the source/dependency change rather than treating compile-time specialization itself as the explanation for performance.

## Native admission

PASS for the existing focused tests on source `e470f255b06bd492960ec21dd1b2556e36f49827fb99f1698133ce3f62102b0b`, manifest `e9e7e9e43664ddbf07bbd62f97b618285d27bd3bee134a71e18d0143a96a7ab3`. Each of the four actual results records one compilation and zero launches, REG96/640 threads, STACK0/LOCAL0 and static shared1024. Dynamic shared and raw/B/decoded/scheduler stages are unchanged. No numerical or performance result for this ablation is asserted here.

Paths begin `profiles/cu132-recovery0911c-static-dims-padding-revert-candidate-` and end `/codegen/`.

| Case | Result SHA256 | Dynamic SMEM; raw/B/D/S | SASS instructions dd4 → e470 |
|---|---|---|---:|
| `m128c1-f4-direct-i2048` | `3855817f3902e6ec4c3864bb193766d322694f4b02aa3355a764f55f411b3a7a` | 194048;5/3/3/3 | 5152 → 5056 |
| `n64-f4-direct-i2048` | `45dc4874027a301aa4ec313efa63a39f6450d52db6cefeb4a54cea208538b073` | 200064;5/3/3/2 | 5536 → 5424 |
| `n128-f4-reuse-i2048` | `0d4f4094889f61fe5d30874fd4e1e5c8aeb10bb2a7c88e9fa51cef83bafbeb73` | 230784;4/3/2/2 | 6232 → 6120 |
| `n64-f4-reuse-i2112` | `a1c24cb2a44b2b32cd860fa50b39eb099d597d9dd0f0c937be7f9ad39b7a792e` | 200320;5/3/3/2 | 5840 → 5720 |

Emitted checks:

- **Restored cumulative arithmetic:** C1 PTX477–492 and515–532 again starts from the preceding expert size plus63, performs normalization/correction and shifts the rounded quotient by6 into the data-prefix addition. N128 uses plus127 and shift7. The token-block prefix continues to add the separate cached count. This is the original Int32 expression and dependency structure. Some quotient shifts become logical before the final multiplication; their shifted-out high bits do not affect the final32-bit rounded data offset. No generic division or new dynamic configuration branch was introduced.
- **Retained signed phase specialization:** C1 PTX711–714 and1275–1278 still selects shift5/1 and mask31/1, using `shr.s32`. N64/full PTX914–933 and1593–1612 preserves signed `>>4`, `/28` floor correction and remainder; N128 has the same pattern. Partial I2112 still selects17/29 and retains signed division, negative-nonmultiple correction and remainder at901–911/1567–1577.
- **Retained epilogue bounds:** full-I variants retain token predicates without the feature2047 test. Partial I2112 retains its token predicate and `>2111` check at5350–5352. Full H256/7168 router clips remain absent; partial H7200 still has subtraction and max/min at5721–5724. The epilogue source is byte-exact to dd4, with no scratch/release/store-order edit.
- **Code size:** all four final SASS counts are lower after restoring the original expressions. This establishes that removing a source-level recomputation did not monotonically reduce native code. It does not establish the cause or size of a latency difference; that requires the separate matched measurement.

Exact sole `dsl/*.ptx` SHA256s in table order:

- C1: `838bd7c177dd2e408b8b380002f926665ab5e3d3b0ca9d31521b08c40b32156f`
- N64/full: `9a7bfe58d83eb3234a72e416947ac40d5d72ecc05e4f66c89a4e132f1eee24f5`
- N128/full: `fccbf69bed5b23da0caca5734592bdb6b22b637e8204e231e7d6b25b197ee7a5`
- N64/partial: `807f029a47fb4210061d1ef309d7d25e14a20de96db172d6296fff86e3c20a55`

Source/native/idle closure: `logs/cu132-recovery0911c-static-dims-padding-revert-native-closure-001.json`, SHA256 `d10c0f537a86e0405fb79006e0b33eee0d2552491491e26711227a7675441f39`. This separate review leaves `NATIVE_REVIEW002.md` and all dd4 evidence intact. No capture, comparator, test, validator or remote command was rerun by this reviewer.
