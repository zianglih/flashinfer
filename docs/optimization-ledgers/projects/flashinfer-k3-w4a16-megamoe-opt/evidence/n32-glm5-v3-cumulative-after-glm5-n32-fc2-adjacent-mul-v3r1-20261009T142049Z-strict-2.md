# GLM5 EP8 incremental N32 study

Every column retains its source/runtime and all untrimmed samples in JSON. AUTO may select different tactics. Only T1/T2 are excluded from aggregate retention.

| Tokens | glm5-before-v1 µs; M/N/G/return; ×fresh866c | glm5-final-auto-v1 µs; M/N/G/return; ×fresh866c | glm5-n32-866c-control-v1r1 µs; M/N/G/return; ×fresh866c | glm5-n32-fc1-register32-v2r1 µs; M/N/G/return; ×fresh866c | glm5-n32-fc2-adjacent-mul-v3r1 µs; M/N/G/return; ×fresh866c |
|---:|---|---|---|---|---|
| 1 | 64.481; 256/64/512/epi_warps; 1.0206× | 66.769; 128/32/1024/epi_warps; 0.9856× | 65.808; 128/32/512/epi_warps; 1.0000× | 62.449; 128/32/512/epi_warps; 1.0538× | 65.873; 128/32/1024/epi_warps; 0.9990× |
| 2 | 84.833; 256/64/1024/epi_warps; 0.9717× | 84.481; 256/32/512/epi_warps; 0.9758× | 82.432; 256/64/1024/epi_warps; 1.0000× | 79.297; 256/32/512/epi_warps; 1.0395× | 82.513; 256/32/512/epi_warps; 0.9990× |
| 4 | 92.497; 256/64/1024/epi_warps; 0.9903× | 93.377; 256/32/1024/epi_warps; 0.9810× | 91.601; 256/32/512/epi_warps; 1.0000× | 93.889; 256/32/1024/epi_warps; 0.9756× | 93.713; 128/32/512/epi_warps; 0.9775× |
| 8 | 113.408; 256/64/1024/epi_warps; 0.9882× | 109.169; 128/32/512/epi_warps; 1.0265× | 112.065; 128/32/512/epi_warps; 1.0000× | 110.801; 128/32/1024/epi_warps; 1.0114× | 109.937; 128/32/1024/epi_warps; 1.0194× |
| 16 | 124.528; 256/64/1024/epi_warps; 0.9914× | 120.946; 256/32/512/epi_warps; 1.0208× | 123.457; 256/32/512/epi_warps; 1.0000× | 122.833; 256/32/512/epi_warps; 1.0051× | 120.705; 128/32/512/epi_warps; 1.0228× |
| 32 | 142.401; 256/64/512/epi_warps; 0.9865× | 143.249; 256/32/1024/epi_warps; 0.9807× | 140.481; 256/32/1024/epi_warps; 1.0000× | 140.802; 256/32/1024/epi_warps; 0.9977× | 142.994; 128/32/512/epi_warps; 0.9824× |
| 64 | 156.881; 256/64/1024/epi_warps; 1.0815× | 158.530; 256/32/512/epi_warps; 1.0702× | 169.666; 128/32/512/epi_warps; 1.0000× | 160.881; 256/32/1024/epi_warps; 1.0546× | 155.363; 128/32/512/epi_warps; 1.0921× |
| 128 | 165.665; 256/64/512/epi_warps; 0.9687× | 162.802; 256/32/1024/epi_warps; 0.9857× | 160.481; 256/32/1024/epi_warps; 1.0000× | 166.866; 256/32/1024/epi_warps; 0.9617× | 163.681; 128/32/512/epi_warps; 0.9804× |
| 256 | 169.761; 256/64/1024/epi_warps; 0.9701× | 155.793; 256/32/1024/epi_warps; 1.0571× | 164.689; 256/32/1024/epi_warps; 1.0000× | 164.578; 256/32/512/epi_warps; 1.0007× | 163.058; 128/32/512/epi_warps; 1.0100× |
| 512 | 172.817; 256/64/1024/epi_warps; 0.9663× | 165.890; 256/32/512/epi_warps; 1.0067× | 166.994; 256/32/1024/epi_warps; 1.0000× | 167.010; 256/32/1024/epi_warps; 0.9999× | 165.619; 128/32/512/epi_warps; 1.0083× |
| 4096 | 396.435; 256/128/1024/reuse_dispatch_warps; 0.9914× | 389.060; 256/128/1024/reuse_dispatch_warps; 1.0102× | 393.027; 256/128/1024/reuse_dispatch_warps; 1.0000× | 391.748; 256/128/1024/reuse_dispatch_warps; 1.0033× | 389.236; 256/128/1024/reuse_dispatch_warps; 1.0097× |
| 8192 | 662.869; 256/128/1024/reuse_dispatch_warps; 1.0066× | 657.639; 256/128/1024/reuse_dispatch_warps; 1.0146× | 667.255; 256/128/1024/reuse_dispatch_warps; 1.0000× | 656.470; 256/128/1024/reuse_dispatch_warps; 1.0164× | 660.679; 256/128/1024/reuse_dispatch_warps; 1.0100× |
| 16384 | 1232.413; 256/128/512/reuse_dispatch_warps; 1.0097× | 1229.966; 256/128/512/reuse_dispatch_warps; 1.0117× | 1244.351; 256/128/512/reuse_dispatch_warps; 1.0000× | 1241.760; 256/128/1024/reuse_dispatch_warps; 1.0021× | 1252.415; 256/128/1024/reuse_dispatch_warps; 0.9936× |

```json
{
  "glm5-n32-866c-control-v1r1": {
    "all11": {
      "speedup_vs_original_before": 1.00495021037342,
      "speedup_vs_fresh_866c": 1.0
    },
    "decode": {
      "speedup_vs_original_before": 1.007770036445829,
      "speedup_vs_fresh_866c": 1.0
    },
    "prefill": {
      "speedup_vs_original_before": 0.9974691881294209,
      "speedup_vs_fresh_866c": 1.0
    }
  },
  "glm5-n32-fc1-register32-v2r1": {
    "all11": {
      "speedup_vs_original_before": 1.0073126369672696,
      "speedup_vs_fresh_866c": 1.0023507896903385
    },
    "decode": {
      "speedup_vs_original_before": 1.008297665727101,
      "speedup_vs_fresh_866c": 1.0005235611917305
    },
    "prefill": {
      "speedup_vs_original_before": 1.0046905956171348,
      "speedup_vs_fresh_866c": 1.0072397298820392
    }
  },
  "glm5-n32-fc2-adjacent-mul-v3r1": {
    "all11": {
      "speedup_vs_original_before": 1.0142083585406516,
      "speedup_vs_fresh_866c": 1.0092125441356854
    },
    "decode": {
      "speedup_vs_original_before": 1.018883202214613,
      "speedup_vs_fresh_866c": 1.0110274818330356
    },
    "prefill": {
      "speedup_vs_original_before": 1.0018467040911998,
      "speedup_vs_fresh_866c": 1.0043886227403058
    }
  }
}
```
