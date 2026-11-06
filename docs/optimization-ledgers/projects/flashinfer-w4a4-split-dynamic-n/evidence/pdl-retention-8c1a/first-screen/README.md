# First retention screen: frozen 8c1a versus corrected aab

All 91 rows passed provenance, timing-policy, cache, chronology and routing-histogram checks. This is one AUTO sweep per arm, before the separately authorized reverse sequence. Matching histograms do not prove exact route order or numerical equivalence; the five-case NV native gate supplies the separate byte-exact evidence.

|Comparison|Decode|Prefill|Overall|
|---|---:|---:|---:|
|nvfp4_vs_control|1.023044×|0.998142×|1.016191×|
|mxfp8_vs_control|1.008250×|1.025455×|1.012914×|
|mxfp4_vs_control|1.008632×|1.015132×|1.010400×|
|nvfp4_vs_trt|1.004328×|1.154992×|1.043352×|
|nvfp4_control_vs_trt|0.981705×|1.157142×|1.026728×|

Ratios are reference/evaluated latency, so above 1 favors the evaluated arm. Exclude only token counts 1/2 from geometric means; all 13 token rows remain below. No repeat drift or significance claim is available from this first screen.

|Tokens|NV C1 µs|NV A1 µs|TRT T1 µs|MX C1 µs|MX A1 µs|Mixed C1 µs|Mixed A1 µs|
|---:|---:|---:|---:|---:|---:|---:|---:|
|1|27.2640|25.6325|23.4080|33.9840|33.4240|31.0725|29.9525|
|2|35.9040|34.0325|36.5605|48.9760|48.0960|36.4165|35.6005|
|4|48.8165|47.0085|47.8085|71.2320|70.0645|52.3520|51.6160|
|8|63.5845|61.8080|62.0165|96.0960|94.4325|69.1520|67.8720|
|16|73.3450|72.0320|72.3520|113.2480|112.5765|76.0960|75.4240|
|32|106.1285|104.1920|103.0245|170.0800|169.2480|113.0885|111.8720|
|64|139.9205|136.4960|138.2260|227.6160|227.6010|149.9520|148.7050|
|128|143.2960|140.2570|139.1690|234.1770|232.1765|153.4880|153.3610|
|256|152.9440|150.4330|150.0645|249.5210|247.4250|161.3445|160.3045|
|512|155.3450|152.7365|155.6330|252.4330|251.4730|164.3360|164.2400|
|4096|202.9770|202.5290|213.3130|322.1610|321.0725|260.6090|258.8970|
|8192|302.4500|303.6660|346.5300|476.6250|447.6020|432.2570|429.8890|
|16384|482.0020|483.8260|620.2280|791.3140|784.0670|806.0340|779.8910|

NV decode is narrowly faster than TRT in aggregate, but T32/T128/T256 remain slower. NV8K/16K are about 0.4% slower than corrected-aab in this sweep.

Archive: `raw.tar.gz`, SHA256 `1ff4ea7d0ff238cc42eac2cdd47e071968f9da4f3ab9fc692fb7a44c1f6f90f3`; 150 extracted files verified against the remote manifest. `summary.json` SHA256 `0d82f5949ce0e94aa3514c532d11bd193df90bad2cb385a3bdd80d274acbc2c8`. Original a65 and previous-node TRT evidence are neither rerun nor pooled.
