# Five-stage readiness capacity audit

CPU-only review, 2026-10-25. **No material capacity-formula or ring-lifetime issue found for the gated compact specialization.** The native five-stage layout requires 216,064 bytes, leaving 16,384 bytes under the installed DSL's 232,448-byte SM100 limit. This establishes capacity feasibility, not a performance improvement.

## Source identity and scope

- Readiness control core: `0f570a27aec49f767b414b7e4fcc163433598b5d344cc8b86fb4114d9802f9d1`.
- Stage5 core: `c849d5aa71d6f33646c97868b5ba6374e7092997e384f8557288b217e55add84`.
- Both use unchanged utilities: `e14d3300a97fa508b0039065a6b29b876a0e14d20a5456ef18bf0a662c168274`.
- Independent AST comparison confirms the kernel function is identical between these two sources. Changes are the host stage selector, metadata estimate, and an actual `SharedStorage.size_in_bytes()` capacity assertion.
- [capacity-source.json](capacity-source.json) preserves source hashes, the exact read-only managed-Hai command, installed source excerpts and hashes, AST evidence, and arithmetic for 4/5/6 stages. No CuTe/CUDA imports, GPU launches, clone edits, or resource-helper execution were performed by this audit.

## Exact shared-memory accounting

The [selector](../../flashinfer-sf-readiness-stage5-review/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py) at 404–424 is gated by `self.sf_publisher`, which is the existing physical-N16 NVFP4 FC1 specialization. Its static extents are M128 / N16 / K512, one channel tile, two accumulator stages, and fixed 512-byte epilogue scratch. Every operand stage is 128-byte aligned, so no additional per-stage padding is needed.

| Allocation | Bytes per stage | Five stages |
|---|---:|---:|
| A payload |32768|163840|
| B payload |4096|20480|
| SFA |4096|20480|
| Compact SFB |2048|10240|
| Total operands |43008|215040|

`SharedStorage` at 855–887 reserves A, AB, SFA and relay barrier pairs: `(8*S + 2*acc_stages)*8` bytes. The two-slot published-SF ring reuses the relay allocation; no additional SF barrier array is required. Include all allocated relay and SFA-empty slots even when some are unused by this specialization.

For S=5, barrier bytes plus the 4-byte TMEM pointer are 356 bytes. Alignment places the 512-byte scratch at 384; it ends at 896. The 8-byte TMEM deallocation barrier ends at 904, and alignment places A at 1024. Thus:

```text
prefix(S) = align128((8*S + 2*acc_stages)*8 + 4) + 512 + 128
S=4: 4*43008 + 1024 =173056 bytes
S=5: 5*43008 + 1024 =216064 bytes; headroom16384
S=6: 6*43008 + 1152 =259200 bytes; exceeds capacity26752
```

The selector therefore chooses exactly 5 for this gate. The corrected metadata estimate at 797–800 includes the SFA barriers, and the actual layout assertion at 888–893 guards against divergence between the static estimate and generated storage. The previous readiness source's 6*S estimate undercounted 128 bytes at four stages; fixed FC1 scratch made that estimate irrelevant to its actual storage allocation.

## Installed capacity and generic ring behavior

Installed nvidia-cutlass-dsl 4.7.1 defines `SMEM_CAPACITY_MAP["sm_100"] = (228-1)*1024` in `cutlass/cutlass_dsl/cutlass.py:154`. File SHA256: `af21441236de2affbdb9fa3342d1eb33274d609a19031cb37e72f804c8f3ce5c`. `utils/smem_allocator.py:506` exports `get_smem_capacity_in_bytes` as `SmemAllocator.capacity_in_bytes`; lines 117–135 returns that table entry. The capacity does not come from `hardware_info.py`.

Installed `pipeline/helpers.py:880–907` advances the index and wraps when `index == stages`, then flips phase. It does not mask by `stages-1`; five stages are supported by this mechanism. Operand layouts at 695–720, source pipeline states, and source tails consistently use `self.num_stages`.

The TMEM SF ring remains independently two-slot. Source and publication states advance separately; no five-to-two divisibility is required. Publisher completion releases the shared SFA/SFB source lifetime only after both S2T copies; MMA releases payload storage and the TMEM SF slot only after their use. The explicit operand tail drains exactly `num_stages`, and the unchanged final whole-CTA barrier joins all roles before cleanup. Increasing source-buffer depth does not change these ownership rules, TMEM allocation, or thread roles.

## Earlier experiment and validation boundary

[small_b_experiment](../small_b_experiment/README.md) rejected coupled physical-B16 plus five stages on 98fd while retaining the N32 accumulator/epilogue. Its 36 arms passed byte checks, but whole-chain speedups were 0.991981x at T32 and 0.992374x at T128. It did not include compact SF, distributed issuers, or independent SF readiness; it was not a stage5-only result.

This audit does not claim the new refinement wins. The owner conducted the separate runtime screen and reported it negative; its exactness/timing receipts remain the authority for those results. The prepared resource helper was not executed by this reviewer.
