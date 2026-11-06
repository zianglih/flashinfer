# All bounded producer-screen medians

Microseconds; each cell lists the six sequential ABA/BAB arm medians. Every arm contains100 cold-L2 graph/CUPTI samples after10 warmups. Ratios are geomean(control arm medians)/geomean(candidate arm medians). FC1 includes unchanged regular preparation; isolated phases are nonadditive.

|Variant|Tokens|Phase|Control / candidate / control / candidate / control / candidate (µs)|Control/candidate|
|---|---:|---|---|---:|
|distributed-tma|32|full|105.7280 / 106.2080 / 106.0480 / 106.4965 / 105.9840 / 106.1605|0.996535×|
|distributed-tma|32|fc1|65.9525 / 66.4320 / 66.2565 / 66.4000 / 66.5925 / 66.0800|0.999440×|
|distributed-tma|32|fc2|35.4075 / 35.2805 / 35.2960 / 35.3760 / 35.3760 / 35.3280|1.000896×|
|distributed-tma|128|full|143.4560 / 143.5200 / 143.2160 / 143.6480 / 143.6645 / 143.3445|0.999591×|
|distributed-tma|128|fc1|89.6960 / 90.5280 / 89.8885 / 90.4325 / 90.1760 / 89.8400|0.996163×|
|distributed-tma|128|fc2|47.8720 / 47.6965 / 47.7605 / 47.8400 / 47.7760 / 47.7760|1.000670×|
