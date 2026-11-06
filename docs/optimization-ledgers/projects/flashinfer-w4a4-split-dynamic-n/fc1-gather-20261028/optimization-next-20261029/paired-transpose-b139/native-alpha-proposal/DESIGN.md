# Apply gated activation before the token transpose

Closed after wider ledger search: this exact mechanism was already implemented and rejected. No source copy or GPU work was started. Do not combine into current R1 or repeat without a distinct mechanism.

Ordinary gated FC1 already activates native up/gate fragments and transposes the16-value result once. Per-token gated FC1 instead transposes both operands, obtains one scale per output-token lane, then activates. We can retain the existing 16x64 TMEM-load ownership, broadcast each native element's token alpha from lane=token, apply identical packed FP32 activation arithmetic, and transpose one result exactly like the ordinary gated path. This removes one full16x32 transpose without repeating the rejected all-native output/shuffle/quantization redesign. Output stores, BF16 intermediate rounding and standalone quantization remain unchanged.

The current native load has token=2*register_index+(lane//2)%2, corroborated by `_scale_pack_transpose`; each lane sees16tokens. Loadalpha in existing canonical lane=token form with the same valid-token mask/mapping and alpha multiply; sixteen shuffles supply native alpha pairs. Packed multiplication permits distinct scale for each element of a pair. Keep the exact alpha*scale rounding and activation operations. Finite/NaN/zero output behavior must remain bit-identical in the existing GPU tests. Do not mistakenly reuse the rejected native-Ld16x256 mapping, which has8tokens perlane.

A direct private behavior input such as optional canonical token-alpha lanes can let `_activate` select native shuffles at compile time while retaining scalaralpha for allothercallers, including ReLU2. No is_fc1 flag, model/dtype dispatch, new autotuneaxis or publicAPI is required. The principle is elementwise activation before ownership conversion; only varying token scales need broadcasting. Prefer a clean generic scale representation if it yields the same codegen.

Use R1's formal TMEMphasewaits. All initial reads complete before scratch overwrite; one fragment retains the full32x32 scratch rectangle. Existing accumulator release moves to after the single result transpose, matching the ordinary gated path; this is later than current per-token release (before activation), so the overlap tradeoff must be measured rather than assumed favorable. This delayed release is the principal risk alongside sixteen SHFL sites and register lifetime.

Gate actual PTX/SASS/resourcebudgets on narrow/wide,one/twoCTA,allgatedactivationcontracts; then existing exact cases before paired CAAC on allgatedperTokenmodel/topologycases. Nongated/per-tokenReLU2 remains a control unless a distinct proven design reduces its two output fragments. Do notextend immediatelytoall-nativeSF/outputpacking: that design already regressed.


## Prior evidence found

`scripts/per_token_single_transpose_20261026/{README.md,source.patch}` implements exactly this native-token scaling and single-result transpose, including identical token formula. `optimization-20261028/warp-polish/producers/next-audit/CLOSED_LEADS.md` records512coordinateassignments/16896expressionchecks/fiveGPUselectors; registersdecrease110→100(N16),107→96(N128),but16shufflesanddelayedrelease. V3/V41F/K3 publicCAAC ratios0.999513/0.997873/0.995208; rejected. Earlierlowerregisterpressuredoesnotjustifyrepeatingit now withoutnewmechanism.

Adjacent-warp SF32barrier64participants is also alreadyrejected: `optimization-20261028/warp-polish/epilogue/README.md`, overall−0.094%,decode−0.003%,prefill−0.230%. No new review copy. The current activepairedtranspose keeps allpairfragments/earlyreleaseinstead ofcomputingactivationearlier, so isdistinctfromtheseleads.
