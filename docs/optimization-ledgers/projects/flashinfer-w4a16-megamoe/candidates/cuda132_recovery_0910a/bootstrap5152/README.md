# Fresh 0910a bootstrap at published5152

Prepared successor of the existing0909e bootstrap/setup. Target is the exact clean commit `5152a9e7cf50c46b76719735d7269a28a4e01130`, source `c2675f51751cab84febe84e173ae3971cacd7fbe85b6ef8bcb9b8cd55c193ba7`, manifest `507e128b730d2e45b172e04b353b18cf09f11f07893123fc048f3e995574ed8e`. This clones the published commit and required submodules, with no tight-row overlay. It does not stage the dirty primary checkout or restore any historical cache.

Integration owns all transport/runtime work. From project `hai/`, use managed `/usr/local/bin/h` after verifying its path. The existing stage driver requires an absent checkout, accepts only new files or identical bytes, and verifies the complete handoff plus the four unchanged current source-provenance helpers. Run locally from the project root, with the actual handoff SHA:

```sh
python3 candidates/cuda132_recovery_0910a/bootstrap5152/stage.py \
  --execute --box fi-w4a16-mega-0910a --handoff-sha256 ACTUAL_HANDOFF_SHA
```

Then, through the established managed remote invocation, run sequentially from `/workspace/flashinfer-w4a16-megamoe`:

```sh
bash candidates/cuda132_recovery_0910a/bootstrap5152/bootstrap.sh
bash candidates/cuda132_recovery_0910a/bootstrap5152/setup.sh
```

Setup preserves the explicit26.05 image Torch/systemCUDA13.2.78 identity, installs the same recorded packages with `--no-deps`, then the exact checkout editable with `BUILD_NIXL_EP=0`. Existing real loader/CUPTI/profiler checks are retained. Only import paths move to the maintained central precision package. Source guard uses the manifest's actual350 required paths with the existing1584-source fingerprint algorithm; obsolete shim paths are not reconstructed. The extra folder level is accounted for in both source and staging roots. Requirements, image guard and native inventory helper are unchanged copies.

Fresh native roots are `/workspace/flashinfer-w4a16-megamoe/caches/cu132-recovery0910a-native/{torch-extensions,flashinfer}`. The setup exports those roots before imports/builds and writes their actual final inventory to `logs/cu132-recovery0910a-setup-001/native-cache-after.json`. `native-environment.json` declares intended paths; it is not an observed inventory and does not assert emptiness or prior d3ce restoration. Driver/CuTe caches are not copied. The installed source receipt, real preflight, loader/environment record and native inventory must be collected from this replacement before later work.

The old box disappeared before tight staging, so no trial mutation or compile needs recovery. Actual replacement identity reports the same hu-pdx-115/all8 UUIDs/driver and matching clock/power observations; final timing policy remains conditional on the loaded-stack verification. Reuse historical whole loop458e only if integration/root admit that continuity. Otherwise collect one fresh whole CLC BEFORE at5152 before tight4cf. Do not label an old timing or native inventory as a new observation, and do not automatically rerun completed host/default or init-cleanup cohorts.

This package performs source/dependency/import/loader setup only: no Mega kernel compilation, numerical test, profiler capture or benchmark launch. Integration separately owns the ordinary native/runtime admission and CLC timing bindings. Existing expected wheel/native-library hashes are checks to satisfy on the new image, not assumptions about its actual loaded state; preserve a failure if any recorded pin differs.
