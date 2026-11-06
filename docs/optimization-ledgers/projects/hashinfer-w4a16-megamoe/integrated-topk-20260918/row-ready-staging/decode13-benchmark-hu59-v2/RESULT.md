# Row-ready staging timing

**Status: rejected and unpromoted. Independent terminal audit passed.**

Decode 4–512 geometric speedup versus retained d01/A1: **0.941059×**, 0/8 rows faster. Every measured median, including all three prefill guards, is slower. This version does not justify its extra readiness orchestration.

| Tokens | Retained d01/A1 µs | Row-ready R1 µs | A1/R1 | MAD A1/R1 µs |
|---:|---:|---:|---:|---:|
| 1 | 65.6805 | 74.7210 | 0.879010× | 0.7355/0.8800 |
| 2 | 84.7690 | 91.1365 | 0.930132× | 1.0235/0.8955 |
| 4 | 94.7040 | 103.9360 | 0.911176× | 0.6550/1.1675 |
| 8 | 120.8970 | 126.3215 | 0.957058× | 1.0080/1.0405 |
| 16 | 134.5290 | 141.0895 | 0.953501× | 0.9600/0.6565 |
| 32 | 159.7930 | 168.1450 | 0.950329× | 0.6880/0.9920 |
| 64 | 182.9625 | 190.9135 | 0.958353× | 0.7035/0.7530 |
| 128 | 184.9770 | 199.0255 | 0.929414× | 0.8320/0.9600 |
| 256 | 191.0255 | 203.8740 | 0.936978× | 0.7205/0.7365 |
| 512 | 195.5375 | 209.6500 | 0.932685× | 0.9915/1.5520 |
| 4096 | 464.0205 | 486.1810 | 0.954419× | 2.7530/2.2555 |
| 8192 | 797.7025 | 846.0560 | 0.942848× | 26.0970/24.3040 |
| 16384 | 1530.8020 | 1544.2040 | 0.991321× | 49.9690/81.4730 |

Same hu-pdx-59 and boot dc868539-2ac3-4565-a1d9-3580f5164d0c; EP8/H7168/I2048/E256/K8, public forward, O3/AUTO4, deterministic unfused finalize. Exactly 100 cold-L2 CUPTI CUDA-graph rank-MAX samples per row after 3 warmups. All 13 tactics unchanged; N64/epilogue through 512 and N128/dispatch return for prefill. Tokens 1/2 visible but excluded from retention. Raw samples, quarters and rank tactics preserved in comparison.json.

All 104 finite, bit-exact cross-arm rank outputs and within-arm repeat checks passed. This is benchmark-output evidence, not full numerical or sanitizer qualification. No generated-code ordering or hardware overlap claim is made. Serial same-node control reuse admits temporal drift; particularly 8K/16K distributions remain visible, without trimming.

Retained source d01f074947d2cc754d6062c2b2ffe674e1577a34; actual R1 source4cd6162b73b94da4be1c3ace76d07cac0d95f8d1, manifest261b1dc106fc5655fd3d7466ec65756017fb6bfdc79ff52f7c0df89364141f13. Earlier d010c6 source/package was never staged or executed: source review caught a missing load dtype and the corrected freeze was measured.

Environment: nvcr.io/nvidia/pytorch:26.05-py3,8 B300 SXM6 AC,driver 590.48.01,CUDA 13.2 runtime,Torch2.12.0a0+5aff3928d8.nv26.05,CuTe 4.7.1,NVSHMEM 3.6.5,CUPTI 13.2; native compiler reports 13.3. Exact environment fingerprints retained.

Sealed remote evidence archive `5975d5efce18dc9f24452cf521bcef96d9a95d2f69fa71be88ea5a97f2a0d306` (342576482bytes). Closure epoch1789827342.771636: same boot, 104 source hashes, all owned groups absent, GPU empty. All 167 original member files are now verified locally, including eight SHA-identical serialized outputs from an audited content cache. Original gzip bytes were not downloaded or verified locally. Independent terminal audit passed: independent-file-timing-audit.json, SHA25609cd4189c0ebd1b97b165c37d259452d9e874c278ca983f078deaf3780fe94ba.
