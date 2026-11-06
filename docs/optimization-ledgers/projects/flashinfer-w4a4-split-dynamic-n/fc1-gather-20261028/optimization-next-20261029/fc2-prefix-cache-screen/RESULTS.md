# Reject protected-prefix register snapshot

Decision: reject R3; retain d9/9037's existing FC2 implementation. No full-matrix expansion or repository commit/push was made. All12 cells are reported, including the earlier wider-span losers and the additional no-overlap bulk-output control.

The complete screen is **-0.270%** overall; the9 affected prefill cells are **-0.344%**, TP prefill **-1.118%**, and per-token **-1.912%**. These mixed results and repeated tight TP losses do not justify the extra register snapshot, helper splitting, and overlapping-path code growth. The added no-overlap control is neutral.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|32|W4A4|103.489|103.345|103.425|103.393|+0.054%|0.093%|0.077%|
|N3U EP8|4096|W4A4|232.498|221.250|221.042|232.322|+5.093%|0.076%|0.094%|
|N3U TP8|4096|W4A4|384.003|377.906|377.379|384.291|+1.722%|0.075%|0.140%|
|K3 TP8|8192|W4A4|785.736|795.783|796.056|785.431|-1.299%|0.039%|0.034%|
|K3 TP8|8192|PER-TOKEN|1028.439|1063.319|1063.143|1028.630|-3.263%|0.019%|0.017%|
|V3 TP8|8192|PER-TOKEN|771.975|803.128|802.727|771.784|-3.867%|0.025%|0.050%|
|V41F TP4|16384|PER-TOKEN|1268.136|1294.281|1294.568|1267.672|-2.049%|0.037%|0.022%|
|V3 TP8|512|MXFP8|269.219|270.338|271.106|270.947|-0.237%|0.642%|0.284%|
|N3U TP8|16384|PER-TOKEN|1785.212|1756.380|1757.740|1785.964|+1.624%|0.042%|0.077%|
|K3 EP8|8192|W4A4|474.564|475.124|476.276|474.964|-0.197%|0.084%|0.242%|
|V3 TP8|8192|MXFP4x8|683.541|687.525|687.796|684.245|-0.548%|0.103%|0.039%|
|V41F EP4|4096|MXFP4x8|349.105|348.866|348.691|348.739|+0.041%|0.105%|0.050%|


## Mechanism and qualification

R3 reads the protected TMEM interval first into packed Uint32 register snapshots, releases accumulator ownership, then stores full TMA groups before the SIMT tail in monotonic output order. Full cached fragments retain native stmatrix ownership; cached partial fragments retain the existing row-owned transpose. Uncached partial output uses the unchanged streamed `_run_token_group`. No extra transpose, buffer allocation, public argument, tactic, model/dtype condition, scale contract, or PDL change was added.

Independent ownership/ring proof covered7716 cases. The unchanged d9 control and final R3 each passed39 zero-tolerance cases with76 CUBIN captures. All152 prelaunch resource guards passed; no new local spills.37 CUBINs are byte-identical. The formerly problematic per-token P128 FC2 is128→200 registers, zero stack/local instructions, but2717→3823 static non-NOP instructions (+1106) and78→115 branches (+37). Some overlapping FC2 cases add1268 instructions/54 branches. No-overlap FC2 differs by at most4 registers and−2…+2 instructions. Static code counts are not dynamic issue counts.

R0/R1 stopped before launching the failing FC2 because they spilled56/8 stack bytes respectively. R2 fixed the spill but exposed a staged-code membership NameError after17 passing cases. R3 only made that membership compile-time explicit. All failed source revisions, source hashes, patches, logs and CUBIN evidence remain in `../fc2-prefix-cache-d9`; they are not retention measurements. No sanitizer was run.

## Timed method and source boundary

C3 `fi-gather-opt-1029`, B300 SM103; persistent CUDA13.2/CuTe4.8 caches and stable native include/data paths were retained. Control is the full514-file source-equivalent d9dee2da. Current9037 changes only W4A16, whose code is not timed in this screen. Candidate is unstaged R3 kernel7d6955fc1e4a6bf11569f9db5321890231cce068a5ea9d2ecf8c89741368e56a; exact full-file hashes/dirty patches are recorded in the gate and performance configs.

Same physical GPU per complete C-A-A-C job; fixed native winners and routed inputs; public unfused swap-AB API; input activation quantizer included for NVFP4, unchanged per-token recipe; no AUTO. Each phase uses10 warmups and100 strict CUPTI samples with cold-L2 CUDA graph replay; no event fallback. Speedup is100×(sqrt(C1×C2)/sqrt(A1×A2)−1), using per-phase medians. All44 phases/4800 CUPTI samples, route/tactic/cache/source checks and96 loaded-MoE function guards passed. All48 FC2 functions have zero local bytes; peak FC2 register count is216. The only observer change adds that CPU-only FC2 local-byte assertion before launch; timing/compiler flags are unchanged.

Stock clocks were never changed. All192 sampled quartiles have NVML coverage and median SM clock2032MHz. Maximum control/candidate repeat spreads are0.642%/0.284%. The MXFP8/512 and K3 EP8192 negatives are smaller than their largest repeat spreads and are inconclusive; they remain in every table and aggregate. The K3/V3/V41F TP per-token losses have tight repeats and are decisive.

## Component evidence and next scope

CUPTI per-invocation completion-frontier extensions (not sums of overlapping kernel durations) put the K3/V3/V41F TP per-token losses in FC2: +34.916/+31.072/+28.028µs, while FC1 changes−0.058/−0.255/−0.166µs. K3 TP W4A4 adds9.714µs in FC2. N3U EP/TP W4A4 gains are primarily FC1:−11.200/−6.702µs, with FC2 approximately neutral. N3U TP per-token does gain28.936µs in FC2, but that isolated gain does not compensate for the three repeated regressions. The next feasible small change is FC1-only protected-span derivation; FC2 should keep its existing64-column release contract. No new experiment has been started.

`evidence/components.json`, `cells.csv`, `summary.json`, `runtime-resource-summary.json`, and all raw phase logs/timelines are source-bound. Raw archive SHA256:3a79a0173299330bb4ba2c115084e3fc56e5fc6fbffcc05e804b023a133c7bce (24,533,968 bytes,307 verified archived files).
