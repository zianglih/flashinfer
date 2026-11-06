# Recent pilot iteration cost

Setup/postflight dominates these two small probes. The adjacent quantizer campaign took **126.33 s**, including six child processes totaling **49.45 s**. The CLC metadata campaign took **126.40 s**, including four child processes totaling **52.23 s**. No new timing measurement or remote/GPU action was performed for this audit.

| Wall-clock interval | Adjacent quantizer | CLC metadata |
|---|---:|---:|
| Native preflight and initial bookkeeping | 11.95 s | 12.44 s |
| Full source verification plus first idle query | 31.80 s | 31.33 s |
| Remaining initial idle gate | 1.60 s | 1.62 s |
| All exact/native child processes | 49.45 s | 52.23 s |
| Gaps between child processes | 4.01 s | 1.00 s |
| Postflight | 27.52 s | 27.78 s |
| **Total** | **126.33 s** | **126.40 s** |

The top-level receipt records process/controller start and finish times. The intermediate boundary is the original `native-preflight.json` write time preserved in each tar archive. Therefore the 12-second interval includes two Python import/Ninja-generation subprocesses, four Ninja dry runs, shared-library/Ninja hashes and bookkeeping; it is not a separately timed native-cache check. The 31-second interval includes both sequential 13,245-file SHA passes and the first idle query. Postflight similarly includes both full inventories, native hashes and release checking. These intervals are source-hash dominated by the controller's code path, but exact hashing-only duration was not instrumented. Total uses the receipt's `finished` timestamp, just before its final GPU-release query/write.

## Import, compile and exactness boundary

- Adjacent: six child processes take **7.69–9.14 s** each. Their saved native-capture write is **5.24–6.77 s** after process start; the exact-result write follows **0.885–0.911 s** later; teardown takes **1.40–1.55 s**. The first interval combines imports, tensor setup, compilation and native capture. The second includes graph replay, output/reference comparisons and serialization; it is not pure GPU execution time. There are no compile-start/end stamps to split them further honestly.
- CLC: four processes take **11.80–16.22 s**. Import/guard/setup before the test's explicit `started` timestamp is **4.43–4.49 s**; the test window is **6.24–10.23 s** and includes data/oracle setup, three native compiles/captures, kernel calls and comparison. Post-test exit takes **1.07–1.55 s**. Compiler artifact write times exist, but do not isolate compile time from setup/capture/execution.
- There is already only **one full source check per arm before and after the campaign**, not one before/after every case. Per-process guards cover 2 quantizer files or 71 CLC files. Removing repeated full checks inside cases is therefore not an available improvement here.

## Small safe improvement to try later

Run the two existing immutable-arm `verify(source)` calls concurrently with a **two-worker executor**, at both existing preflight/postflight boundaries. Keep each verifier's exact path list and SHA-256 calculation, wait for both futures, and propagate every missing-file/hash error before proceeding. Do not alter source manifests, their order/serialization, native checks, per-process guards or timing helpers. Do not reuse a cached digest across preflight/postflight.

This is orchestration-only and preserves all 52,980 file-hash checks per campaign. It targets roughly **59 s** of existing source-check/release intervals without changing evidence. A perfect two-arm overlap would save at most roughly **30 s** here; actual benefit is unmeasured and shared-storage contention may reduce it. It is preferable to inode-based digest reuse, which would add metadata assumptions for a small tool. Parallelizing the two independent CPU native-preflight subprocesses is a secondary option, but need not be bundled with the first change.

No active harness was modified. The [machine-readable audit](iteration-speed-adjacent-clc.json) binds both archived receipts/runners and retains every process interval. Existing sources, caches, records and raw qualification evidence remain unchanged.
