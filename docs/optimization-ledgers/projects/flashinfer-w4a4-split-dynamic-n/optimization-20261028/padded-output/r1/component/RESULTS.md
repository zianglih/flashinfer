R1 N3U T4 MXFP4x8 component attribution

|Topology|Source|PDL-on E2E us|Prepare us|FC2 us|Combine us|
|---|---|---:|---:|---:|---:|
|TP|control|36.416|3.264|16.881|4.384|
|TP|candidate|40.385|3.232|16.400|13.408|
|EP|control|35.408|2.943|18.464|3.104|
|EP|candidate|35.921|2.943|18.320|4.096|

All 1,600 strict CUPTI samples and final output bytes passed. Components use PDL off with ready inputs; their times must not be added to the overlapped E2E. Same frozen winner, routing and GPU. TP output allocation adds5,406,720bytes; EP adds3,899,392bytes. The measured decode loss is in inverse-mapped combine, not FC2 bulk-tail code (both use N16). No new policy or production change is proposed.
