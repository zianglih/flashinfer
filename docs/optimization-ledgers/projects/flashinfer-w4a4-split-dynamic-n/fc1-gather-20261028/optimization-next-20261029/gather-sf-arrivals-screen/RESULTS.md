# Physical SF-owner arrival qualification

Control is retained `77391e28d12a01e371196e76e56d4b46ace122df` (kernel `dca375bb…`). Candidate kernel `abec6f9ba4cbb3a26f7e88f6cbcdccf7268815245f68a6e7c7211b0e47bc5fcd` changes only the static gather-local SF barrier count to `1 + min(route_tile, 128)` and excludes non-owner threads from `cp.async.mbarrier.arrive.noinc`. Payload TMA, copied SF rows, transaction bytes, relay, phase reuse, PDL and tactics are unchanged.

The initial 12-cell screen does not establish a broad gain: geometric mean −0.227%, decode +0.130%, prefill −0.583%. The three-cell repeat confirms K3 TP8 MXFP4x8 +0.670% (original +0.640%); N3U EP8 NVFP4 is nearly neutral in the repeat. This is not an instruction-count improvement: narrow variants add 4–13 non-NOP instructions and 1–4 branch/reconvergence sites. The private predicated-PTX alternative was rejected because ptxas still generated reconvergence. No retention decision is inferred from the aggregate or from noisy wide controls.

## Original screen — all 12 cells

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.569|47.760|47.808|47.617|-0.401%|0.100%|0.102%|
|N3U EP8|16384|W4A4|584.674|583.650|583.889|583.858|+0.085%|0.140%|0.041%|
|V41F TP4|8|W4A4|51.937|51.920|51.856|52.000|+0.155%|0.121%|0.122%|
|V41F TP4|16384|W4A4|1043.304|1043.176|1042.280|1042.424|+0.013%|0.084%|0.086%|
|V3 EP8|8|MXFP8|88.448|88.353|88.480|88.512|+0.072%|0.072%|0.144%|
|V3 EP8|16384|MXFP8|703.411|746.899|739.651|719.731|-4.271%|2.320%|0.980%|
|V3 TP8|8|MXFP8|70.849|70.753|71.025|70.944|+0.010%|0.135%|0.384%|
|V3 TP8|16384|MXFP8|1362.715|1342.923|1354.747|1358.218|+0.863%|0.331%|0.880%|
|V41F EP4|8|MXFP4x8|49.936|49.696|49.712|49.776|+0.306%|0.320%|0.033%|
|V41F EP4|16384|MXFP4x8|798.260|796.180|812.244|805.187|-0.305%|0.868%|2.018%|
|K3 TP8|8|MXFP4x8|80.513|80.001|80.001|80.513|+0.640%|0.000%|0.001%|
|K3 TP8|16384|MXFP4x8|1661.181|1671.838|1662.029|1679.502|+0.203%|1.103%|0.590%|

## Predeclared repeat — kept separate

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|8|W4A4|47.568|47.649|47.568|47.600|-0.051%|0.067%|0.170%|
|V3 EP8|16384|MXFP8|737.091|713.171|726.195|691.507|-0.795%|6.592%|1.826%|
|K3 TP8|8|MXFP4x8|80.576|80.113|79.904|80.512|+0.670%|0.080%|0.260%|

V3 EP16K MXFP8 stays negative in both campaigns, but its source-paired native FC1 and FC2 PTX, CUBIN, SASS and resource files are byte-identical. The repeat control spread is 6.592%; all observed repeat clocks are SM2032MHz with clock-reason0. The unresolved end-to-end variation is retained, not attributed to clocks or to changed kernel instructions. Binary identity was established by a separate compile-only public benchmark capture using the exact frozen cache key/tactic and route ID/weight hashes; neither MoE kernel was launched in that diagnostic.

## Qualification and methodology

- 41 existing/focused exact cases per arm, 80 paired compiled functions, with N16/N32/N64/N128/N256 and one-/two-CTA coverage. No register or local-site growth. The two inherited synthetic MX FC1 cases retain STACK160 and 20 LDL/20 STL sites; this is not an all-qualification-spill-free claim.
- Original screen: 4,800 raw CUPTI samples and 96 loaded MoE guards. Repeat: 1,200 samples and 24 guards. All timed kernels have LOCAL_BYTES0; all source, cache, route, runtime and observer guards passed. No missing clock quartiles.
- Fixed existing native tactics, same physical GPU for every complete C-A-A-C and repeated cell, 100 strict CUPTI samples per phase, 10 warmups, cold-L2 CUDA graphs, public functional API, unfused swap-AB. NVFP4 includes its input quantizer. No retuning, external baseline rerun or sanitizer.
- Cell speedup is `100 * (sqrt(C1*C2/(A1*A2)) - 1)`, using each phase's median. Repeat rows do not replace original rows. Stock clocks; small changes within repeat spread remain inconclusive.
- B300, explicit image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTe DSL4.8, driver595.91.07. Persistent native and CuTe caches reused.

## Evidence

- `evidence/` contains all original raw samples, phase/source/guard receipts and telemetry; `raw-audit.json` and `independent-raw-audit.json` verify every row.
- `../gather-sf-arrivals-screen-repeat/evidence/` and its independent audit preserve the complete repeat separately.
- `../gather-sf-arrivals-r0-7739/` binds exact/codegen qualification to the timed source. `../gather-sf-arrivals-native-wide/analysis.json` binds native binary identity to the frozen wide case. Native archive SHA256: `ed482b94d51c7b444c95258c251f40650d58d9a2325b2473adc8b52b060b9075` (51 verified files).
- Diagnostic route-order guard failure and archive-cache-path failure are preserved. Both stopped data acceptance before analysis; neither changed production source or timed work.
