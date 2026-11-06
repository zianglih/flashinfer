# Retained N3U TP8 per-token FC2 and intermediate quantization

The current K640 quantizer is instruction intensive: issue activity is 78.74% with 18.31% DRAM throughput. Its actual native image contains two separate ordered scalar error4/error6 recurrences. Pairing those independent recurrences is a concrete instruction-removal candidate, now being qualified separately. This profile does not establish a speedup. FC2 exhibits metadata, scale-load and output-completion dependencies, but provides no evidence that an existing wait can safely be deleted.

## Scope and method

- Retained source: `c1ac8ce7341039db65195b99445fcdeb193cf226`, no overlay. The full 13,245-file inventory and 71-file process guard passed before and after both campaigns. No production source, compiler options, tuning choices or precision contract changed.
- N3U, TP8/EP1, 16,384 input tokens, 512 local experts, top-k 22, `cute-dsl-per-token`, initial quantization included. Frozen public tactic: `[256, [[128,256],[1,1],false], [[256,256],[2,1],false], [4,4], true]`. The final Boolean selects shared CLC. FC2 is M256/N256, two CTAs, K256, five operand stages, one accumulator stage, overlapping accumulators and 512 TMEM columns.
- One B300 per profile on recovery GPUs 0/1, C2 `fi-gather-pipeline-recovery-1030`; `nvcr.io/nvidia/pytorch:26.05-py3`, driver 595.91.07, CUDA 13.2, CuTe DSL 4.8.0. Runtime/cache receipts are included. The four persistent release C++ modules were Ninja no-ops and retained identical ELF/command hashes.
- NCU application replay of the complete public CUDA graph/PDL chain, exact selected kernel names, `--profile-from-start off --app-replay-match grid --clock-control none --cache-control none`. Five metric replays and four SourceCounters replays per target. Warmup and L2 flush remain in the existing runner. This is a diagnostic, not a new baseline timing campaign; NCU perturbs overlap and its durations must not replace CUPTI E2E results.
- Existing alpha-screen control CUPTI context has a 1,800.509 us E2E median in its first control phase. Intermediate quantization contributes a 446.467 us median extension of the running chain, and FC2 contributes 477.7155 us. These are extensions, not their overlapping kernel durations (466.163 and 525.748 us). No historical timing rows were changed.

## Actual row and native contract

The original public intermediate-quantizer invocation was observed passively; primitive metadata was copied to CPU only after `cudaProfilerStop`.

| Quantity | Observed value |
|---|---:|
| Allocated BF16 input rows × K | 491,008 × 640 |
| Device valid/padded prefix; processed rows | 426,752 |
| Logical live routed rows | 360,448 |
| Inactive rows within the processed prefix | 66,304 |
| Routing/SF row group | 256 / 256 |
| Grid / CTA threads | 2,368 / 64 |
| Registers / local memory / resident CTAs | 61 / 0 bytes / 16 |

The existing `row_limits` contract reads and quantizes only live rows; inactive processed rows clear their scale factors. Allocation capacity is not the amount of numerical quantization work. K640 comprises 40 real SF16 blocks: 64 threads participate in row-max reduction, with the extra threads rereading the last block for that reduction and masked from quantized output stores. The recipe is MSE 4over6, E4M3 max 256, error fast math enabled, base FP4 quantization fast math disabled; input is BF16. Literal row limits and live counts are retained in each `intermediate-invocation.json`.

FC2 uses 136 registers, 228,352 bytes dynamic shared memory, 256 threads and zero local memory. The reported launch grid `(16, 1918, 1)` includes CLC work reservations; it is not a statement that all logical CTA tickets execute independently.

## Aggregate metrics

| Metric | FC2 | Intermediate quantizer |
|---|---:|---:|
| NCU diagnostic duration (us) | 486.400 | 440.640 |
| DRAM read / write bytes | 522,847,488 / 1,446,068,736 | 462,753,280 / 156,215,552 |
| DRAM throughput (% peak) | 52.77 | 18.31 |
| L2 throughput / hit rate (%) | 44.01 / 43.87 | 10.41 / 16.42 |
| Instructions executed | 77,313,028 | 392,910,772 |
| Issue activity (%) | 14.25 | 78.74 |
| Long scoreboard (%) | 65.51 | 24.44 |
| Short scoreboard (%) | 5.76 | 6.96 |
| Barrier (%) | 11.11 | 4.72 |
| MIO throttle (%) | 0.21 | 0.02 |
| Math-pipe throttle (%) | 0.04 | 5.81 |
| Active warps / SMSP | 2.00 | 6.71 |
| Tensor activity (%) | 17.02 | — |

Metrics and PC counters come from separate diagnostic passes. In particular FC2's CLC execution count varies between them; their instruction totals must not be equated.

## Exact-PC attribution

All 3,248 FC2 and 768 quantizer instruction PCs match the actual loaded device ELF. Metrics and PC passes use identical device images. Sample counts below are warp observations, not percentages of time or estimates of removable overhead.

| Target / dependency | Native site | Sample evidence |
|---|---|---:|
| Quantizer BF16 row-load consumer | `0x7c0` after the two `LDG.E.128` at `0x7a0/0x7b0` | 7,211 long-scoreboard samples |
| Quantizer row-limit consumer | `0x380` after `LDG` at `0x370` | 627 long-scoreboard |
| Quantizer row-max CTA reduction | `LDS 0xa60`, following deferred barrier `0xa10` | 677 barrier |
| Quantizer shared-buffer reuse | `LDCU 0x2830`, following deferred barrier `0x2820` | 632 barrier |
| FC2 activation/weight/MMA metadata-ready consumers | branches `0x3530/0x1980/0x2b90`, full barrier offset `0x68` | 3,723 / 3,319 / 727 long-scoreboard |
| FC2 scheduler metadata-slot reuse | branch `0xe00`, empty barrier offset `0x70` | 3,523 long-scoreboard |
| FC2 per-token-scale/alpha multiply consumers | `0x4490/0x4260/0x44d0` | 2,037 / 1,425 / 422 long-scoreboard |
| FC2 accumulator-full / empty consumers | `0x3f30/0x1ce0`, barriers `0x50/0x58` | 680 / 652 long-scoreboard |
| FC2 epilogue join after store completion | `0xba10`, following barrier `0xba00` and `DEPBAR 0xb9f0` | 861 barrier |
| FC2 terminal CTA join | `EXIT 0xbb50`, following barrier `0xbb40` | 2,087 barrier |

The quantizer's two identified sites account for all 1,309 sampled barrier stalls. Its first row-load consumer accounts for 7,211 of 7,965 long-scoreboard samples. The native scoring section has two ordered scalar RN candidate-error chains and no FADD2/FMUL2; the separate paired-error experiment preserves each chain's order and must still pass exactness/resource checks. Neither these counts nor the 4.72% aggregate barrier metric alone justify a new row-ownership or CTA policy.

For FC2, `next_work` waits for metadata, copies it, immediately releases the slot, then advances its existing state. Producer/scheduler/epilogue dependencies can propagate through the one-stage metadata pipeline. The large samples at metadata branches therefore do not demonstrate excessive metadata instructions or a removable barrier. The scale-consumer registers are traced to actual per-token-scale loads and the expert-alpha load; samples alone cannot distinguish which outstanding dependency dominates a multiply. Prior alpha-prefetch, scale-prefix, metadata-depth and terminal-wait leads remain closed. No new FC2 source change is proposed from this capture.

## Provenance, failures and completion

- FC2 actual cubin: `ea14f11c1877d052ddd30c01860bd0a0da7fbbfae7f069fa41aee9388e65b3a9`.
- K640 quantizer actual cubin: `ff00cf52bf25550ace511512220c9baf801c3cfd55d29524e6026c1cfec05ba0`.
- Quantizer normal disk-cache loading was preserved. Its exact installed `kernels_binary` ELF symbol was copied from the returned host object, then its device ELF extracted without recompilation. Cache-hit PTX is absent; `quant-640-ptx-reuse.json` separately binds source-correlation PTX from a preserved earlier fresh compile to the identical device image. Compile options were not changed.
- Earlier plumbing failures remain preserved: a fatbinary-versus-ELF extraction assumption; broad kernel filters that selected an initial quantizer/FC1 and are excluded from target metrics; and a post-profile JSON serialization error. The final successful exact-name passes above, rather than those failed attempts, support the report.
- `metrics-summary.json`, `pc-binding.json`, `pc-attribution.json` and both controller receipts bind raw archives, source, native resources, cache closure and route/tactic identity. Each raw `.ncu-rep`, CSV, loader object/native receipt and helper is retained. `gpu-release.json` verifies GPUs 0/1 idle and released. No more profiling or timing is requested by this report.
- The public CuTe quantizer also supplies the TRTLLM PER-TOKEN initial-activation stage. If the separate shared quantization-helper candidate survives, its whole-chain comparison must freshly measure both backends; this retained-source diagnostic does not change historical TRT denominators.
