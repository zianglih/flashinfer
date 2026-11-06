# FC1 SF register publication: rejected after bounded NV screen

Both variants are closed without production integration. Direct replaces4-byte cp.async SF loads and the completion relay with static16/8/4-byte synchronous loads, prepared-layout stores, and per-writer AsyncUmma publication. Split keeps the same publication but places loads before Gather4 and stores afterward. Neither adds a stage, scratch allocation, public alignment requirement, or runtime policy branch.

Frozen baseline: `442d2aa53f68b4640c3ab5118a76f1599ff60d34`. C1 `fi-w4a4-pipeline-1025`, GPU5 B200, UUID `GPU-70e05730-b01e-9de7-6a94-2e5bf0bd7856`; image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, PyTorch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL4.7.1. Candidate cache setup: `scripts/recovery442/env_candidate.sh`.

## Result and boundary

Direct regresses8K full chain by2.30%/2.60% in forward/reverse order, while improving16K by1.41%/2.13%. Split regresses8K by2.03%/2.28%, while improving16K by1.41%/2.46%. Percentages compare the mean of adjacent same-arm medians. The repeated8K regression rejects a uniform replacement; no token-count exception is retained.

Each arm passes eight NVFP4 paired cases (K64/384/512/7168 × quantized/per-token BF16 output) plus one short-K smoke, covering logicalM512/N128/twoCTA, route/channel/K tails, nonuniform SF, and a poisoned SF guard row. All native output comparisons across24 arms pass byte-exactly. All72 timing arrays contain100 samples and match their reported medians. `verification.json` records archive/source hashes and counts.

No all-six-format/SF32 matrix, sanitizer, NCU, primary benchmark, or production integration was run for these rejected variants. CPU source checks cover576 legal vector/K combinations, but that does not establish untested GPU correctness.

## Codegen and overlap limit

Native NV quantized FC1 remains80 registers/thread, per-token remains111, and there are no local spills. LDGSTS sites fall4→0, LDG.E.128 sites increase4→5, STS sites2→6, and barrier try-wait sites50→38. K384 statically uses8-byte SF loads; K64 uses4-byte loads. Split adds no native register increase. FC2 resources/instruction patterns remain unchanged.

In split SASS, the SF LDG128 is at0x2680 and first dependent move at0x2910. Four Gather4 instructions follow at0x2a50/0x2ab0/0x2b10/0x2b20; the first SF store is at0x2b30. The41 independent instructions before the dependent move provide some overlap, but the move may wait for SF readiness before any Gather4 issue. Moving STS alone did not force the intended TMA overlap. The automated `inspect_order.py` windows match registers in either address or data operands; this conclusion uses manual first-dependency inspection, not its heuristic first-store field.

## Complete native medians

Microseconds; actual native top-k8 routing,256 experts total/32 local, hidden7168/intermediate2048, fixedN128/FC1logicalM512/FC2M256(twoCTA).10 warmups/100 cold-L2 CUDA graph/CUPTI samples, fallback fatal. FC2 is an unchanged drift control. Isolated phase medians are not additive full-chain evidence.

| Experiment | Order | Tokens | Arm | FC1 | FC2 | Full |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: |
| direct | forward | 8192 | baseline | 150.7525 | 91.0405 | 300.0330 |
| direct | forward | 8192 | direct | 158.4165 | 91.2315 | 307.0725 |
| direct | forward | 8192 | baseline | 150.3845 | 91.1040 | 300.2885 |
| direct | forward | 16384 | baseline | 256.5125 | 153.5360 | 523.5370 |
| direct | forward | 16384 | direct | 256.2730 | 154.8480 | 516.8980 |
| direct | forward | 16384 | baseline | 259.6165 | 163.3445 | 525.0095 |
| direct | reverse | 16384 | direct | 247.6165 | 152.9445 | 518.7690 |
| direct | reverse | 16384 | baseline | 256.2410 | 154.0965 | 530.2415 |
| direct | reverse | 16384 | direct | 251.4730 | 151.7440 | 519.1530 |
| direct | reverse | 8192 | direct | 158.7520 | 91.9200 | 306.3850 |
| direct | reverse | 8192 | baseline | 150.6890 | 91.3930 | 298.6725 |
| direct | reverse | 8192 | direct | 158.0485 | 91.5360 | 306.4970 |
| split | forward | 8192 | baseline | 151.1680 | 91.2325 | 300.0970 |
| split | forward | 8192 | split | 157.4240 | 91.2645 | 306.1285 |
| split | forward | 8192 | baseline | 151.3765 | 91.2005 | 300.0010 |
| split | forward | 16384 | baseline | 255.3285 | 152.6880 | 528.7690 |
| split | forward | 16384 | split | 250.9450 | 152.8805 | 520.6740 |
| split | forward | 16384 | baseline | 260.7370 | 152.9610 | 527.4735 |
| split | reverse | 16384 | split | 247.0250 | 154.3685 | 516.9130 |
| split | reverse | 16384 | baseline | 256.1770 | 152.9120 | 529.6170 |
| split | reverse | 16384 | split | 252.1125 | 153.6965 | 516.2890 |
| split | reverse | 8192 | split | 157.7280 | 92.1280 | 305.7445 |
| split | reverse | 8192 | baseline | 150.5285 | 91.4240 | 299.0250 |
| split | reverse | 8192 | split | 157.2160 | 91.5680 | 305.9690 |

## Reproduction and archive

These commands describe the completed bounded runs. GPU work is closed; GPU5 was released with no compute process,0 MiB and0% utilization.

```bash
cd /workspace/flashinfer-w4a4-split-dynamic-n/candidate
source ../scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=5 PYTHONPATH=. SFREG_GPU_RELEASED=1
export CUTE_DSL_KEEP_PTX=1 CUTE_DSL_KEEP_CUBIN=1
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_nv_exact.py --candidate direct
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_nv_exact.py --candidate split
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_native_screen.py --candidate direct --direction forward
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_native_screen.py --candidate direct --direction reverse
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_native_screen.py --candidate split --direction forward
../.venv/bin/python ../scripts/fc1_sf_register_experiment/run_native_screen.py --candidate split --direction reverse
```

Runners reject existing result files to prevent accidental overwrite. Exact original commands, environments, source hashes and timestamps are in receipts. Native results include route counts and every sample. `raw/` contains all sources and generated PTX/CUBIN; complete SASS/resource reports are indexed by CUBIN hash under `raw/logs/fc1-sf-register/full-sass/`.

Final archive:7,454,876 bytes, SHA256 `08b614740ecf264f7baf73fe807529d7127f246178689a63575c5087395c9ef7`, also recorded in `archive-sha256.json`. It includes56 PTX/CUBIN pairs and30 unique complete core disassemblies. The initial direct-only archive is retained as `direct-initial-raw.tar.gz` (2,205,036 bytes, SHA256 `b61c32403cbbe1dff06bb6e5795c7c6c4a7b23c1ab4f437fa372a13e8a1555dd`) with its original summary and digest. Prototype design and synchronization proof: [experiment README](../../scripts/fc1_sf_register_experiment/README.md).
