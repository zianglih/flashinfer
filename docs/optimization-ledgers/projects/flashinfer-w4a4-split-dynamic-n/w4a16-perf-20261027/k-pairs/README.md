# Independent FC1/FC2 K trial

Control: native 46-tactic winning geometry and shared CLC flag, K256/K256. Candidate changes only the two K tilers. Public wrapper, 10 warmups,100 cold-L2 CUPTI CUDA graph samples, sameGPU6 CAAC. All72 timed outputs match their control bit hashes.

| Model | Tokens | FC1 K128 | FC2 K128 | Both K128 |
|---|---:|---:|---:|---:|
| v3 | 16 | 0.9539× | 0.9576× | 0.9151× |
| v3 | 4096 | 1.0024× | 1.0066× | 1.0104× |
| v41-flash | 16 | 0.9718× | 0.9816× | 0.9565× |
| v41-flash | 4096 | 0.9852× | 0.9891× | 0.9559× |
| kimi-k3 | 16 | 0.9364× | 0.9838× | 0.9273× |
| kimi-k3 | 4096 | 1.0094× | 1.0178× | 0.9358× |

Decision: reject AUTO expansion. Every decode point regresses; prefill gains are small and inconsistent across models. Keep46tactics and existing five FC1/FC2 topology pairs. This bounded trial does not exhaust every K/geometry combination. No repository changes were made for this experiment.
