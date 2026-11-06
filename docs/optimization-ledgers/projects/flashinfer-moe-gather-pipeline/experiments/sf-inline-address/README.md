# SF inline address formation: native stress probe

**Closed/rejected:** the single wide pilot compiled but had LOCAL48 versus current control LOCAL0. No candidate FC1 launch or timing. See [RESULTS.md](RESULTS.md); the patch and native failure remain preserved after review retirement.

Unstaged review: `flashinfer-sf-inline-address-review`, based on retained `c1ac8ce7`. Source `c631de18130fdafaa337e1e7be88b17faeb101d2e88dd453091b8e11c4021148` restores the rejected R2 coalesced ownership/Int32 row cache, then forms the signed 64-bit source address inside the existing side-effecting `_copy_gather_sf` assembly. There is no new helper, public argument, policy branch, register quota, compiler option, or pipeline operation.

The source pointer already includes the current channel offset. Two additional private parameters supply the Int32 row and constexpr full-width stride. `cvt.s64.s32` followed by `mad.lo.s64` preserves the former cast-before-multiply semantics without restricting supported strides. All R2 mapping, destination, issue/zero-fill and arrival expressions are unchanged; `source-proof.json` checks the inverse AST outside the existing helper/address/call.

This trades repeated address arithmetic for possible shorter live state. The failing N256/G2 case would ideally replace eight persistent offset words with four row words; it might also shorten simultaneous full-address temporaries. Neither is a measured register saving. Four stages recompute 16 row products instead of four, although native MAD may fold additions. Expected full-stage sector-request grouping is 2x for this case, not a reduction in unique sectors or DRAM bytes. Partial K, shared-bank effects and the unchanged Gather4 row-ID state limit the benefit; see `audits/sf-coalesced-lanes/INLINE_ADDRESS_FEASIBILITY.md` and `ADDRESS_REMATERIALIZATION_MEMORY.md`.

The only authorized pilot is the original MXFP8 N256/K8/G2 case (`case 10`, Relu2, static bounded scheduler, PDL on), with fresh current-source control and candidate on GPU2. The four existing capture/oracle/resource helpers are byte-identical to the preceding CLC pilot. The existing native LOCAL0 and role-register pool checks run before candidate launch. No remaining qualification or timing is authorized by this pilot.

R1 `86836355` and R2 `377f0404` failures remain immutable under `experiments/sf-lane-coalescing/`. This is a distinct native lifetime question, not a successful rescue claim.
