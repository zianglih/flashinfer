# GLM5 EP8 incremental N32 study

Every column retains its source/runtime and all untrimmed samples in JSON. AUTO may select different tactics. Only T1/T2 are excluded from aggregate retention.

| Tokens | glm5-before-v1 µs; M/N/G/return; ×fresh866c | glm5-final-auto-v1 µs; M/N/G/return; ×fresh866c | glm5-n32-866c-control-v1r1 µs; M/N/G/return; ×fresh866c | glm5-n32-fc1-n16-v1r1 µs; M/N/G/return; ×fresh866c | glm5-n32-fc2-combined-v1r1 µs; M/N/G/return; ×fresh866c |
|---:|---|---|---|---|---|
| 1 | 64.481; 256/64/512/epi_warps; 1.0206× | 66.769; 128/32/1024/epi_warps; 0.9856× | 65.808; 128/32/512/epi_warps; 1.0000× | 66.561; 256/32/1024/epi_warps; 0.9887× | 66.560; 128/32/512/epi_warps; 0.9887× |
| 2 | 84.833; 256/64/1024/epi_warps; 0.9717× | 84.481; 256/32/512/epi_warps; 0.9758× | 82.432; 256/64/1024/epi_warps; 1.0000× | 80.049; 256/32/1024/epi_warps; 1.0298× | 79.105; 256/32/1024/epi_warps; 1.0421× |
| 4 | 92.497; 256/64/1024/epi_warps; 0.9903× | 93.377; 256/32/1024/epi_warps; 0.9810× | 91.601; 256/32/512/epi_warps; 1.0000× | 94.480; 256/32/1024/epi_warps; 0.9695× | 91.473; 128/32/1024/epi_warps; 1.0014× |
| 8 | 113.408; 256/64/1024/epi_warps; 0.9882× | 109.169; 128/32/512/epi_warps; 1.0265× | 112.065; 128/32/512/epi_warps; 1.0000× | 111.586; 128/32/512/epi_warps; 1.0043× | 109.729; 128/32/1024/epi_warps; 1.0213× |
| 16 | 124.528; 256/64/1024/epi_warps; 0.9914× | 120.946; 256/32/512/epi_warps; 1.0208× | 123.457; 256/32/512/epi_warps; 1.0000× | 118.881; 256/32/1024/epi_warps; 1.0385× | 122.305; 128/32/512/epi_warps; 1.0094× |
| 32 | 142.401; 256/64/512/epi_warps; 0.9865× | 143.249; 256/32/1024/epi_warps; 0.9807× | 140.481; 256/32/1024/epi_warps; 1.0000× | 141.729; 256/32/512/epi_warps; 0.9912× | 143.250; 128/32/512/epi_warps; 0.9807× |
| 64 | 156.881; 256/64/1024/epi_warps; 1.0815× | 158.530; 256/32/512/epi_warps; 1.0702× | 169.666; 128/32/512/epi_warps; 1.0000× | 159.202; 256/32/512/epi_warps; 1.0657× | 157.730; 128/32/512/epi_warps; 1.0757× |
| 128 | 165.665; 256/64/512/epi_warps; 0.9687× | 162.802; 256/32/1024/epi_warps; 0.9857× | 160.481; 256/32/1024/epi_warps; 1.0000× | 154.609; 256/32/512/epi_warps; 1.0380× | 164.066; 128/32/512/epi_warps; 0.9782× |
| 256 | 169.761; 256/64/1024/epi_warps; 0.9701× | 155.793; 256/32/1024/epi_warps; 1.0571× | 164.689; 256/32/1024/epi_warps; 1.0000× | 166.770; 256/32/512/epi_warps; 0.9875× | 163.857; 128/32/512/epi_warps; 1.0051× |
| 512 | 172.817; 256/64/1024/epi_warps; 0.9663× | 165.890; 256/32/512/epi_warps; 1.0067× | 166.994; 256/32/1024/epi_warps; 1.0000× | 169.090; 256/32/1024/epi_warps; 0.9876× | 168.226; 128/32/512/epi_warps; 0.9927× |
| 4096 | 396.435; 256/128/1024/reuse_dispatch_warps; 0.9914× | 389.060; 256/128/1024/reuse_dispatch_warps; 1.0102× | 393.027; 256/128/1024/reuse_dispatch_warps; 1.0000× | 394.052; 256/128/1024/reuse_dispatch_warps; 0.9974× | 391.956; 256/128/1024/reuse_dispatch_warps; 1.0027× |
| 8192 | 662.869; 256/128/1024/reuse_dispatch_warps; 1.0066× | 657.639; 256/128/1024/reuse_dispatch_warps; 1.0146× | 667.255; 256/128/1024/reuse_dispatch_warps; 1.0000× | 658.119; 256/128/1024/reuse_dispatch_warps; 1.0139× | 660.006; 256/128/1024/reuse_dispatch_warps; 1.0110× |
| 16384 | 1232.413; 256/128/512/reuse_dispatch_warps; 1.0097× | 1229.966; 256/128/512/reuse_dispatch_warps; 1.0117× | 1244.351; 256/128/512/reuse_dispatch_warps; 1.0000× | 1251.274; 256/128/512/reuse_dispatch_warps; 0.9945× | 1238.047; 256/128/1024/reuse_dispatch_warps; 1.0051× |

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
  "glm5-n32-fc1-n16-v1r1": {
    "all11": {
      "speedup_vs_original_before": 1.0126356006498032,
      "speedup_vs_fresh_866c": 1.0076475333773274
    },
    "decode": {
      "speedup_vs_original_before": 1.0176652899877834,
      "speedup_vs_fresh_866c": 1.0098189598659357
    },
    "prefill": {
      "speedup_vs_original_before": 0.9993442934550176,
      "speedup_vs_fresh_866c": 1.0018798629049517
    }
  },
  "glm5-n32-fc2-combined-v1r1": {
    "all11": {
      "speedup_vs_original_before": 1.0122508991988246,
      "speedup_vs_fresh_866c": 1.0072647268989492
    },
    "decode": {
      "speedup_vs_original_before": 1.0154697925830989,
      "speedup_vs_fresh_866c": 1.0076403900282895
    },
    "prefill": {
      "speedup_vs_original_before": 1.0037169791415415,
      "speedup_vs_fresh_866c": 1.0062636431144676
    }
  }
}
```
