# Row-outer Gather4 follow-up — reject

Reject this follow-up and preserve retained475. Moving the live row-group loop outside compile-time K chunks reduces redundant SHFL/control instructions, but does not produce a consistent general speedup. No source was committed or pushed. The inactive review copy is retired after verifying its exact patch/source receipts.

- Base retained475; patch `92af4b26bbe4957359ae16bb9bc86d9d3c91838648e085a25dfb58216d0d6090`, kernel `821b22521d662d8b1df770b6d40698fbf70a23fdb38ae0af402c9d0570f8a09b`. Only loop interchange beyond the rejected preceding experiment. SF, barriers, byte accounting, tactics and FC2 unchanged.
- Exact/codegen:23 tests passed;44 compiled kernels with zero local memory;21 FC2 cubins identical;14 FC1 cubins also identical to the preceding loop. Representative K8/N128 code has four fewer SHFLs, four fewer R2URs,23 fewer static instructions. Full gate evidence: `GATE_RESULTS.md`.
- Fresh C-A-A-C versus retained475, fixed tactics,100 strict-CUPTI cold-L2 graph samples per scope/phase,10 warmups. All12 phases complete:4,400 samples,24 guarded executable observations, zero local bytes. No search, clocks changed, sample filtering, or clock normalization.
- Same B300 GPU7 UUID `GPU-7bda223d-cb19-0578-d9d3-e925a359254b`, image `nvcr.io/nvidia/pytorch:26.05-py3`,CUDA13.2.1,CuTeDSL4.8.0. Persistent caches and exact source/route/input/tactic hashes preserved.
- N3U EP W4A4 uses its original N128/two-CTA K8/4 tactic. K3 EP prefill uses a fixed N128/two-CTA K8/4 diagnostic; decode is N16/two-CTA K4/4. The latter two are explicitly diagnostic tactics, not a new tuning axis or selected winners.

## Actual full chain

Positive means candidate faster. Control/candidate latency is the geometric mean of its two phase medians. Prefill T8192, decode T8.

| Case | Retained µs | Candidate µs | Change | Control spread | Candidate spread |
|---|---:|---:|---:|---:|---:|
| n3u-ep-w4a4-k8 | 415.076 | 420.725 | -1.343% | 0.131% | 0.113% |
| k3-ep-w4a4-k8 | 492.140 | 490.111 | +0.414% | 0.023% | 0.872% |
| k3-ep-decode-two-cta | 79.832 | 79.816 | +0.020% | 0.301% | 0.220% |

K3’s +0.41% result is smaller than its0.87% candidate repeat spread. N3U remains−1.34%; decode is neutral. Prefill geometric mean−0.47% is a bounded diagnostic summary, not the full benchmark scoreboard. The prior K-outer N3U screen was−5.41%; separate campaigns do not establish an exact causal K-outer→row-outer percentage.

## All diagnostic scopes

`runner_balanced` retains the production prehook. `runner_actual` uses saved actual routes with identical other inputs. `runner_full_tiles` deliberately concentrates all tokens into the first top-k local experts, fills tiles, and may substantially increase EP rank load; it is excluded from scoreboards.

| Case | Scope | Retained µs | Candidate µs | Change | C spread | A spread | C-A-A-C last/first quartile |
|---|---|---:|---:|---:|---:|---:|---|
| n3u-ep-w4a4-k8 | runner_balanced | 382.219 | 389.035 | -1.752% | 0.063% | 0.012% | +0.09%, +0.00%, -0.02%, -0.21% |
| n3u-ep-w4a4-k8 | runner_actual | 405.411 | 411.755 | -1.541% | 0.000% | 0.012% | +0.06%, +0.06%, -0.07%, +0.05% |
| n3u-ep-w4a4-k8 | runner_full_tiles | 2398.371 | 2436.462 | -1.563% | 0.080% | 0.015% | +1.47%, +0.99%, +1.17%, +0.60% |
| n3u-ep-w4a4-k8 | full_actual | 415.076 | 420.725 | -1.343% | 0.131% | 0.113% | -1.03%, -0.17%, -1.10%, -1.54% |
| k3-ep-w4a4-k8 | runner_balanced | 514.588 | 505.251 | +1.848% | 0.314% | 0.190% | +0.03%, +0.11%, +1.87%, +1.50% |
| k3-ep-w4a4-k8 | runner_actual | 471.220 | 472.652 | -0.303% | 0.177% | 0.017% | -0.50%, +1.73%, -0.53%, +1.30% |
| k3-ep-w4a4-k8 | runner_full_tiles | 2421.653 | 2500.275 | -3.145% | 1.852% | 0.172% | +7.92%, +5.14%, +5.04%, +6.18% |
| k3-ep-w4a4-k8 | full_actual | 492.140 | 490.111 | +0.414% | 0.023% | 0.872% | -1.23%, +1.20%, -0.21%, -1.28% |
| k3-ep-decode-two-cta | runner_balanced | 346.994 | 350.651 | -1.043% | 0.203% | 0.132% | +0.10%, -0.13%, -0.32%, -0.15% |
| k3-ep-decode-two-cta | runner_actual | 77.512 | 77.881 | -0.473% | 0.021% | 0.020% | +0.08%, -0.12%, +0.16%, +0.12% |
| k3-ep-decode-two-cta | full_actual | 79.832 | 79.816 | +0.020% | 0.301% | 0.220% | +0.44%, -0.64%, +0.20%, +0.12% |

## Clock qualification

Read-only10ms NVML sampling is coarse and may be stale. The envelopes below bracket CPU launches in CUPTI time, not individual GPU-kernel clocks. Mask4 is software power cap; its presence may reflect changed utilization as well as external variation. No iso-clock or normalized claim is made.

| Case | Phase | SM MHz sample counts | Reason masks |
|---|---|---|---|
| n3u-ep-w4a4-k8 | 0 control | {'1995': 5} | {'4': 5} |
| n3u-ep-w4a4-k8 | 1 candidate | {'1995': 5} | {'4': 5} |
| n3u-ep-w4a4-k8 | 2 candidate | {'1995': 5} | {'4': 5} |
| n3u-ep-w4a4-k8 | 3 control | {'1995': 1, '1987': 4} | {'4': 5} |
| k3-ep-w4a4-k8 | 0 control | {'1762': 6} | {'4': 6} |
| k3-ep-w4a4-k8 | 1 candidate | {'1755': 6} | {'4': 6} |
| k3-ep-w4a4-k8 | 2 candidate | {'1770': 5, '1980': 1} | {'4': 6} |
| k3-ep-w4a4-k8 | 3 control | {'1807': 6} | {'4': 6} |
| k3-ep-decode-two-cta | 0 control | {'2032': 2} | {'0': 2} |
| k3-ep-decode-two-cta | 1 candidate | {'2032': 2} | {'0': 2} |
| k3-ep-decode-two-cta | 2 candidate | {'2032': 2} | {'0': 2} |
| k3-ep-decode-two-cta | 3 control | {'2032': 2} | {'0': 2} |

## Evidence and conclusion

The two prefill dense stress scopes still regress1.56% and3.14%. Reusing coordinates removes a real redundancy, but the runtime live-group/shuffle design remains inferior as a general replacement. Avoid further loop permutations absent new evidence. Reduced announced payload bytes mostly avoid descriptor-OOB zero-fill/shared-destination work, not corresponding HBM activation reads.

Screen archive: 86 verified files, 1,974,646 compressed bytes, SHA `93fab9c64af92eca992dd08140c425db2243f82db2fe799c23a7d499f7122845`. `summary.json`, `runtime-guards.json`, and `screen-evidence/screen/` preserve every raw sample, phase/route/source receipt and clock trace. Candidate gate archive SHA `3c3f07b3cddde1d14f2e56e21a3b06e4d5e3df17cb966f03243722dbcf9e8093`.

Reproduce: `python3 fc1-gather-20261028/optimization-next-20261029/live-groups-row-outer/analyze_screen.py`. Remote sources and evidence remain immutable in persistent storage. GPU7 released; no further runs for this candidate.
