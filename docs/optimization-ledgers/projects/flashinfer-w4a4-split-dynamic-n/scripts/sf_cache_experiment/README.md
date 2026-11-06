# SFB cp.async prefetch hints

Frozen source: `7829fc00dc7121341cc40cd4190660507e006490`. Isolated modules only; no production changes retained.

The `_copy_tile` helper only serves SFB. The prototype replaces its CuTe copy with equivalent inline `cp.async.ca.shared.global` 4-byte transfers and adds optional L2 prefetch hints of64,128,256 bytes. Predicate/zero-fill and pipeline barriers are unchanged. A no-prefetch inline-PTX arm separates intrinsic lowering from the hint.

C1 B200 GPU3, `nvcr.io/nvidia/pytorch:26.05-py3`, native DeepSeek T16384, M256/N256 two-CTA tactic, NVFP4 without per-token, fused finalize disabled. Diagnostic phase measurements use10 warmups/100 cold-L2 CUDA graph CUPTI samples. These are not primary AUTO retention results. Complete output/SF bytes matched the frozen control before timing each variant.

| Variant | FC1 us | FC2 us |
|---|---:|---:|
| CuTe control |323.505|180.689|
| Inline PTX, no hint |324.065|180.8645|
| L2 prefetch64B |323.808|180.864|
| L2 prefetch128B |324.033|180.8005|
| L2 prefetch256B |324.065|180.7845|

All variants are neutral or slower; reject. Source snapshots and raw log/JSON are retained here. No baseline rerun was needed.
