# Nemo ReLU2 NVFP4 T16384 bounded result

All 45 collected hashes match. Both frozen sources and fixed native tactics/routes match; no AUTO or source mutation.

|C0 µs|A1 µs|A2 µs|C3 µs|Speedup|Control drift|Candidate drift|
|---:|---:|---:|---:|---:|---:|---:|
|574.884|581.397|578.052|574.180|0.991047×|−0.122%|−0.575%|

100 cold-L2 CUDAgraph CUPTI samples / ten warmups per leg, input quantization included, unfused public functional API. This is a measured 0.8953% prefill loss; no gain claim.

127,287,360 live payload/SF bytes per arm are exact after expanded-route canonicalization; unique/equal route IDs and expert ownership are checked. ReLU2 uses two 16-element max reductions: both depths8→3, registers102→100, non-NOP1724→1723, STACK/LOCAL zero. The candidate was rejected; the original simpler loop remains.
