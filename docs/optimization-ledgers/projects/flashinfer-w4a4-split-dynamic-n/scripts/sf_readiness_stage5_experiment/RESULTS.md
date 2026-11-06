# Five-stage versus four-stage SF-readiness medians

Microseconds; each cell lists the six sequential ABA/BAB arm medians. Every arm contains100 cold-L2 graph/CUPTI samples after10 warmups. Ratios are geomean(control arm medians)/geomean(candidate arm medians). FC1 includes unchanged regular preparation; isolated phases are nonadditive.

|Variant|Tokens|Phase|Control / candidate / control / candidate / control / candidate (µs)|Control/candidate|
|---|---:|---|---|---:|
|stage5|32|full|106.0000 / 107.0880 / 106.1130 / 107.4400 / 106.2080 / 107.2320|0.989312×|
|stage5|32|fc1|66.3360 / 67.6795 / 66.3520 / 67.6160 / 66.9925 / 67.3280|0.985468×|
|stage5|32|fc2|35.4085 / 35.3920 / 35.4240 / 35.3125 / 35.3125 / 35.3280|1.001060×|
|stage5|128|full|144.0320 / 144.6560 / 144.1440 / 144.8160 / 144.2560 / 144.6085|0.996202×|
|stage5|128|fc1|90.3360 / 91.5040 / 90.5285 / 91.4240 / 90.8640 / 91.1845|0.991301×|
|stage5|128|fc2|47.7760 / 47.7760 / 47.7440 / 47.7280 / 47.8245 / 47.7600|1.000562×|
