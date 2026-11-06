Fixed native winner crosschecks, T4 per-token. Positive is faster. All rows use 10 warmups and 100 CUPTI samples per phase.

| Model | Source at old winner | Source at new winner | New vs old winner on candidate | Native pair |
|---|---:|---:|---:|---:|
| v3 | +0.015% | +12.338% | -1.388% | -1.373% |
| kimi-k3 | -0.256% | +42.442% | -0.942% | -1.195% |

The selected-tactic change accounts for most of each decode loss. K3 also has a small source loss at the old winner. These diagnostics do not change the native pilot selections or replace any pilot result. All paired drifts are below 0.5%.

16 phases / 1,600 samples; raw evidence: `diagnostics-evidence/`. Archive SHA256 `c80384293b2c0218a3e449f7d2a5a6d374eb099e4a4981a0607ff086e45ce73e`.
