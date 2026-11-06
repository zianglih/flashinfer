# Paired 4/6 error: final42 raw peer

Passed independent replay of all42 unique cells (24CuTe +18TRT),16,800 CUPTI spans,168 phase medians and672 clock quartiles. The two complete-job subsets retain all four CAAC phases; no pooling or replacement. All23 negative cells,22 exception quartiles and3 missing windows are retained.

Geometric aggregate: −0.225720%; CuTe −0.306214%; TRT −0.118292%. All188 captured GEMM resources match (LOCAL0), with one reused FC1 compilation in N3U TP. These are actual compilation records, not192 unique per-cell loads. The quantizer load/resource binding is not supplied by this GEMM-only performance guard.

Source inventories and original choices/routes remain fixed. Both arms reuse the same four native modules plus TRT binding76e15d66/Ninjaeadf6470. V3 TP32 is the sole recorded TRT default; its complete non-input-quant kernel sequence matches all400 iterations/four phases. Native timer/observer, cold-L2 graph policy,100 samples/10 warmups and CAAC estimator are unchanged.

| N3U TP CuTe | Speedup | Control spread | Candidate spread | Clocks |
|---|---:|---:|---:|---|
| T32 | -0.591208% | 0.401553% | 0.657550% | 2032MHz/reason0, complete |
| T4096 | -2.827503% | 0.097906% | 0.089970% | 2032MHz/reason0, complete |
| T16384 | -3.693679% | 0.053360% | 0.024354% | 2032MHz/reason0, complete |

At4K/16K, intermediate-quant exposed extension increases14.768/63.961µs, initial quant adds0.528/4.544µs, while FC1 extension changes−0.063/−0.047µs and FC2 extension−0.016/+0.449µs. FC2 launches earlier and overlaps the quantizer; its longer duration must not be interpreted as extra exposed compute. These measurements establish where the additional chain time appears, not its microarchitectural cause.

The tight, normal-clock N3U TP prefill regressions support the parent rejection. No repeated runs, shape-specific rescue or retained-source change. K3EP16K’s separate clock caveat remains in the prior six-cell peer.

All negative cells:

| Job | Backend | Tokens | Speedup |
|---|---|---:|---:|
| ep-kimi-k3-per-token | CuteDSL PER-TOKEN | 32 | -0.128400% |
| ep-kimi-k3-per-token | CuteDSL PER-TOKEN | 16384 | -0.669546% |
| ep-nemo3-ultra-per-token | TRTLLM PER-TOKEN | 4096 | -0.302068% |
| ep-nemo3-ultra-per-token | TRTLLM PER-TOKEN | 16384 | -0.478824% |
| ep-v3-per-token | TRTLLM PER-TOKEN | 32 | -0.014278% |
| ep-v3-per-token | CuteDSL PER-TOKEN | 4096 | -1.793415% |
| ep-v3-per-token | TRTLLM PER-TOKEN | 4096 | -1.137288% |
| ep-v41-flash-per-token | CuteDSL PER-TOKEN | 32 | -0.122031% |
| ep-v41-flash-per-token | TRTLLM PER-TOKEN | 32 | -0.493209% |
| ep-v41-flash-per-token | CuteDSL PER-TOKEN | 4096 | -0.789881% |
| ep-v41-flash-per-token | TRTLLM PER-TOKEN | 4096 | -0.417455% |
| tp-nemo3-ultra-per-token | CuteDSL PER-TOKEN | 32 | -0.591208% |
| tp-nemo3-ultra-per-token | CuteDSL PER-TOKEN | 4096 | -2.827503% |
| tp-nemo3-ultra-per-token | TRTLLM PER-TOKEN | 4096 | -0.148608% |
| tp-nemo3-ultra-per-token | CuteDSL PER-TOKEN | 16384 | -3.693679% |
| tp-nemo3-ultra-per-token | TRTLLM PER-TOKEN | 16384 | -0.277964% |
| tp-v3-per-token | TRTLLM PER-TOKEN | 32 | -0.011767% |
| tp-v3-per-token | CuteDSL PER-TOKEN | 4096 | -0.468523% |
| tp-v3-per-token | TRTLLM PER-TOKEN | 4096 | -0.604094% |
| tp-v41-flash-per-token | TRTLLM PER-TOKEN | 32 | -0.031651% |
| tp-v41-flash-per-token | CuteDSL PER-TOKEN | 4096 | -1.319109% |
| tp-v41-flash-per-token | TRTLLM PER-TOKEN | 4096 | -0.439756% |
| tp-v41-flash-per-token | CuteDSL PER-TOKEN | 16384 | -1.045074% |
