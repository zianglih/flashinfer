# All bounded producer-screen medians

Microseconds; each cell lists the six sequential ABA/BAB arm medians. Every arm contains100 cold-L2 graph/CUPTI samples after10 warmups. Ratios are geomean(control arm medians)/geomean(candidate arm medians). FC1 includes unchanged regular preparation; isolated phases are nonadditive.

|Variant|Tokens|Phase|Control / candidate / control / candidate / control / candidate (µs)|Control/candidate|
|---|---:|---|---|---:|
|initial|32|full|105.7125 / 107.9520 / 105.9365 / 107.8720 / 106.0480 / 107.7445|0.981853×|
|initial|32|fc1|65.9530 / 66.6085 / 66.3045 / 66.8800 / 66.5440 / 66.4480|0.994320×|
|initial|32|fc2|35.2960 / 36.3365 / 35.3280 / 36.3840 / 35.3760 / 36.2400|0.972831×|
|initial|128|full|143.4085 / 145.9525 / 143.7125 / 146.0805 / 143.6965 / 145.9530|0.983633×|
|initial|128|fc1|89.3605 / 90.4640 / 89.9685 / 90.5920 / 90.0165 / 90.0965|0.993333×|
|initial|128|fc2|47.9040 / 49.2165 / 47.6800 / 49.3120 / 47.7765 / 49.1360|0.970852×|
|shared-empty|32|full|105.7920 / 107.8085 / 105.7290 / 107.7120 / 105.8560 / 107.5840|0.982274×|
|shared-empty|32|fc1|65.9360 / 66.6720 / 66.2085 / 66.6085 / 66.8480 / 66.3680|0.996700×|
|shared-empty|32|fc2|35.3600 / 36.2880 / 35.2960 / 36.2720 / 35.3285 / 36.3360|0.973263×|
|shared-empty|128|full|143.3120 / 146.2245 / 143.4880 / 146.2725 / 143.4565 / 146.1285|0.980920×|
|shared-empty|128|fc1|89.5840 / 90.4960 / 89.8565 / 90.5600 / 89.7765 / 90.2405|0.992335×|
|shared-empty|128|fc2|47.8400 / 49.2490 / 47.8565 / 49.2320 / 47.7285 / 49.2640|0.970760×|
