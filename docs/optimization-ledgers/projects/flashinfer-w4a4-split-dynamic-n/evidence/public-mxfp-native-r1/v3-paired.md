# v3 public API bounded native screen

Bounded native AUTO API migration screen on tokens4,32,128,512. Direct paired medians; no prefill/full-grid performance claim.

Exact route/GPU/source/method/runtime checks passed. Old assembly control and public API candidate use the explicit replay bridge.

## nvfp4/CuteDSL W4A16

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|55.040500|55.185000|54.753000|54.656000|0.997805x|
|32|110.945000|110.817000|111.169000|110.113000|0.995814x|
|128|148.481000|148.561000|148.209500|147.969000|0.998919x|
|512|160.385000|160.337000|160.385000|160.192500|0.999549x|

Four-point geometric mean: 0.998021x.

## nvfp4/CuteDSL W4A4

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|46.592000|46.624000|47.297000|46.624000|0.992519x|
|32|101.920500|101.936500|101.968500|101.904500|0.999608x|
|128|137.745000|137.985000|137.553000|137.761000|0.999885x|
|512|151.121000|151.425000|151.313000|151.313000|0.998996x|

Four-point geometric mean: 0.997747x.

## mxfp/CuteDSL MXFP8

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|70.240500|69.904500|70.465000|70.176500|1.000346x|
|32|167.714000|168.098000|169.201500|167.648000|0.994261x|
|128|229.986000|230.530000|231.202000|229.952000|0.996116x|
|512|250.834000|251.058500|251.106000|249.968500|0.997286x|

Four-point geometric mean: 0.997000x.

## mxfp/CuteDSL W4A8

|Tokens|C1 us|A1 us|A2 us|C2 us|Paired speedup|
|---|---|---|---|---|---|
|4|48.161000|48.096500|48.161000|48.448500|1.003653x|
|32|103.937000|103.969000|103.025500|103.008000|0.999761x|
|128|138.689000|138.449500|138.626000|139.472500|1.003916x|
|512|150.305000|150.593000|150.577500|150.240500|0.997925x|

Four-point geometric mean: 1.001310x.
