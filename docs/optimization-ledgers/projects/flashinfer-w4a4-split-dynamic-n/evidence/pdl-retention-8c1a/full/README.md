# Paired PDL retention campaign

Frozen candidate `8c1a20173cf166b9fc279f6ae3ec5386250c5c5e` versus corrected control `aab93f854054de834447bdd8985b8bbd653fb3c8`, ordered C1 → T1 → A1 → A2 → T2 → C2. All 182 rows, source/config/observer hashes, per-token AUTO snapshots and routing histograms passed the recorded guards. Original a65 results were not rerun or pooled.

|Comparison|Decode|Prefill|Overall|
|---|---:|---:|---:|
|nvfp4_vs_control|1.022727×|0.998799×|1.016145×|
|mxfp8_vs_control|1.008417×|1.013744×|1.009867×|
|mxfp4_vs_control|1.008362×|1.018723×|1.011177×|
|nvfp4_vs_trt|1.003372×|1.155006×|1.042634×|

Paired speedup is `sqrt(C1*C2/(A1*A2))`, or the analogous T1/T2 ratio. Above 1 favors the candidate. Geometric means exclude only token counts 1 and 2: 8 decode, 3 prefill and 11 overall points.

## nvfp4 full medians

|Tokens|C1 µs|C2 µs|A1 µs|A2 µs|C1/A1|C2/A2|Paired speedup|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|27.2640|27.4240|25.6325|25.8880|1.063650|1.059333|1.061489|
|2|35.9040|36.0640|34.0325|34.4160|1.054992|1.047885|1.051432|
|4|48.8165|48.7840|47.0085|47.6480|1.038461|1.023842|1.031125|
|8|63.5845|63.5360|61.8080|61.2965|1.028742|1.036536|1.032632|
|16|73.3450|73.4080|72.0320|71.8090|1.018228|1.022267|1.020246|
|32|106.1285|106.9440|104.1920|103.9360|1.018586|1.028941|1.023750|
|64|139.9205|140.0970|136.4960|137.7125|1.025089|1.017315|1.021194|
|128|143.2960|143.3450|140.2570|140.7205|1.021667|1.018650|1.020158|
|256|152.9440|152.8160|150.4330|150.1445|1.016692|1.017793|1.017242|
|512|155.3450|155.1205|152.7365|152.9605|1.017078|1.014121|1.015599|
|4096|202.9770|202.7845|202.5290|202.2250|1.002212|1.002767|1.002489|
|8192|302.4500|302.0175|303.6660|305.0250|0.995996|0.990140|0.993064|
|16384|482.0020|485.9380|483.8260|483.2660|0.996230|1.005529|1.000869|

## mxfp8 full medians

|Tokens|C1 µs|C2 µs|A1 µs|A2 µs|C1/A1|C2/A2|Paired speedup|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|33.9840|33.8880|33.4240|33.3760|1.016754|1.015340|1.016047|
|2|48.9760|48.9760|48.0960|48.3045|1.018297|1.013901|1.016097|
|4|71.2320|71.2315|70.0645|70.0170|1.016663|1.017346|1.017004|
|8|96.0960|96.1445|94.4325|94.5760|1.017616|1.016585|1.017100|
|16|113.2480|114.3370|112.5765|112.5770|1.005965|1.015634|1.010788|
|32|170.0800|170.1120|169.2480|169.6330|1.004916|1.002824|1.003869|
|64|227.6160|227.5525|227.6010|227.6005|1.000066|0.999789|0.999927|
|128|234.1770|234.5285|232.1765|232.5765|1.008616|1.008393|1.008505|
|256|249.5210|249.4725|247.4250|248.0330|1.008471|1.005804|1.007137|
|512|252.4330|252.5610|251.4730|251.9370|1.003818|1.002477|1.003147|
|4096|322.1610|319.9850|321.0725|320.7210|1.003390|0.997705|1.000544|
|8192|476.6250|475.0095|447.6020|450.0815|1.064841|1.055386|1.060103|
|16384|791.3140|793.5695|784.0670|830.1950|1.009243|0.955883|0.982201|

## mxfp4 full medians

|Tokens|C1 µs|C2 µs|A1 µs|A2 µs|C1/A1|C2/A2|Paired speedup|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|31.0725|30.5120|29.9525|29.9365|1.037393|1.019224|1.028268|
|2|36.4165|36.7045|35.6005|35.5840|1.022921|1.031489|1.027196|
|4|52.3520|52.2880|51.6160|51.6645|1.014259|1.012068|1.013163|
|8|69.1520|69.1205|67.8720|67.9040|1.018859|1.017915|1.018387|
|16|76.0960|76.1275|75.4240|75.4250|1.008910|1.009314|1.009112|
|32|113.0885|112.8645|111.8720|111.9840|1.010874|1.007863|1.009367|
|64|149.9520|150.1120|148.7050|148.6085|1.008386|1.010117|1.009251|
|128|153.4880|153.5365|153.3610|153.2160|1.000828|1.002092|1.001460|
|256|161.3445|161.2485|160.3045|160.4170|1.006488|1.005183|1.005835|
|512|164.3360|164.3045|164.2400|164.2565|1.000585|1.000292|1.000438|
|4096|260.6090|260.0165|258.8970|258.8650|1.006613|1.004448|1.005530|
|8192|432.2570|430.4020|429.8890|428.6730|1.005508|1.004033|1.004771|
|16384|806.0340|803.9695|779.8910|758.8340|1.033521|1.059480|1.046420|

## Native TRT NVFP4 on the same GPU

|Tokens|TRT T1 µs|TRT T2 µs|NV A1 µs|NV A2 µs|T1/A1|T2/A2|Paired speedup|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|23.4080|23.4880|25.6325|25.8880|0.913216|0.907293|0.910249|
|2|36.5605|36.5445|34.0325|34.4160|1.074282|1.061846|1.068046|
|4|47.8085|47.8240|47.0085|47.6480|1.017018|1.003694|1.010334|
|8|62.0165|61.8730|61.8080|61.2965|1.003373|1.009405|1.006385|
|16|72.3520|72.3530|72.0320|71.8090|1.004442|1.007576|1.006008|
|32|103.0245|102.7045|104.1920|103.9360|0.988795|0.988151|0.988473|
|64|138.2260|138.3050|136.4960|137.7125|1.012674|1.004302|1.008480|
|128|139.1690|139.3450|140.2570|140.7205|0.992243|0.990225|0.991234|
|256|150.0645|150.0490|150.4330|150.1445|0.997550|0.999364|0.998457|
|512|155.6330|155.5525|152.7365|152.9605|1.018964|1.016946|1.017954|
|4096|213.3130|213.4095|202.5290|202.2250|1.053247|1.055307|1.054276|
|8192|346.5300|346.6580|303.6660|305.0250|1.141155|1.136490|1.138820|
|16384|620.2280|620.8835|483.8260|483.2660|1.281924|1.284766|1.283344|

## Repeat drift

|Arm pair|Decode second/first|Prefill second/first|Overall second/first|
|---|---:|---:|---:|
|nvfp4 C2/C1|1.000801|1.001919|1.001106|
|nvfp4 A2/A1|1.001421|1.000602|1.001197|
|mxfp8 C2/C1|1.001475|0.997561|1.000406|
|mxfp8 A2/A1|1.001142|1.020744|1.006451|
|mxfp4 C2/C1|0.999669|0.996958|0.998928|
|mxfp4 A2/A1|1.000204|0.989942|0.997395|
|TRT T2/T1|0.999516|1.000626|0.999818|

Ratios above 1 mean the second sweep was slower. These are descriptive repeats with fresh AUTO, not statistical significance or an isolated PDL-causality estimate. Saved tactic changes must be considered alongside these values.

## Scope and reproducibility

NVIDIA PyTorch `nvcr.io/nvidia/pytorch:26.05-py3`, B200-92, three independent single-GPU CuTe processes (NV GPU2, MX GPU3, mixed GPU4); native nondistributed TRT NVFP4 also GPU2. 10 warmups and 100 cold-L2 CUDA-graph CUPTI iterations per median; H7168/I2048/E256, 32 local experts, top-k8, simulated EP8/TP1. Routed preparation is inside the timed graph; input quantization, allocation, compile/tune and communication are outside. CuTe uses unfused finalization; TRT uses its native finalize. Per-tensor only.

The immutable config, commands, actual software versions, GPU UUIDs, source hashes, native-header identities, all medians and winner caches are in `raw/`. Original observers preserve medians, not the 100 individual timing samples. The separate five-point NV native gate preserved 9,000 samples and byte-exact checks; the full-grid campaign is performance evidence, not an expanded numerical test matrix.

Remote source is an independent Git repository with shallow boundary exactly aab; the same 8c1a commit was imported from the verified delta bundle. No alternate object store, remote recommit, source repair or cache-epoch switch occurred. See `scripts/pdl_retention_campaign/freeze-deploy-r2/receipt.json`.

## Conclusion and AUTO boundary

Both repeats improve NVFP4 decode versus corrected aab (1.023044× and 1.022410×); paired gain is 2.27%, with prefill near-neutral (0.998799×). NVFP4 is 1.003372× TRT on the included decode aggregate, but token counts 32/128/256 remain slower in both repeats; excluded token count 1 is also slower. This does not establish pointwise superiority over TRT.

[The exact AUTO audit](local-audit/tactic-full-audit-final.md) reconstructs all 182 measured-token cached selections. MXFP8 8K and mixed 16K consistently switch from control N128/logical-FC1-M512 to candidate N256/M256. MXFP8 16K stays on the same tactic in all four arms, yet candidate repeats vary 784.067→830.195µs. Mixed16K candidate 779.891→758.834µs also varies with its tactic unchanged. Preserve all rows; the cache does not provide losing-candidate timing margins or establish causality.

`independent-verification.json` rechecks all 262 archive files and 182 rows, source/environment/cache guards, chronology, histograms and every ratio. `repeat-geomeans.json` and `drift.json` preserve first/reverse aggregate results. No further benchmark variants or profilers were run.
