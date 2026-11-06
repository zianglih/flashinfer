# Future source verification: two immutable arms in parallel

The future-only controller is `validation/templates/paired-native/run.py` (SHA `d596d2c850e4782efb35ae3fb75af5c88c9665452273f472933d9309fc482561`). Recent probes copied the previous experiment's controller; the qualification owner confirmed that reuse path. The new template is now documented in `validation/templates/README.md` and `harness/README.md` as the next controller copy source.

The change adds one three-line wrapper using `ThreadPoolExecutor(max_workers=2)` and replaces the two existing sequential arm loops at preflight/postflight. `verify(source)` is unchanged. All native, exact/capture, resource, cache, process and receipt-writing bodies are unchanged. The template's output directory derives from its copied file location, preventing an accidental write to the old CLC evidence leaf. Inverse byte reconstruction of the original controller passes (`source-proof.json`, `template.patch`). Historical and active controllers were not edited.

## CPU-only measurement

The actual verifier functions were extracted from the template with AST, without executing its controller/GPU path, and applied to the existing sealed CLC source pair on `fi-gather-pipeline-resume-1030`. Every pass reads and hashes both 13,245-file inventories. No Torch/CUDA/compiler/native modules were imported.

| Pass | Seconds | Verified files |
|---|---:|---:|
| Serial warmup, excluded | 24.861 | 26,490 |
| Serial 1 | 27.830 | 26,490 |
| Parallel 1 | 15.472 | 26,490 |
| Parallel 2 | 15.292 | 26,490 |
| Serial 2 | 27.342 | 26,490 |

Median verification time falls **27.586 → 15.382 s**, saving **12.204 s per boundary (44.24%)**. Applying that difference to both existing boundaries would save about **24.4 s** per similar campaign. That is an extrapolation: no full qualification controller was rerun. Measurements used one warmup, then S-P-P-S, without dropping caches; two repeats per mode on one node/storage state are not a general filesystem throughput guarantee. Both modes use the same small result-recording lock for this comparison.

Every sorted path→actual-SHA record is byte-identical across all five passes (`observed-results.json`, SHA `068c99d449cb5fb26536b952e7e620a7da45001de6ee8c9540ae4ae655043a0d`). Wrong expected digests and nonexistent paths remain fatal for both execution modes. Failure checks changed only expectation dictionaries, never source files. Control/candidate source-record hashes match the previously sealed local archive.

`measurement.json`, `measurement.tar.xz`, `remote.log` and `check_parallel.py` preserve the raw timing/record evidence. No digest is reused between passes or between preflight/postflight; no inventory entry, source/cache check, or timing/qualification boundary was removed. Production c1ac remains clean; there was no GPU operation, source change or PR update.
