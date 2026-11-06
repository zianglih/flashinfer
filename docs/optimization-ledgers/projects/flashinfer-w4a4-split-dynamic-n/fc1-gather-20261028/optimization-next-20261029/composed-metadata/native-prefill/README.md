# Complete native prefill retune

The source is exactly retained `c0c0bc41c70100c694ac55585990971aba8b7fb9`
(kernel SHA256 `3225acf2dfeba54df42481b3186267b1bde642da9887b98cb966d5383d8635af`).
Remote execution reuses the immutable measured checkout at 7106 plus its
metadata patch; all 513 source hashes match the retained commit.

This campaign measures tactic selection, not a new source optimization. The
existing public autotune context is bounded to 4096, 8192 and 16384 tokens.
No tactic axes, ordering or admission rules are changed. The previous default
20-bucket search is deliberately not used. Native compiled caches and all nine
persistent C++ cache links remain available.

- 23 jobs cover 28 supported model/topology/dtype arms: V3 EP8/TP8, V41F
  EP4/TP4, K3 EP8/TP8 and N3U EP8/TP8; W4A4, per-token NVFP4, MXFP4x8 and
  MXFP8. Existing unsupported V41F TP MX and K3 MXFP8 arms are omitted.
- 84 prefill cells. W4A16 is unchanged and excluded from native search.
- GPUs 4/6/7, B300, CUDA 13.2, image `nvcr.io/nvidia/pytorch:26.05-py3`.
- Each job creates a fresh managed winner cache, runs native existing-tactic
  search, freezes that cache, then measures two native replay passes with
  100 strict CUPTI cold-L2 samples per cell and 10 warmups. NVFP4 includes the
  input quantizer; all outputs remain unfused.
- The old-winner control is the final-source AA from `../full-validation`.
  Reuse verifies identical source, GPU UUID, original sample hashes, routes,
  cache manifest and requested backend cells. There is no control rerun.
- Tuning-phase timings are excluded from retention. Final comparison uses
  16,800 new native-replay samples and 16,800 reused old-winner samples.
- The guard observes loaded-kernel register limits without changing compile
  options. Native search separately records host time at the `cute.compile`
  API and profiling calls; neither is a claim of pure backend compile time
  or pure GPU execution time.

`build_campaign.py` creates the hash-bound helpers; `prepare_remote.py` and
`launch_remote.py` deploy/launch them. `status_remote.py` reports progress.
Source changes remain frozen during this campaign. No sanitizer is run.

After verifying the evidence archive:

```sh
python3 fc1-gather-20261028/optimization-next-20261029/composed-metadata/native-prefill/analyze.py \
  fc1-gather-20261028/optimization-next-20261029/composed-metadata/native-prefill/evidence \
  --reference fc1-gather-20261028/optimization-next-20261029/composed-metadata/full-validation/evidence/perf \
  --output fc1-gather-20261028/optimization-next-20261029/composed-metadata/native-prefill/report
```
