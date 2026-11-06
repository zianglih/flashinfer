# C1 GLM W4A4 compiled instruction audit

The isolated B200 study completed successfully on 2026-10-08 at22:42:21UTC.
It confirms **K64 for the emitted split kernels and the exact historical
T4096 MegaMoE configuration**. Both PTX and cubin disassembly target
`sm_100a`. B300 code generation remains a separate pending study.

This is regenerated compiled-code evidence, not retained historical binaries
or a new performance result. The original GLM source and runtime were
reconstructed and verified before and after execution. The published latency
captures are unchanged.

## Provenance and scope

- FlashInfer `b730d5f6f5929fe666b24b466144a57f5587ba4b`, CuTe DSL4.7.1,
  `nvcr.io/nvidia/pytorch:26.05-py3`, eight B200s on C1 `b200-81`.
- Independent checkout/submodules; original GLM patch and exact resulting
  file hashes; canonical diff SHA256
  `8915b29d14bd3e25eae23905c489056a92477932864606e71bb69ecab2f45f2b`.
- T4096, D6144/E2048/N256/K8, EP8. Split native AUTO exported four FC1 and
  eight FC2 specializations. Mega used the recorded tile256/128/256,
  cluster2/1/1, flag batch4, epilogue batches2/4, group hint512,
  `atomic_counter`, `reuse_dispatch_warps`, and no in-kernel FC2 reduction.
- Native benchmark/driver and kernel code were unmodified. The compile wrapper
  requested PTX/cubin/SASS without adding optimization or line-info switches,
  preserved compile arguments and returned the original compiled object.
- Native explicit-knob JSON retains lists while AUTO supplies tuples. The
  wrapper normalizes only that exact CLI payload's three tuple-valued fields
  to match historical AUTO types. Per-rank receipts record this conversion.
- Split completed in attempt2. Mega was retried after the list/tuple setup
  failure; completed split outputs were retained. The failed attempt and its
  original helper receipt are archived. An earlier fresh-checkout packaging
  failure was also preserved; only standard project-local data symlinks were
  added. Neither failure produced valid Mega timing or a main Mega binary.
- Supervisor returncode0 and final source/runtime checks passed. Both devboxes
  remain allocated; C2 was untouched by this study.

Evidence root: `evidence/glm5-mma-instruction-audit/c1/`. The complete remote
study remains at
`/data/home/ziangli/nvfp4-w4a16-blog-draft/glm-mma-study/c1`.
`retrieved/` contains the final receipts, logs, all-rank compile manifests and
rank0 PTX/cubin/SASS.233 downloaded artifact files were checked against the
completion manifest, which also binds the final study receipt.

## Split: emitted masks independently clear bit31

`split-ptx-descriptor-audit.json` traces all48 block16 MMA sites across the12
main specializations. Every descriptor has bit31 provably zero from the
emitted constant/mask/unsigned-shift expressions, without relying on a TMEM
address bound. The small conservative checker treats unknown inputs as all
bits possible; it does not infer a zero bit from missing information.

Example `retrieved/artifacts/w4a4/rank-0/compile-0010.ptx`:

- Lines1558–1577: SFA extraction uses unsigned right1 then `&0x60000000`;
  SFB uses unsigned right26 then `&0x30`.
- Lines1735–1737: fixed format/M/N bits do not set bit31.
- Lines1745–1785: four finalized descriptors feed the four block16 MMA sites.
- Matching SASS lines1420–1430 contain four `UTCOMMA.2CTA.4X` instructions.

Fresh AUTO does not identify the old split winner, which was not logged.
This result covers all emitted native split specializations at this shape,
consistent with the separate source proof that K96 is absent from AUTO.

## Mega: actual signed shifts plus valid-layout proof

Main artifact: `retrieved/artifacts/w4a4_megamoe/rank-0/compile-0002`.
All eight ranks have byte-identical PTX, cubin and SASS:

| Artifact | SHA256 |
|---|---|
| PTX | `542208433529606266a5ffc37365ab517515efd93a9279c0a4935b05f20bafa1` |
| cubin | `b1b1844d41a2119218f483ba93c8314405c061bf904d146429aa2cfbd3ecc08d` |
| SASS | `aae20e8bb02eb39cb151b7607ca85103fff2d96bab15ee2af3143663e71cab08` |

PTX line2488 loads the TMEM base from shared address `[%r1+280]`; lines2960–2963
allocate512 TMEM columns into that same shared slot. Lines2551–2582 form the
four descriptors. The compiler **retains signed shifts**; it does not remove
the general helper's sign-extension possibility for arbitrary invalid pointers.

The actual operands advance whole TMEM columns:

- SFA: base+256,260,264,268.
- SFB: base+272,276,280,284.

This exactly matches the independent installed-DSL layout query: both scale
atom origins have E4M3 offsets0,16,32,48, or word offsets0,4,8,12.
Full-word base construction and these offsets leave the subword-ID bits zero.
The pinned TMEM pointer definition's physical mask is `0x007F01FF`; even this
conservative base upper bound plus284 is below `2^26`. Thus both emitted
scale-ID terms are zero despite their signed shift instructions.

The dynamic token term at PTX2544–2547 is:

```text
(((valid_tokens <<14) +245760) &0xeffc0000) |0x10000480
```

The native scheduler bounds `valid_tokens` to0..128 for this tile. Checking
all129 possible values reproduces the source expression
`0x10000480 | ((align16(valid_tokens)>>3)<<17)`; its maximum is`0x10200480`.
Therefore bit31 stays zero in all four final descriptors. They feed MMA sites
2762,2799,2836,2873. SASS retains signed `USHF.R.S32.HI` and combines the
corresponding descriptor registers before four `UTCOMMA.2CTA.4X` instructions
at SASS2230–2234.

`mega-ptx-valid-layout-proof.json` records the address/token assumptions,
actual emitted expressions and artifact hash. `MMA_DESCRIPTOR_REVIEW.md` and
`static-tmem-layout-query.json` independently establish the installed layout
for both native AUTO tiles, including N256. `all-rank-artifact-consistency.json`
confirms all13 main variants have matching hashes across all eight ranks.

The generic mask-only checker deliberately leaves the four Mega descriptors
unresolved: their proof requires valid TMEM and scheduler bounds. This keeps
the source/layout reasoning separate from an unconditional bit-mask proof.

## Interpretation

K96 was never a tuning candidate in these pinned implementations. The B200
regeneration confirms the actual K64 instruction selection and closes the
signed-shift concern for valid native layouts. The B300 export must still
verify its own target and descriptors. Neither this instruction audit nor
similar B200/B300 prefill latency establishes an epilogue bottleneck.
