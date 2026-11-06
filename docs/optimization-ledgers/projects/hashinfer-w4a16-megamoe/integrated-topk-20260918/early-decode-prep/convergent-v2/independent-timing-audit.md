# 04 integrated /53 early-reduce /364 early-decode

Medians and MAD in µs; every row uses all100 rank-MAX samples.

| Tokens |04 median (MAD)|53 median (MAD)|364 median (MAD)|04/364|53/364|
|---:|---:|---:|---:|---:|---:|
|1|75.729 (0.848)|78.624 (0.864)|86.241 (0.832)|0.878103×|0.911684×|
|2|96.017 (0.720)|99.441 (0.880)|96.641 (0.896)|0.993538×|1.028973×|
|4|106.416 (0.879)|108.913 (0.928)|116.801 (1.184)|0.911092×|0.932466×|
|8|130.529 (1.185)|119.969 (1.136)|131.329 (1.120)|0.993905×|0.913496×|
|16|144.450 (1.168)|142.657 (0.720)|144.577 (0.800)|0.999118×|0.986723×|
|32|170.177 (1.040)|170.642 (0.913)|169.010 (0.912)|1.006908×|1.009656×|
|64|205.394 (1.152)|193.842 (1.136)|197.571 (3.216)|1.039596×|0.981126×|
|128|196.434 (0.752)|195.537 (0.720)|192.162 (0.640)|1.022231×|1.017566×|
|256|197.537 (0.896)|196.945 (0.911)|197.010 (0.832)|1.002678×|0.999673×|
|512|200.866 (0.784)|202.482 (1.104)|202.833 (0.928)|0.990300×|0.998267×|
|1024|221.986 (0.896)|224.179 (0.927)|223.058 (1.136)|0.995194×|1.005023×|
|2048|301.732 (2.272)|301.651 (1.824)|305.395 (1.792)|0.988006×|0.987740×|
|4096|459.796 (3.569)|453.732 (3.615)|454.420 (3.391)|1.011829×|0.998486×|
|8192|749.254 (13.232)|752.870 (11.151)|762.521 (17.854)|0.982601×|0.987343×|

8–8192 geometric ratios:04/364=1.002818308×;53/364=0.989194080×. Rows1/2/4 remain shown and are excluded only from these aggregates.

Precomputed-routing public forward: staging, collective MegaMoE compute and deterministic integrated reduction; routing selection excluded.

One serial same-node BEFORE/AFTER pair does not cancel temporal drift. All100 samples are retained. MAD and quarter medians describe within-arm spread, not a causal confidence interval. Idle endpoints and recorded launch chronology are not continuous GPU monitoring.

| Tokens |04 AUTO N/return|53 AUTO N/return|364 AUTO N/return|
|---:|---|---|---|
|1|N128 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|2|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|4|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|8|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|16|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|32|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|64|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|128|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|256|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|512|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|1024|N64 / epi_warps|N64 / epi_warps|N64 / epi_warps|
|2048|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|
|4096|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|
|8192|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|N128 / reuse_dispatch_warps|

Full per-rank tactic dictionaries and100-sample quarter trends are retained in the JSON. Mixed rank winners, if any, are listed together.
