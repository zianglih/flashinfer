# Physical N16 plus native16 bulk scatter

Independent unstaged source `flashinfer-fc2-physical-n16-bulk-review`, base0c1e00fc3e4f913c8c241796c70a29673737c542. The corrected native16 bulk donor is patch3d09bce11b296e205a93ee538c1080d6cb949feeb3877fce75b7a215acc793e4; combined candidate patch61430be0fb7cf618cad64d7c4f8c63c02a7765b49dbb9bb8568be4d5f07e2fc2. Three changed files, all unstaged, scoped pre-commit passed before freezing.

The older physical-N16 experiment narrowed NVFP4 FC1 and retained four operand stages. This candidate instead couples the existing native16 BF16/FP16 bulk scatter epilogue to a true16-row B tile and16-column accumulator. K tiles, roles, PDL, weight/activation cache priorities, canonical128-row SF atoms, and the capacity-derived stage calculation remain unchanged. No shape or model threshold is added.

A direct private `epilogue_token_granularity` constructor parameter defaults to32. The common host caller selects16 for output scattering without fused finalize or generated output SF, with BF16/FP16 output. The core rejects invalid granularity/output combinations. Physical allocation is `max(granularity, route_tile)`; TMEM accumulator base assumptions use `min(32, allocated_n)`. An actualN16 allocation requires a native16 bulk slab, preventing a fallback reader from accessing columns16–31. The resolved granularity is in the compile-cache tuple. FC1 resolves32; its numerical/ownership policy is unchanged.

The native16 slab needs4352 bytes of padded shared output (16×136×2); activation B alone saves4096 bytes per NV K512 stage when its physical rows shrink32→16. SFA/SFB publication remains canonical. Capacity calculations determine the final operand depth, rather than forcing five stages. TMEM window offsets can be16 aligned, so every accumulator-base alignment assumption is adjusted; logicalM512 still resolves32. Total TMEM allocation may shrink only when the remaining scale footprint permits a smaller hardware allocation.

Rejected after the fixed paired screen. Validation passed; the measured benefit did not justify retaining this implementation. All evidence is local. First gate r1 failed in the unchanged control because the copied layout-audit helper passed physicalM256 where the current constructor expects logicalM512; no numerical kernel ran. The helper-only fix is recorded in r2 and the source patch remains unchanged. The corrected gate checks180 actual layouts per source, and99 exact scatter cases covering six supported dtype/scale contracts, FP16/BF16 outputs, per-token scaling, partial token tiles, zero values, and forced wider native16 slabs to verify the offset correction.

The completed fixed diagnostic used V41 EP4 T32/128/512, N16/M128 for both phases, native10warmup/100cold-L2 CUDA-graph/CUPTI, PDL enabled, fused finalize disabled. Same-GPU C1 / bulk-A1 / physical-A1 / physical-A2 / bulk-A2 / C2 order separates the bulk epilogue effect from the physical allocation effect. The failed screen does not justify a V3/AUTO campaign or composition with retained mixed-FC1 overlap.

## Corrected gate result

R2 passed99/99 raw byte comparisons in128.65seconds, including all six supported dtype/scale contracts and the wider-slab offset checks. Both180-policy actual-layout audits pass, and all96 FC1 entries have identical policy/storage fields. There is no SF canonical-layout change; only the number of allocated operand stages can change their aggregate reserved bytes.

| V41 N16 FC2 | Operand K | Stages before→candidate | Actual SMEM before→candidate | TMEM before→candidate |
|---|---:|---:|---:|---:|
| NVFP4 | 512 | 4→5 | 197504→230016B | 128→128 |
| MXFP8 | 256 | 5→5 | 215936→199296B | 128→64 |
| MXFP4×MXFP8 | 256 | 5→5 | 215936→199296B | 128→64 |

The99-case probe uses smaller output-channel geometry. Its K2304 kernels report94→40 registers, zero local bytes and one active CTA/SM; full V41 H5120 specializations were independently queried during the fixed benchmark and are summarized below. The architecture per-block capacity is232448B. Current source and script receipts live in `evidence/fc2-physical-n16-bulk-r2`; the unchanged candidate source receipt remains in r1, alongside the failed helper-only attempt.

## Fixed screen and retention decision

Same GPU5 on B300 `hu-pdx-150`, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.78 and CuTe4.7.1. Each source used separate compiler caches; fresh native timing used the same fixed N16/M128 tactics and exact routes. The unaffected W4A16 column was preserved as a control and excluded from the decision. Final source checks confirm all83 recorded files unchanged in all three checkouts, empty staged diffs and no untracked files. The independent candidate remains unstaged; production was not changed.

| Format | Clean0c / bulk-only | Clean0c / physicalN16+bulk |
|---|---:|---:|
| NVFP4 | 1.001301× | 0.992761× |
| MXFP8 | 1.000718× | 1.000942× |
| MXFP4×MXFP8 | 1.001394× | 1.000256× |

These are geometric means over T32/128/512 of paired `sqrt(C1*C2/(A1*A2))`. PhysicalN16 slows all three NVFP4 points slightly and leaves MX formats effectively unchanged. The bulk-only comparator is also neutral. **Reject** this combined policy; retain the source and all raw results locally. These results are a bounded fixed-tactic diagnostic, not an AUTO retention campaign.

Actual full-model FC2 resource queries (`H5120/I2304`, BF16 scatter):

| Format | Variant | K/stages | SMEM bytes | Registers/thread | TMEM columns |
|---|---|---:|---:|---:|---:|
| NVFP4 | clean0c | 512/4 | 197504 | 90 | 128 |
| NVFP4 | bulk-only | 512/4 | 201344 | 54 | 128 |
| NVFP4 | physicalN16+bulk | 512/5 | 230016 | 54 | 128 |
| MXFP8 and mixed | clean0c | 256/5 | 215936 | 90 | 128 |
| MXFP8 and mixed | bulk-only | 256/5 | 219776 | 43 | 128 |
| MXFP8 and mixed | physicalN16+bulk | 256/5 | 199296 | 43 | 64 |

All actual specializations report zero local bytes and one active CTA/SM. FC1 resources are identical across the three variants. The physical architecture SMEM capacity is233472B, while the existing per-block capacity helper supplies232448B. Reducing output register use and B allocation did not produce a chain-level benefit, and capacity-derived NV depth5 increased total SMEM. No isolated attribution to stage depth is claimed.

Evidence: `evidence/fc2-physical-n16-bulk-r1-fixed/{summary.md,aggregates.json,resources-summary.json,source-final.json}` plus complete native outputs and resource observations under `raw/`. The source-independent instrumentation only queries compiled resources before native timing; compiler dumps are preserved under each run's artifact directory.
