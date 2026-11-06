# 04 integrated /1ad pre-producer-tail control /7dc fused input staging

Medians and MAD in µs; every row uses all 100 cold-L2 CUPTI rank-MAX samples after 3 warmups. Both controls are reused sealed same-node arms; no split MoE run.

| Tokens |04 median (MAD)|1ad median (MAD)|7dc median (MAD)|04/7dc|1ad/7dc|
|---:|---:|---:|---:|---:|---:|
|1|75.729 (0.848)|79.776 (0.768)|72.273 (0.975)|1.047812×|1.103822×|
|2|96.017 (0.720)|99.648 (0.880)|90.465 (0.672)|1.061366×|1.101514×|
|4|106.416 (0.879)|108.785 (1.104)|101.841 (0.912)|1.044928×|1.068185×|
|8|130.529 (1.185)|132.593 (0.943)|123.281 (0.880)|1.058793×|1.075535×|
|16|144.450 (1.168)|147.169 (0.992)|135.089 (1.424)|1.069291×|1.089423×|
|32|170.177 (1.040)|170.497 (0.880)|163.010 (0.737)|1.043970×|1.045930×|
|64|205.394 (1.152)|193.970 (0.880)|185.154 (0.704)|1.109317×|1.047620×|
|128|196.434 (0.752)|195.985 (1.072)|189.714 (0.911)|1.035424×|1.033058×|
|256|197.537 (0.896)|196.034 (0.624)|191.219 (0.913)|1.033046×|1.025183×|
|512|200.866 (0.784)|203.522 (0.641)|195.826 (0.785)|1.025737×|1.039300×|
|1024|221.986 (0.896)|221.587 (0.720)|222.755 (1.136)|0.996550×|0.994759×|
|2048|301.732 (2.272)|303.748 (1.825)|300.370 (1.424)|1.004533×|1.011244×|
|4096|459.796 (3.569)|471.781 (4.320)|467.492 (4.000)|0.983537×|1.009173×|
|8192|749.254 (13.232)|764.569 (18.769)|768.808 (11.825)|0.974565×|0.994486×|

8–8192 geometric ratios:04/7dc=1.029736980×;1ad/7dc=1.032833269×. Rows 1/2/4 remain shown and are excluded only from these aggregates.

Precomputed-routing public forward: staging, collective MegaMoE compute and deterministic integrated reduction; routing selection excluded.

One serial same-node BEFORE/AFTER pair does not cancel temporal drift. All100 samples are retained. MAD and quarter medians describe within-arm spread, not a causal confidence interval. Idle endpoints and recorded launch chronology are not continuous GPU monitoring.

| Tokens |04 AUTO N/return|1ad AUTO N/return|7dc AUTO N/return|
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

Full per-rank tactic dictionaries and 100-sample quarter trends are retained in the JSON. Mixed rank winners, if any, are listed together.
