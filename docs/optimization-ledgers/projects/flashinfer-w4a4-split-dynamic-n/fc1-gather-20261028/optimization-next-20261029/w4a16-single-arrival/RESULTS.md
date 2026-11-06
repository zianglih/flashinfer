# W4A16 single B-stage arrival: full screen

Four Gather4 warp issuers share one full-stage byte-count owner; all four independently wait for reuse. Candidate is the source-bound unstaged single-arrival copy; control is frozen b361 W4 TMA cleanup, not PR head. Both use the same64-gather/96-decoder/144-epilogue quotas and activation cache hint. No tactic, payload layout, stage-count, PDL or FC2 change.

33 existing exact cases passed.32 cells use frozen tactics/routes and same-GPU C-A-A-C,100 strict-CUPTI cold-L2 samples per phase. GPU0 EP, GPU3 TP. CSV contains all four medians and both repeat spreads. Setup/collection failures were resolved before timing and are preserved separately.

| Model | Topology | 8 | 256 | 4096 | 16384 |
|---|---|---:|---:|---:|---:|
| v3 | EP8 | -0.47% | +0.04% | -0.69% | +1.71% |
| v3 | TP8 | +0.50% | +0.12% | -0.13% | +0.93% |
| v41-flash | EP4 | -0.10% | +0.14% | -2.91% | -0.41% |
| v41-flash | TP4 | -0.10% | +0.12% | -3.36% | +0.22% |
| kimi-k3 | EP8 | +0.41% | -0.12% | -3.33% | +0.09% |
| kimi-k3 | TP8 | +0.01% | -0.07% | -1.31% | +0.27% |
| nemo3-ultra | EP8 | -0.03% | -0.15% | -0.14% | +0.25% |
| nemo3-ultra | TP8 | +0.07% | -0.16% | +0.06% | -0.61% |

Aggregate geometric means:
```json
{
  "ep-decode": -0.048263905931578144,
  "ep-middle": -0.02202645146244242,
  "ep-prefill": -0.6901048196572224,
  "ep-all": -0.36316359631305417,
  "tp-decode": 0.12038786928010303,
  "tp-middle": 0.003279492947960705,
  "tp-prefill": -0.498908286646349,
  "tp-all": -0.21893974595637022
}
```

Decision: reject. Decode is effectively neutral and the prefill aggregates are negative. Several 4K observations have visible repeat drift, so the screen does not establish a reliable benefit from replacing four arrivals with one. Keep four independent producer arrivals; test static shared transaction accounting separately. All 112 runtime resource observations (56 gathered FC1) passed allocation guards with zero local bytes. No sanitizer was run.
