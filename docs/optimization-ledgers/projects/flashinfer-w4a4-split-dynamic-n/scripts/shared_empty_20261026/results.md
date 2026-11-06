# Shared operand empty ring: measured status

Candidate remains unstaged in `../../flashinfer-shared-empty-20261026`, based on control `0def601d6603df828ea39679b41ccbce64f7f09e`. No production change or push.

Recommendation: suitable as a synchronization simplification if retained by the parent. No material latency regression was observed. NV is effectively neutral; MX shows small consistent improvements. These sub-percent changes do not close the TRTLLM performance gap and should not be presented as a major speedup.

## Validation

- Source-paired 114 exact graph replays across 19 configurations: changing activations/routes, balanced/skewed/no-local routes, PDL on/off, one/two CTA, narrow/wide SF, inline/overlap, CLC/static, all three formats plus per-token NVFP4.
- All 76 compiled core variants have zero stack/local allocation and no local memory instructions. Actual SASS confirms one fewer UTCBAR for each emitted narrow mainloop copy; wide counts remain unchanged.
- Stage depths are unchanged; shared storage is unchanged in 64 variants and shrinks 128 B in 12.
- Follow-up M512/two-channel gate passed 12 additional exact replays (NVFP4 narrow overlap/CLC and MXFP8 wide inline/static, each PDL on/off). All eight core variants preserve stage depths and shared storage, have zero stack/local allocation, and retain the expected actual SASS commit reductions. Total bounded coverage is 126 exact replays and 84 core variants per source. No sanitizer/exhaustive claim.

## Public benchmark screens

B300 GPU7 on c3/infra, `nvcr.io/nvidia/pytorch:26.05-py3`, source-private CuTe caches and reused persistent verified C++ caches. Each row is control–candidate–candidate–control, with 10 warmups and 100 native cold-L2 CUPTI CUDA-graph samples per arm; the ratio uses medians of the two returned run medians. NV includes initial activation quantization, per-token preserves the benchmark recipe, and fused finalize is disabled. V41 standard NV/MX uses the recorded K8 fixed caches; V41 per-token and K3 use saved current native AUTO tactics with varying K and fail on cache miss. No new autotuning is included.

Full unrounded samples, source/cache/route hashes, constructor/stage diagnostics and commands are retained in `evidence/`; aggregate medians and run spans are in `timing-summary.json`. Unchanged W4A16 is a noise control; its V41 prefill control runs varied 7%, so that cell is not an optimization claim.

### fixed-native-kimi-k3-mxfp

| Tokens | Backend | Control us | Candidate us | Speedup |
|---:|---|---:|---:|---:|
| 32 | CuteDSL MXFP8 | 302.5768 | 301.9768 | 1.00199x |
| 32 | CuteDSL MXFP4x8 | 174.2970 | 173.6805 | 1.00355x |
| 64 | CuteDSL MXFP8 | 418.1210 | 417.3528 | 1.00184x |
| 64 | CuteDSL MXFP4x8 | 234.5290 | 233.9447 | 1.00250x |
| 128 | CuteDSL MXFP8 | 525.8015 | 525.0415 | 1.00145x |
| 128 | CuteDSL MXFP4x8 | 294.2083 | 293.1210 | 1.00371x |
| 512 | CuteDSL MXFP8 | 597.0260 | 595.3857 | 1.00275x |
| 512 | CuteDSL MXFP4x8 | 339.4335 | 337.8725 | 1.00462x |

### fixed-native-kimi-k3-nvfp4

| Tokens | Backend | Control us | Candidate us | Speedup |
|---:|---|---:|---:|---:|
| 32 | CuteDSL W4A4 | 177.4407 | 177.2165 | 1.00127x |
| 32 | CuteDSL PER-TOKEN | 188.3610 | 188.0085 | 1.00187x |
| 32 | CuteDSL W4A16 | 187.5923 | 187.8168 | 0.99880x |
| 64 | CuteDSL W4A4 | 241.6008 | 241.4330 | 1.00069x |
| 64 | CuteDSL PER-TOKEN | 252.9050 | 253.1447 | 0.99905x |
| 64 | CuteDSL W4A16 | 251.8888 | 252.5130 | 0.99753x |
| 128 | CuteDSL W4A4 | 299.6970 | 299.6008 | 1.00032x |
| 128 | CuteDSL PER-TOKEN | 316.1125 | 315.8890 | 1.00071x |
| 128 | CuteDSL W4A16 | 317.5528 | 317.0168 | 1.00169x |
| 512 | CuteDSL W4A4 | 342.7290 | 343.0888 | 0.99895x |
| 512 | CuteDSL PER-TOKEN | 379.7370 | 380.0173 | 0.99926x |
| 512 | CuteDSL W4A16 | 373.6410 | 373.9447 | 0.99919x |

### fixed-v41-flash-mxfp

| Tokens | Backend | Control us | Candidate us | Speedup |
|---:|---|---:|---:|---:|
| 32 | CuteDSL MXFP8 | 215.2962 | 215.0485 | 1.00115x |
| 32 | CuteDSL MXFP4x8 | 123.6645 | 122.9765 | 1.00559x |
| 128 | CuteDSL MXFP8 | 469.2817 | 467.7375 | 1.00330x |
| 128 | CuteDSL MXFP4x8 | 261.3768 | 260.6572 | 1.00276x |
| 4096 | CuteDSL MXFP8 | 586.9298 | 586.8422 | 1.00015x |
| 4096 | CuteDSL MXFP4x8 | 378.8252 | 378.7447 | 1.00021x |

### fixed-v41-flash-nvfp4

| Tokens | Backend | Control us | Candidate us | Speedup |
|---:|---|---:|---:|---:|
| 32 | CuteDSL W4A4 | 128.9765 | 128.5042 | 1.00367x |
| 32 | CuteDSL W4A16 | 136.3765 | 136.1043 | 1.00200x |
| 128 | CuteDSL W4A4 | 265.2967 | 265.4567 | 0.99940x |
| 128 | CuteDSL W4A16 | 279.5207 | 279.6408 | 0.99957x |
| 4096 | CuteDSL W4A4 | 349.6092 | 349.0730 | 1.00154x |
| 4096 | CuteDSL W4A16 | 581.4413 | 566.0335 | 1.02722x |

### fixed-v41-flash-per-token

| Tokens | Backend | Control us | Candidate us | Speedup |
|---:|---|---:|---:|---:|
| 32 | CuteDSL PER-TOKEN | 137.3202 | 136.9285 | 1.00286x |
| 128 | CuteDSL PER-TOKEN | 278.7050 | 278.7848 | 0.99971x |
| 4096 | CuteDSL PER-TOKEN | 448.4495 | 448.0253 | 1.00095x |
