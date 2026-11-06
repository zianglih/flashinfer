# Warp6 activation setup versus readiness in current saved native code

**Most meaningful setup is already hoisted. No additional patch is justified by this saved-code pass.** The current kernel7e's source calls the real readiness wait before `_activation_task`, but its generated code moves the descriptor-base load, GMEM view/tile coordinate and dynamic-N nonleader shift ahead of that wait. Seven small once-per-work setup instructions remain after readiness. They are a real residual window, not a deferred payload load or evidence of a material uncovered stall.

Reviewed only the current epilogue943f candidate captures at `profiles/fc1-post-scratch-release-raw5-fixed8-m256n{64,128}c2-001`. Both are five-WG, two-decode, REG96 with controlWG cap80, B3 and explicit S2; N64raw5/decoded3 and N128raw4/decoded2. No remote action, native compile, control recapture or source modification was performed. This updates the older B4 scheduling note using the actual current captures.

## Source and generated windows

Private `kernel.py:866–893` forms `real_b`, nonleader shift, MMA slice, TMA source/destination partition and mask. The source caller waits at1125–1127 (FC1 hook) or1142–1148 (FC2 done counter) before calling that helper. `custom_ext.py:438–480` builds the B view from already copied work metadata and the existing descriptor; it does not fetch activation payload. These definitions are the apparent candidate window.

| Geometry/phase | Setup already before readiness | Initial acquire LDG / retry loop | Residual setup | Free B-stage check | First B TMA |
|---|---|---|---|---|---|
|N64 FC1|0x5120–0x51b0|0x51d0 /0x5210–0x5250|0x5260–0x52c0|0x5300|0x5450|
|N64 FC2|0x5570–0x5600|0x5680 /0x56c0–0x5700|0x5710–0x5770|0x57b0|0x5900|
|N128 FC1|0x5040–0x50d0|0x50f0 /0x5130–0x5170|0x5180–0x51e0|0x5220|0x5370|
|N128 FC2|0x5490–0x5520|0x55a0 /0x55e0–0x5620|0x5630–0x5690|0x56d0|0x5820|

The descriptor-base `LDCU.64 UR10,...` is before the readiness branch in all four cases. `dynamic_mainloop.compute_non_leader_cta_load_shift` becomes conditional VIADD/shift/mask, then the B domain offset and tile coordinate are folded through IADD3/IMAD. FC1 tests the dispatch-ready count against valid tokens; FC2 tests the done count against32 for this fixture. The acquire loads and retry loops remain intact, and metadata `peek_ready` still skips the corresponding spin when already satisfied.

The residual seven instructions are exactly two R2UR, a64-bit uniform descriptor offset add/carry, a ULEA that combines the prepared row coordinate and partition offset, zeroing the K counter, and recomputing the CTA-leader predicate. N64's ULEA shift is5, N128's6. There is no residual GMEM descriptor or activation payload load in this seven-instruction window. The later per-K destination/coordinate setup and four TMA issues follow the free B-stage acquire; those are the established producer loop, not a missing setup-only hoist.

## Actual values and resource boundary

FC1 retains partition componentR3 and token coordinateR10 across readiness; FC2 retainsR3 andR11. Both retain the descriptor base inUR10/UR11. The FC1 retry changesR5/P0; FC2 retry changesR4/P0. Thus the meaningful address values already survive the blocking path. Afterward they move toUR8/UR19, form descriptorUR36/UR37 and initializeUR27. The leader predicate is recomputed because the readiness test reusesP0.

The displayed steady-state windows reference ordinary registers onlyR0–R11 (some names omitted), plus uniform registers throughUR37. That is an operand-name observation, not a full liveness measurement or proof of unused register budget. Warp6 shares the controlWG's fixed80 cap; current artifacts have no local accesses. A source restructuring that keeps prepared tensors/pointers across the spin could change uniform/GPR live ranges and lowering. There is no present spill evidence requiring such a change, and the high register names in other roles do not establish warp6 pressure.

Moving only source-level view construction above the hook would largely restate work the compiler already hoists. A narrower attempt to move the seven residual instructions could be legal, but these are integer/uniform bookkeeping with no new transfer started; source ordering alone does not establish a different schedule or benefit. This audit therefore recommends no new trial from this window and does not claim that every residual instruction is unmovable. Integration's independent lifetime/source note can use these actual PC boundaries without another capture.

Reviewed SASS identities:
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n64c2-001/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sass` SHA `ffd3839e28b677cad20a84284e4865e37f01d115e7d8f851fdff026ccd0ae2e9`
- `profiles/fc1-post-scratch-release-raw5-fixed8-m256n128c2-001/codegen/dsl/cutlass___call___flashinfermoe_epkernel_srccutedsl_megamoeshim_reuse512_compile_onlykernelSm100W4A16MegaMoEKernel_object_at__FakeTensorBFloat16div1div1i64div11_FakeTensorInt64div1d.sass` SHA `2517b1b37a181937abed99629958ac3b5a30e7e53dddbd3b4949910a9ff9ec53`
