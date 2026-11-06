# Frozen adcc source and timeline interpretation

Independent CPU-only review against `aab93f854054de834447bdd8985b8bbd653fb3c8`; no GPU execution or source changes. The current executed trace in [summary.json](summary.json) supersedes earlier resource receipts for this interpretation.

## Source identity and placement

The actual candidate files and baseline Git blobs match [source-manifest.json](source-manifest.json), SHA256 `083b4aef3f8e3b915a0dc5b19687b0297b35b27b838bc6199fa355cd47e11a4a`.

|File|aab SHA256|adcc SHA256|
|---|---|---|
|Blackwell core|`7c0fe69faab5acecafdd3d67a157f016836e149fafdc29942542d44ef4852c66`|`adcc6506dd4ba28769cf7a5f65526e9dc927363847150de231eb850cc6c9b4b9`|
|`moe_prepare.py`|`ec2c70b178f828b769ab7d63128996bed8535f23f099591e1a5c046392bc292c`|`a3b0042ea0ae64f66cfc968768c85b96118ed750fa92a668cb1485f91866a67b`|
|`utils.py`|`9811c53e0faa4ab39bc8dd3b03152498958938ff17761fdad57a0afae6ede889`|unchanged|
|`moe_finalize.py`|`0b043869056d7e1d8bd3a7c35d9ab33ebb632e65c410626cdebaf5d2784dd8cf`|unchanged|

All anchors below refer to the frozen files under `source-snapshots/{control,candidate}/`; “core” means `blockscaled_contiguous_grouped_gemm_finalize_fusion.py`.

- Preparation retains its predecessor wait at candidate `moe_prepare.py:95–96`, then signals dependents at `:99`, before reading the active count and copying payload/SF. The old signal was at control `moe_prepare.py:165–166`, after the copies. The consumer GEMM still waits before consuming prepared data.
- Both GEMMs perform cluster/TMEM initialization before their dependency wait: candidate core `:971–976`, then wait at `:1003`. The common all-thread signal now follows at `:1013`, before the persistent tile loop and operand loads. Standalone FC2 with PDL first executes each issuer's device-release fence at `:1004–1011`; its helper is `:79–82`. No new CTA barrier was inserted. Control signaled at `:1531`, after the terminal CTA barrier and TMEM cleanup (`:1524–1530`). Candidate preserves that cleanup at `:1540–1546` but removes the terminal signal.
- Combine is unchanged. Candidate `moe_finalize.py:131–138` loads routing rows/scales before its wait at `:140–141`; expert-output loads/reduction follow at `:145` onward. Thus its early lifetime can include useful metadata setup and dependency waiting. It does not establish early consumption of FC2 payload.
- Launch geometry and shared storage are unchanged. Candidate core `:845–855` uses the SM-count-derived grid, cluster size, 288-thread block, `SharedStorage.size_in_bytes()`, and `min_blocks_per_mp=1`. The latter is a compiler launch-bounds hint, not by itself a proof of one resident CTA per SM.

## Residency and observed overlap

The executed T16384 tactic is M256/N256, two CTAs per cluster, for both GEMMs. Both arms have 148 CTAs (74 clusters) and identical resource fields:

|Kernel|Threads|Registers/thread|Requested dynamic SMEM|Nsight `sharedMemoryExecuted`|
|---|---:|---:|---:|---:|
|FC1|288|80|195,584 B|200,704 B|
|FC2|288|120|229,888 B|233,472 B|
|Combine|128|80|0 B|32,768 B|

FC1 plus FC2 require **425,472 B** of requested shared memory, exceeding the B200's **233,472 B per SM**; each GEMM alone exceeds half that capacity. Same-SM FC1/FC2 co-residency is therefore excluded by shared-memory demand, independently of the launch-bounds hint. An early signal does not reduce this allocation. FC2 can start its prologue on SM/cluster resources that have become free while other FC1 CTAs remain alive. The retained dependency wait prevents interpreting that lifetime overlap as concurrent dependent GEMM computation.

Combine allocates register tensors (`moe_finalize.py:122–126`) and its launch requests no shared memory (`:105–110`); the source contains no shared-memory allocation. Nevertheless, the executed trace reports `sharedMemoryExecuted=32768`. Preserve that field without assigning unsupported per-CTA reservation semantics. Zero requested SMEM alone does not prove FC2/combine co-residency. This trace cannot distinguish admission on freed SMs from any co-residency elsewhere, and does not provide per-SM/CTA or dependency-wait PC timing.

The candidate's FC1/FC2 lifetime overlap is **29.568 us**, and FC2/combine overlap is **144.992 us**. Combine starts at **263.264 us**, before FC2 ends at **408.256 us**. Its end is **87.936 us** after the FC2 endpoint, versus **80.064 us** for control. Those endpoint differences are arithmetic segments, not measurements of useful combine work. Total span is **485.185 → 496.192 us** for one warmed profiler replay per arm; these are not benchmark medians.

The source and trace establish earlier downstream admission with unchanged resources. They do not establish cache causality, resource contention by waiting CTAs, a spill regression, or the amount of useful computation overlapped. All QMD completion timestamps are NULL, and graph edge-type metadata was not queried.
