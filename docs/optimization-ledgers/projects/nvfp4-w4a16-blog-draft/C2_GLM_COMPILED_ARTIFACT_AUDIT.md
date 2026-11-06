# C2 GLM W4A4 compiled instruction audit

The B300 study completed successfully on 2026-10-08 at 23:15:28 UTC.
**Both split MoE and the exact historical T4096 MegaMoE configuration use
K64, despite compiling for `sm_103a`.** The matching B200 study targets
`sm_100a`. This closes the hardware-specific compiled-code check.

These are regenerated instruction artifacts, not new performance evidence or
retained binaries from the published timing campaign. The blog article was
not changed; the result belongs in supporting resources.

## Validated provenance

The source, submodule commits, original GLM workload diff, runtime package
versions and container image are identical across the two studies:
FlashInfer `b730d5f6f5929fe666b24b466144a57f5587ba4b`, CuTe DSL 4.7.1,
`nvcr.io/nvidia/pytorch:26.05-py3`. Each study has its own independent checkout.
The source/runtime guards passed before and after execution. The C2 wrapper
normalizes the explicit historical knob JSON arrays to native AUTO tuple
types, as already documented for C1; no kernel or benchmark source changed.

The final native supervisor returned 0. All 233 downloaded artifact files
present in the completion manifest match their hashes, the manifest binds the
final study receipt, and all six receipt-bound helper/workload/environment
files match. Full output remains at
`/data/home/ziangli/nvfp4-w4a16-blog-draft/glm-mma-study/c2`.
Selected evidence is local under
`evidence/glm5-mma-instruction-audit/c2/retrieved/`.
Both devboxes remain allocated.

The native setup compiled C++ routing/communication helpers before producing
the CuTe artifacts. Those helpers' architecture does not establish the main
MoE MMA choice; the conclusions below use the exported main kernels directly.

## Cross-hardware comparison

For each hardware, all eight ranks have byte-identical PTX/cubin/SASS for
all 13 main specializations: four split FC1, eight split FC2 and one Mega.
The 13 configurations match across hardware after excluding the actual
hardware `arch` field (`sm_100` versus `sm_103` in Mega metadata).

Every main PTX file is byte-identical across hardware after replacing only
`.target sm_100a` with `.target sm_103a`. No arithmetic, scale layout,
instruction descriptor or MMA instruction changes. The cubins and SASS are
not byte-identical: register allocation differs, and the MMA disassembly
uses `.4X` on B200 versus `.BLOCK16` on B300.

For the exact Mega artifact (`w4a4_megamoe/rank-0/compile-0002`):

| C2 artifact | SHA256 |
|---|---|
| PTX | `1c0189de66553df00cbd4f5f5055313894011eb51d7200dcba4cdea53d971db1` |
| cubin | `db24eb9e231bcb665a144a1e78b5b209150ccc66a11afa80d3baccdc595309cc` |
| SASS | `e522fd79d215df3be19c9fb18606f82c85dac9603a2d84a4100fdce9b3a836ae` |

The durable CPU comparison is
`evidence/glm5-mma-instruction-audit/compare_compiled_artifacts.py`;
its output is `cross-hardware-compiled-comparison.json`, with full configs,
targets and per-hardware hashes. Per-hardware `all-rank-artifact-consistency.json`
records all-rank equality. The script and Ruff checks pass.

## Descriptor confirmation

`c2/ptx-descriptor-audit.json` conservatively verifies all 48 split MMA
sites have bit 31 clear directly from their emitted unsigned-shift/mask
expressions, independent of TMEM address bounds.

Mega's four descriptor sites retain signed shifts. Their identical PTX body
means the C1 dataflow and installed-layout proof applies without modification:

- PTX line 2488 reads the TMEM base from the shared slot written by the
  512-column allocator at lines 2960–2963.
- The scale addresses use whole-column offsets 256/260/264/268 for SFA and
  272/276/280/284 for SFB, matching the actual installed DSL layouts.
- Valid physical TMEM addresses plus those offsets have no subword-ID high
  bits; both signed-shift terms vanish.
- The emitted dynamic-N formula matches the source expression for all 129
  valid token counts of the N128 tile. Its maximum is `0x10200480`.
- The four resulting descriptors feed PTX MMA sites 2762, 2799, 2836 and 2873.
  B300 SASS lines 2093–2171 retain the corresponding signed-shift and combine
  operations; lines 2230–2234 issue four `UTCOMMA.2CTA.BLOCK16` instructions
  using descriptor registers UR57/UR51/UR45/UR39.

Thus bit 31 remains zero for valid execution, selecting K64. This is a
combined actual-code and valid-layout proof; arbitrary malformed inputs to
the generic signed-shift helper are outside its scope. The supporting proof
is `c2/mega-ptx-valid-layout-proof.json`, bound to the B300 PTX hash and the
installed-layout query receipt.

The source audit establishes K96 is absent from AUTO rather than a candidate
that lost tuning. Binary regeneration confirms that result on both hardware.
It does not establish an epilogue bottleneck or replace the original
performance captures.
