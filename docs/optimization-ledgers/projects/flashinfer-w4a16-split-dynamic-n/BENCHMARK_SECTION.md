### Performance

At measured revision `9ec90d0`, unfused finalize improves **1.020415×** across the 11 retention points (**2.041% speedup**, equivalent to **2.001% lower latency**). Decode T4–512 improves **1.008383×**; prefill T4096/T8192/T16384 improves **1.053206×**. Unfused performance is the retention target; the completed fused measurements are reported separately below.

- **Sources:** before `316faec37a4706a2ecc7d46265087f8190b40baa`; after `9ec90d0696752c72ff826c8880e58515ace84e60`. Both use the same upstream base, benchmark source and runtime. These are the measured revisions, including the fixed-tactic diagnostics; their provenance is preserved.
- **Split-only follow-up:** at `c610e3c9d46078a131bd84cd6d98ab682d03eb54`, the runtime-N helpers now live directly in the split kernel, and MegaMoE is restored byte-for-byte to the baseline. Executable helper bodies are AST-equivalent to the measured implementation; only helper ownership and documentation change. This follow-up has not been rebenchmarked. Its 28 focused tests pass, and both retained CTA-group PTX files match the measured revision byte for byte. The subsequent shared-reference and deterministic-combine change is qualified separately; this PTX equality applies to the split MMA specializations, not to the changed standalone finalizer.
- **Rounding follow-up:** `333009bd63364d7332c0b449471561c01e4b8867` additionally changes the common deterministic finalizer to preserve FP32 subnormals and use a first-slot multiply, affecting W4A4 and W4A16. It has not been measured by the full-MoE campaign above. The separate finalizer-only CUPTI spotcheck below compares the old combine with recorded finalizer-measurement head `65a563a447eb23e55177eec907533439180d760c`; it neither replaces primary rows nor enters their aggregates.
- **Environment:** one NVIDIA B300 SXM6 AC (SM103), GPU0 on an eight-GPU node; `nvcr.io/nvidia/pytorch:26.05-py3`; driver `595.91.07`; Python `3.12.3`; container Torch `2.12.0a0+5aff3928d8.nv26.05`; CUDA runtime `13.2` and system nvcc `13.2.78`; imported CuTe DSL `4.7.1`; CUPTI Python `13.4.0` / library package `13.4.58`. Additional installed CUDA compiler/NVVM packages are `13.3.73`; the emitted CuTe PTX identifies the DSL bundled compiler as `13.3.27` (NVVM 23, PTX 9.3, `sm_103a`), separate from system CUDA 13.2. The older container DSL distribution is shadowed by the verified venv import.
- **Workload:** native `benchmarks/bench_moe_deepseek.py` W4A16 wrapper arm; H7168/I2048, 256 global experts, top-k 8, groups 8/top-groups 4, routed scaling 2.5, seed 42 and routing-bias scale 0.01; SwiGLU; BF16 activations/output, NVFP4 weights and FP32 accumulation. Single-GPU simulated EP8/TP1 means 32 local experts at offset 0. Routing and split W4A16 are timed; weight preparation, allocation, JIT/autotuning and inter-GPU communication are excluded.
- **Timing:** two independent normal-AUTO processes per source/finalize mode; ten warmups and 100 native cold-L2 CUDA-graph CUPTI samples per row, reporting medians. `CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0`. Primary runs do not load another arm’s tactic cache. Native build-cache restoration avoids repeated compilation when changing checkouts and does not reuse AUTO selections.
- **Grid and metric:** token inclusion follows [#6277](https://github.com/flashinfer-ai/flashinfer/pull/6277): `1,2,4,8,16,32,64,128,256,512,4096,8192,16384`; only T1/T2 are excluded from retention. The split workload/timer follow [#5186](https://github.com/flashinfer-ai/flashinfer/pull/5186). Row speedup is `sqrt((Before R1 × Before R2)/(After R1 × After R2))`; aggregates are the geometric mean of those row ratios. Above 1 means faster. No row minima or fixed-tactic substitutions.
- **Existing-data reuse:** baseline unfused R1 had already used the older grid through 8192. Its T16384 was measured separately with the same source/runtime; T1024/T2048 are preserved as unpaired supplemental observations. No existing primary row was rerun to change the grid. The tables contain all **106 measured primary medians**.

#### Unfused finalize — retention evidence

The per-repeat retention aggregates are **1.015547×** and **1.025306×**. Ten of 11 paired rows improve. T8 is **0.995283×** under AUTO and changes direction between repeats; its selected tactics also change. T8192 improves **1.087116×** with identical full FC1/FC2 tactics in all four captures. T16384 uses matched N128 in R1 and matched N192 in R2, so its repeats are not a fixed-tactic comparison.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 34.2730 | 34.7520 | 34.0160 | 34.0485 | 1.014087× |
| 2* | 40.3840 | 40.0645 | 39.7925 | 39.6325 | 1.012880× |
| 4 | 54.8640 | 54.9120 | 54.4165 | 53.5050 | 1.017220× |
| 8 | 68.6730 | 69.2005 | 69.7610 | 68.7685 | 0.995283× |
| 16 | 76.8970 | 76.8330 | 76.2880 | 75.7450 | 1.011168× |
| 32 | 109.7130 | 109.9850 | 109.1370 | 108.9290 | 1.007484× |
| 64 | 143.2010 | 143.6820 | 141.9375 | 142.0810 | 1.010084× |
| 128 | 145.8900 | 145.7775 | 144.1300 | 144.6090 | 1.010144× |
| 256 | 152.7530 | 152.4330 | 151.4895 | 151.6810 | 1.006648× |
| 512 | 159.0090 | 157.9055 | 156.9455 | 157.0890 | 1.009165× |
| 1024† | 174.8340 | — | — | — | — |
| 2048† | 211.6820 | — | — | — | — |
| 4096 | 308.8670 | 309.3145 | 295.1390 | 294.5150 | 1.048380× |
| 8192 | 627.3330 | 620.1335 | 573.9090 | 573.5730 | 1.087116× |
| 16384 | 1183.9945 | 1226.3790 | 1199.2750 | 1152.2980 | 1.025051× |

*T1/T2 are reported but excluded from retention. †T1024/T2048 are supplemental; missing cells were not measured. T4 and all three prefill sizes participate in retention.*

#### Fixed-tactic diagnostics — separate from AUTO results

Ten additional unfused measurements replay the original saved R1 caches with `do_autotune=False`, using the same ten-warmup/CUPTI100 cold-L2 timing. Each pair holds both FC1/FC2 tactics fixed across sources. Cache metadata/hash, unchanged-cache flags, selected tactics, input shapes/histograms, software and source hashes were validated. Fallback tactics are rejected. These medians are not substituted into the AUTO table or aggregates.

| Tokens | Saved R1 cache | FC1 / FC2 tactic (M/N/K; cluster) | Before (µs) | After (µs) | Speedup |
| ---: | :--- | :--- | ---: | ---: | ---: |
| 8 | baseline | 128/16/256; 2×1 / 256/16/256; 2×1 | 68.6080 | 68.1120 | 1.007282× |
| 8 | candidate | 128/8/256; 2×1 / 128/8/256; 2×1 | 69.9840 | 69.2005 | 1.011322× |
| 4096 | baseline | 256/128/256; 2×1 / 256/128/256; 2×1 | 312.0825 | 297.1540 | 1.050238× |
| 4096 | candidate | 256/192/256; 2×1 / 256/192/256; 2×1 | 367.0585 | 294.5140 | 1.246319× |
| 16384 | baseline | 256/128/256; 2×1 / 256/128/256; 2×1 | 1171.6410 | 1165.3205 | 1.005424× |

All five measured pairs improve; all listed tactics use raster-along-M=True. T8 improves under both saved choices, so its small AUTO regression is not reproduced by these fixed-tactic pairs. At T4096, dynamic N improves both N128 and N192; the latter becomes the AUTO choice in both candidate repeats. The common N128 T16384 pair also improves slightly. Each diagnostic is one matched pair: it does not establish that every tactic improves or eliminate run variation.

<details>
<summary>Fused finalize — reported only, excluded from retention (all 52 measured medians)</summary>

Descriptive geometric speedup is **0.992009×** overall, **1.004722×** decode and **0.958889×** prefill. All three prefill rows regress in both repeats; T8192/T16384 use identical full tactics across sources. Fused performance is outside the retention target, and these losses are preserved without replacement measurements.

| Tokens | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1* | 36.8640 | 36.9600 | 37.3450 | 36.6720 | 0.997433× |
| 2* | 42.1600 | 42.0170 | 41.9365 | 42.6245 | 0.995490× |
| 4 | 58.3845 | 58.4485 | 58.2245 | 58.2730 | 1.002880× |
| 8 | 73.2970 | 73.4565 | 73.0890 | 74.1610 | 0.996654× |
| 16 | 79.9685 | 82.8490 | 83.1530 | 79.8405 | 0.998970× |
| 32 | 114.4970 | 114.4810 | 113.8570 | 113.7930 | 1.005834× |
| 64 | 148.4495 | 148.2570 | 147.2490 | 147.2170 | 1.007608× |
| 128 | 152.1620 | 152.0655 | 151.3775 | 151.4570 | 1.004600× |
| 256 | 158.9775 | 158.7215 | 158.1935 | 157.7930 | 1.005420× |
| 512 | 164.8970 | 164.7220 | 162.3695 | 162.0810 | 1.015930× |
| 4096 | 350.3870 | 350.7390 | 366.4835 | 366.5630 | 0.956455× |
| 8192 | 659.3340 | 667.2220 | 705.6710 | 685.8305 | 0.953407× |
| 16384 | 1301.8370 | 1295.7555 | 1329.9645 | 1356.7965 | 0.966857× |

*T1/T2 are excluded from these descriptive aggregates. No fused value enters the unfused retention metric.*

</details>

- **Evidence limits:** these are routed-expert microbenchmarks, not end-to-end model results. Two primary sweeps and one pair per diagnostic do not establish statistical significance. The unchanged primary harness retains medians and saved tactic caches, not individual timing vectors; all measured medians are shown above. Fixed-tactic diagnostics remain separate, and no universal acceptance percentage is inferred from the predecessor PRs.

#### Isolated deterministic-finalizer rounding check — separate from primary MoE results

This additional check compares only `moe_finalize.py` from `c610e3c9d46078a131bd84cd6d98ab682d03eb54` with recorded finalizer-measurement head `65a563a447eb23e55177eec907533439180d760c`. It measures the authorized W4A4/W4A16 combine rounding change. It does not measure routing, either expert GEMM, or complete MoE latency, and none of these values enters the primary retention metric.

- **Workload:** T8/T8192, H7168, top-k8, BF16 expert rows/output and FP32 scores. Expanded rows exercise W4A4 addressing; a random nonidentity permutation exercises W4A16 addressing. All eight routes are local/valid, unlike the primary EP8 traffic distribution. Both sources receive the exact same tensor objects, generated with seed `20261024 + tokens`. Their outputs match bit for bit for these ordinary finite inputs; signed-zero/subnormal contracts are covered by the exact tests separately.
- **Environment/control:** same B300, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, Torch `2.12.0a0+5aff3928d8.nv26.05`, CuTe DSL4.7.1 and CUPTI13.4.0 as above. Both source modules are loaded in one process, with independent kernel caches. Ten requested warmups and 100 cold-L2 CUDA-graph CUPTI samples per arm; fallback timers are rejected. PDL is explicitly disabled for this standalone kernel because no FC2 producer is present. Input preparation, module loading and JIT compilation are untimed.
- **Order/provenance:** each shape runs before R1 → after R1 → after R2 → before R2. Source snapshots match their Git objects; the only checkout status entries are the three recorded vendor-header symlinks. The saved JSON retains all 1,600 individual samples, 16 medians, source/script/timer hashes and input mapping hashes. Reported row speedup is the geometric mean of the two before/after ratios.

| Tokens | Input layout | Before R1 (µs) | Before R2 (µs) | After R1 (µs) | After R2 (µs) | Speedup |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 8 | expanded | 6.2080 | 6.2720 | 6.2400 | 6.2080 | 1.002561× |
| 8 | permuted | 6.3520 | 6.3040 | 6.3355 | 6.3040 | 1.001301× |
| 8192 | expanded | 176.7210 | 176.5935 | 176.5780 | 176.6250 | 1.000316× |
| 8192 | permuted | 190.8180 | 190.8170 | 190.8655 | 190.7375 | 1.000084× |

The four paired ratios are close to parity (1.000084–1.002561×). This limited synthetic check does not establish statistical significance or substitute for a new full-MoE campaign at final head.

<details>
<summary>Self-contained isolated-finalizer reproduction</summary>

Use the pinned environment above and run from the final-head checkout, with the two recorded commits available locally. This extracts both source modules from Git, preserves them in a new project-local directory, calls the existing CUPTI timer and saves every sample separately from the primary benchmark.

```bash
CUDA_VISIBLE_DEVICES=0 TRTLLM_ENABLE_PDL=1 FLASHINFER_DIST_AWARE_AUTOTUNE=0 \
PYTHONPATH=. python - <<'PYFINALIZE'
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import warnings
import torch
from cupti import cupti
from flashinfer.testing.utils import bench_gpu_time_with_cupti

assert int(importlib.metadata.version("cupti-python").split(".")[0]) >= 13
warnings.filterwarnings("error", message=r".*[Ff]alling back.*")
out = Path(tempfile.mkdtemp(prefix="finalizer-rounding-", dir="..")).resolve()
refs = {
    "before": "c610e3c9d46078a131bd84cd6d98ab682d03eb54",
    "after": "65a563a447eb23e55177eec907533439180d760c",
}
source_path = "flashinfer/fused_moe/cute_dsl/blackwell/moe_finalize.py"
modules, sources = {}, {}
for arm, ref in refs.items():
    source = subprocess.check_output(["git", "show", f"{ref}:{source_path}"])
    path = out / f"{arm}.py"
    path.write_bytes(source)
    name = f"finalize_rounding_{arm}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    modules[arm] = module
    sources[arm] = {"git_head": ref, "sha256": hashlib.sha256(source).hexdigest()}

rows = []
for tokens in (8, 8192):
    h, k = 7168, 8
    g = torch.Generator(device="cuda").manual_seed(20261024 + tokens)
    logical = torch.randn((tokens * k, h), dtype=torch.bfloat16,
                          device="cuda", generator=g)
    scores = torch.rand((tokens, k), dtype=torch.float32,
                        device="cuda", generator=g) + 0.125
    permutation = torch.randperm(tokens * k, device="cuda", generator=g)
    for layout in ("expanded", "permuted"):
        if layout == "expanded":
            data = logical
            mapping = torch.arange(tokens * k, device="cuda", dtype=torch.int32)
        else:
            data = torch.empty_like(logical)
            data[permutation] = logical
            mapping = permutation.to(torch.int32)
        mapping = mapping.reshape(tokens, k).contiguous()
        outputs = {a: torch.empty((tokens, h), dtype=torch.bfloat16, device="cuda")
                   for a in modules}
        def run(arm):
            modules[arm].moe_unpermute(
                data, outputs[arm], mapping, scores, tokens, k,
                enable_pdl=False, input_is_expanded=layout == "expanded")
        run("before")
        run("after")
        torch.cuda.synchronize()
        torch.testing.assert_close(outputs["before"].view(torch.int16),
                                   outputs["after"].view(torch.int16), rtol=0, atol=0)
        row = {"tokens": tokens, "layout": layout, "measurements": {}}
        for arm, repeat in (("before", 1), ("after", 1), ("after", 2), ("before", 2)):
            times = [1000 * float(t) for t in bench_gpu_time_with_cupti(
                lambda arm=arm: run(arm), dry_run_iters=10, repeat_iters=100,
                cold_l2_cache=True, use_cuda_graph=True)]
            assert len(times) == 100 and all(math.isfinite(t) and t > 0 for t in times)
            row["measurements"][f"{arm}_r{repeat}"] = {
                "median_us": statistics.median(times), "samples_us": times}
        m = row["measurements"]
        row["paired_speedup"] = math.sqrt(
            m["before_r1"]["median_us"] * m["before_r2"]["median_us"] /
            (m["after_r1"]["median_us"] * m["after_r2"]["median_us"]))
        rows.append(row)
        (out / "results.json").write_text(json.dumps({"sources": sources, "rows": rows}, indent=2))
        print(tokens, layout, {key: value["median_us"] for key, value in m.items()},
              row["paired_speedup"], flush=True)
        del outputs, data, mapping
    del logical, scores, permutation
    torch.cuda.empty_cache()
print(out / "results.json")
PYFINALIZE
```

</details>
