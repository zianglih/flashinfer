# Tiled SF preparation: rejected

The fixed128-row canonical SF atom ×32-word K chunk is slower than the frozen grid16 row-copy preparation in both orders. No full-chain execution/timing, profiler, or source integration followed this gate. The independent source copy remains unstaged.

## Raw preparation medians

| Order | Arm | NV8192 us | NV16384 us | MXFP8 16384 us |
|---|---|---:|---:|---:|
| forward | control0 | 19.1040 | 31.7760 | 49.1835 |
| forward | tile1 | 51.2320 | 58.9285 | 153.4720 |
| forward | control2 | 19.0395 | 31.7600 | 49.2480 |
| reverse | tile0 | 52.4480 | 59.3600 | 153.0880 |
| reverse | control1 | 19.4400 | 32.2565 | 49.2800 |
| reverse | tile2 | 51.4250 | 58.8000 | 154.8645 |

Bracket-arm means; latency ratio is tiled/control, so greater than1 is slower.

| Order | Mode | Tokens | Control us | Tiled us | Latency ratio |
|---|---|---:|---:|---:|---:|
| forward | nvfp4 | 8192 | 19.0718 | 51.2320 | 2.6863 |
| forward | nvfp4 | 16384 | 31.7680 | 58.9285 | 1.8550 |
| forward | mxfp8 | 16384 | 49.2157 | 153.4720 | 3.1184 |
| reverse | nvfp4 | 8192 | 19.4400 | 51.9365 | 2.6716 |
| reverse | nvfp4 | 16384 | 32.2565 | 59.0800 | 1.8316 |
| reverse | mxfp8 | 16384 | 49.2800 | 153.9762 | 3.1245 |

## Evidence and interpretation

- 72 CPU ownership/address cases pass. Actual-source CuTe compilation succeeded on the first attempt; no failed attempt was discarded.
- The6-check smoke and31-check bounded graph suite pass (31unique checks,37executions). They cover zero/grow/shrink replay, N16 extra16 rows, full128-row SF atoms, short/partial K chunks, arbitrary packed bits, poisoned invalid mappings, and capacity/end canaries.
- All18 timing rows preserve100samples and pass their own exact byte oracle and post-timing output hash. Original inputs, top-k IDs/weights and valid limits match across processes. Each native moe_sort execution has a different row permutation, so these are **not strictly matched fixed-permutation performance measurements** and prepared output hashes are not asserted equal across processes. All actual mapping hashes remain in the raw JSONs.
- NV original inputs also match prior full-chain harness hashes for logits, bias, quantized activations/SF and top-k results. The first archive validation caught the overstrong cross-process mapping assertion; its script/log remain under history/ and validation-first-attempt.log. This was not a GPU correctness failure.
- Same B200 GPU6 and nvcr.io/nvidia/pytorch:26.05-py3 environment, CUDA13.2/CuTeDSL4.7.1; the candidate native cache is unchanged. Each arm uses a private CuTe cache and fresh process. Source hashes/environment/commands/logs are retained.
- Timing uses10warmups/100cold-L2 CUDA-graph CUPTI samples. Standalone native DeepSeek routing and quantization occur before timing; N256, top-k8,32localexperts, hidden7168. No weights, FC1, or FC2 execute in this harness.
- Address analysis shows fewer destination sectors per full warp, but this does not establish lower measured HBM traffic. The tile has16,896B shared memory, two CTA barriers, and fewer live work items: NV8K360CTAs, NV16K616CTAs, MX16K308CTAs, versus a row-copy resident-grid bound of2368 on148SMs. These are plausible costs, not an NCU-supported causal diagnosis.
- No sanitizer or codegen/NCU profile was run for this rejected variant. The full MoE and per-token numerical contract was not revalidated; preparation leaves original mapping/per-token ownership unchanged.

[Design and replay commands](../../scripts/regular_tma_sf_tile_experiment/README.md); [validation receipt](validation-receipt.json). GPU6 was released idle.
