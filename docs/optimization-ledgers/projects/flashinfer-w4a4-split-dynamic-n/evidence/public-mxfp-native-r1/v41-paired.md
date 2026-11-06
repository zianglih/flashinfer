# v41 public API bounded native screen

Bounded native AUTO API migration screen on tokens4,32,128,512. Direct paired medians; no prefill/full-grid performance claim.

Exact route/GPU/source/method/runtime checks passed. Old assembly control and public API candidate use the explicit replay bridge.

## nvfp4/CuteDSL W4A16

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|41.728500|41.728000|41.744500|41.728000|0.999808x|
|32|138.065500|136.113000|136.257000|136.241500|1.007090x|
|128|280.034000|279.522000|279.522000|280.066000|1.001889x|
|512|325.074500|324.898500|325.010000|324.818000|0.999975x|

Four-point geometric mean: 1.002186x.

## nvfp4/CuteDSL W4A4

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|35.232000|35.247500|35.168000|35.216000|1.000462x|
|32|127.921000|128.113000|128.128500|127.681500|0.997506x|
|128|269.682000|269.394500|269.538000|269.890000|1.001187x|
|512|313.170500|312.995000|313.186000|313.090000|1.000127x|

Four-point geometric mean: 0.999819x.

## mxfp/CuteDSL MXFP8

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|51.984500|52.224000|52.112500|52.064000|0.997240x|
|32|216.578500|216.705500|217.202000|216.706000|0.998565x|
|128|473.222000|472.964000|473.012500|473.284000|1.000560x|
|512|552.549500|551.285000|551.733000|552.228500|1.001596x|

Four-point geometric mean: 0.999489x.

## mxfp/CuteDSL W4A8

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|37.120500|37.568000|37.553000|37.264000|0.990194x|
|32|126.161500|125.953000|126.034000|126.241000|1.001649x|
|128|263.315500|263.602500|263.794500|263.554000|0.999000x|
|512|307.091000|306.435000|306.531000|307.282000|1.002295x|

Four-point geometric mean: 0.998273x.
