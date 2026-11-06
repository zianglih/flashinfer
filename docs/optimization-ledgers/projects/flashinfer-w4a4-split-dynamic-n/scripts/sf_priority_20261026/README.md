# Activation payload and scale-factor eviction priority — 2026-10-26

Private candidate at `0def601d6603df828ea39679b41ccbce64f7f09e`; one unstaged core file. Both activation-scale transports reuse the existing activation payload L2 policy. No new flag, dtype/shape policy, scheduling or barrier change.

The installed CuTe DSL `CopyG2SOp` supports only cache_mode; `CopyG2STrait` inherits an unpack method that ignores kwargs. The narrow path therefore uses four-byte inline `cp.async.ca.shared.global.L2::cache_hint`, preserving the existing valid ? 4 : 0 source-size and zero-fill contract. Wide SFB TMA already had the cache-hint qualifier but passed zero; it now receives the same activation policy.

[Official PTX cp.async documentation](https://docs.nvidia.com/cuda/parallel-thread-execution/#data-movement-and-conversion-instructions-cp-async) specifies the 64-bit cache-policy operand and requires `.L2::cache_hint`; the hint affects eviction priority, not memory consistency. Source size zero fills the destination. Current cp.async completion, publication fences and pipeline ownership remain unchanged.

The old `scripts/sf_cache_experiment` varied prefetch sizes 0/64/128/256 bytes on Gather4 and was neutral. It did not test eviction priority, so this regular-TMA candidate is distinct.

GPU7 on `fi-moe-nvfp4-port-1026`, c3/infra, image `nvcr.io/nvidia/pytorch:26.05-py3`; persistent native cache reuse under c3-20261026. No production source changes. Results pending.

## Narrow-path lowering obstacle

The first V41 NVFP4 N32 public profiler run compiles both cores but reports
`CUDA_ERROR_ILLEGAL_INSTRUCTION` after FC1 execution and before querying FC2
resources. There is no timing claim for this failed arm. The generated narrow
LDGSTS instructions refer to `desc[UR1]` without a definition of UR1, unlike the
control's initialized descriptor register pairs. This is a lowering observation,
not yet a minimized proof of a compiler defect.

The standalone `cp_async_probe.cu` validates 16 copied and 16 zero-filled words
for raw policy zero, raw `0x14f0000000000000`, and PTX `createpolicy` evict-last.
The created policy is exactly the same hexadecimal value. Thus the raw policy
encoding itself is valid. Reassembling the full failing PTX with external
ptxas 13.3.73 reproduces the suspect instruction form; switching to createpolicy
or the PTX ignore-src form also does so. No workaround is being added.

Removing only the narrow cache-hint qualifier/operand from captured FC1 PTX
reproduces all **2,976 control machine instruction words exactly**, proving the
inline copy without the hint retains the existing generated behavior. The
zero-fill validity and byte count have not changed. Files named `fc1-*` in
`evidence/` are CPU-only reassembly diagnostics, not benchmark variants.

## Wide-path codegen

V41 tokens4096 NVFP4 and MXFP8 both execute successfully with the modified
TMA-SFB policy. All four FC1/FC2 kernels keep identical instruction counts,
register counts (NV 80/112, MX 82/110), SMEM, one CTA/SM occupancy and zero local
memory or spill instructions. The actual TMA instruction descriptors change;
`wide-codegen-diff.json` and `resources.json` record the comparison against the
current saved-tactic control codegen.

## Bounded timing

Only wide route tiles N128/N256 are timed because the narrow candidate failed.
Existing K8 fixed diagnostic caches select geometry identically in C–A–A–C;
there is no production AUTO expansion and no new problem-specific policy.
Models are V3 EP8, V41-flash EP4 and Kimi K3 EP8, all at 4096 tokens.
NVFP4 includes the input quantizer and unchanged W4A16 drift control; MX tests
both MXFP4x8 and MXFP8. Fused finalize is disabled. The public benchmark's
10 warmups and 100 cold-L2 CUPTI-graph samples are unchanged. Receipts verify
source pins, routing identity, cache immutability and every 100-sample array.

`results.md` contains paired medians and `summary.json` retains individual
repeat medians. Performance results are fixed-geometry diagnostics, not retained
AUTO results or TRTLLM comparisons. Rigorous correctness/sanitizer testing is
not claimed. Parent may retain only the existing TMA policy-operand change if
these wide cases justify it; the narrow SDK copy remains unchanged in that case.

## Decision: do not retain

All six wide CAAC runs completed. The nine affected model/format results span
0.9989–1.0013x, with no useful repeatable gain. The unchanged K3 W4A16 drift
control also moved by 5.4%, so sub-percent K3 changes are not evidence of a win.
The narrow hint arm remains failed and no asm workaround is pursued. Keep
production unchanged; no TMA-only priority change is recommended. All GPU7
processes completed before handing the GPU to the next experiment.
