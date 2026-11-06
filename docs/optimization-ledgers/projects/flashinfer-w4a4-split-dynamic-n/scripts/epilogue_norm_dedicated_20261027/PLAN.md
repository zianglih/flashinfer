# Dedicated epilogue invariant normalization hoist

Final independent experiment on b85eff41 with the same six-field all-CLC policy in both arms. Only the dedicated epilogue block moves the optional norm scalar out of its tile loop. The inline implementation and alpha load placement remain original. This follows resource evidence: the broader hoist increased inline registers, while the public dedicated NV path removed a repeated LDG with registers78→68 for N16 and80→80 for N128.

There is no new argument or model/dtype/geometry branch. The existing dedicated-role block already separates its lifetime from input producer warps. The dependency wait precedes this load, norm is immutable across scheduled experts/tiles, and empty work can only read a valid optional scalar once.

Gate uses the existing source-paired graph replay harness: four formats, one/two CTA, N16/N128, PDL on/off, balanced/skewed/empty/reactivated routes. Config0 now enables the dedicated uniform-NV epilogue so the changed code is actually covered; config2 retains inline coverage. The codegen observer preserves PTX/SASS/resources for all16 pairs.

Then bounded fixed-native all-CLC CAAC across V3/V41/K3 at32,128,4096,16384, same public10/100 cold-L2 CUPTI methodology and NV initial activation quantization. W4A16 serves as unchanged control. No new upstream tests, no sanitizer or broad matrix, no source edits during gates/timings.
