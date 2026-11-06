# Routed activation preparation:256-bit payload copy

The independent source clone `flashinfer-regular-tma-ldg256` remains at base `442d2aa53f68b4640c3ab5118a76f1599ff60d34` with the same three unstaged files as the grid16 regular-TMA experiment. Only `blackwell/moe_prepare.py` differs from that control:8Uint32 payload vectors, CopyUniversal256,32-byte payload pointer/row alignment. SF writes, allocation lifetimes, PDL, route validity/padding and grid are unchanged. No fallback or shape-specific dispatch was added.

Control prep SHA256: `125d0f15910debc75ca1a128c6c59ad83db84558ef66fe338d362371955d4392`. Experiment prep SHA256: `c45c7b9ddf47d9f3c89d932215c25f0b4a040eee8ac93af7d8488419abd55c4d`.

## Validation and measurement

C1 `fi-w4a4-pipeline-1025`, B200 GPU5, image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, same restored native442 cache. Actual source files are imported directly; no backend implementation overlay.

-40 exact graph cases cover FP4/SF16 and FP8 E4M3/SF32, minimum K64/K128 and K7168, routingN16/32/64, route counts0→1→5→2→0, N16 physical padding, canonical SF padding and whole-allocation canaries.
-Three native-route prep pairs use identical preallocated buffers and mapping/limits; both payload and SF bytes/canaries match.
-Each case measures ABA then BAB, where A is128-bit control and B is256-bit copy, with10warmups/100cold-L2 CUDA-graph CUPTI samples perarm. All18arms/1,800individual samples are preserved. Initial native full-chain call obtains routing/input buffers; only preparation is timed.
-Both control and candidate cubins/PTX/SASS are archived. Candidate payload instructions are actual `LDG.E.ENL2.256` and `STG.E.ENL2.256`; SF remains32-bit. All kernels retain16active128-thread CTAs/SM,0staticSMEM and0local memory.

## Raw arm medians

|Case|128-bit control µs (ABA/BAB)|256-bit µs (ABA/BAB)|Control /256-bit geometric mean|Registers control→256-bit|
|---|---|---|---:|---:|
|nvfp4-8192-128|17.9045/17.8405/17.9035|17.0235/17.0880/17.1200|1.0472×|32→28|
|nvfp4-16384-256|33.0240/32.8800/32.9760|31.4880/31.4725/31.6160|1.0455×|32→32|
|mxfp8-16384-256|49.3760/49.1845/49.3605|46.7840/46.8800/46.8800|1.0525×|32→32|

The measured preparation saving is approximately0.8µs for NV8K,1.4µs for NV16K and2.5µs for MX16K. This is a modest positive candidate for composition; no full-chain benefit or retention conclusion is established. No primary campaign or baseline was rerun. GPU5 is released.

## Reproduction and archive

`provision.py` creates a new remote independent clone only if absent; it never overwrites an existing source checkout. `probe_exact.py` performs bounded byte checks. `run_phase.sh` contains the exact three native routing commands and invokes `phase_screen.py`. All commands preserve distinct named outputs and the existing native cache. `archive.py` fetches completed evidence and verifies sample counts, medians, cubin hashes and instruction widths.

```bash
source scripts/recovery442/env_candidate.sh
export CUDA_VISIBLE_DEVICES=5 CUTE_DSL_CACHE_DIR="$PWD/cache/prep-ldg256-experiment"
.venv/bin/python scripts/prep_ldg256_experiment/probe_exact.py \
  --repo regular-tma-ldg256 \
  --output-dir scripts/prep_ldg256_experiment/results/NEW-exact
bash scripts/prep_ldg256_experiment/run_phase.sh
```

The saved driver refuses existingr1 logs/results; choose fresh output labels when explicitly authorizing a new run. Do not rerun these completed measurements merely to regenerate summaries.

Archive: `evidence/prep-ldg256-442/raw.tar.gz`, SHA256 `99a85b843e7908e8ce16804b2065447cf142ce213bcd97db5f055798165e94ab`. `summary.json` pins all raw file hashes and derives results from every arm.
