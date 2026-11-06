# Elected-owner CLC: complete fixed-tactic timing evidence

Both tested versions are rejected. Canonical source stays at `9b4721b0`; the goal of improving CLC-only performance remains open. All six model/family workers completed in each screen. No TRTLLM or W4A16 timing was performed.

Environment: c3 `fi-moe-nvfp4-port-1026`, B300, CUDA 13.2, `nvcr.io/nvidia/pytorch:26.05-py3`, installed CUTLASS DSL 4.7.1. Public `benchmarks/bench_moe_deepseek.py` through CuteDslMoEWrapper, frozen native six-field True/True tactics, PDL on, fused finalize off, 10 warmups and 100 cold-L2 CUDA-graph CUPTI samples per point. NV includes initial quantization; MX inputs are prequantized.

Each C/A value below is the raw process median in milliseconds. Speedup = mean(C0,C3) / mean(A1,A2); drift = C3/C0 − 1. Full 100-sample arrays, routing identities, cache-hit tactics, source hashes and commands are preserved in each linked result tree. No candidate timings are pooled across versions.

## V2 fixed lane

Candidate patch `d8ca478d88600876d317374b3f07b873a30f4dd550bd7665a8bad88855069d20` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. [Full summary](full_screen/results-v2/full-screen-summary.json); [collection hashes](full_screen/results-v2/collection.json).

All four processes are fresh.

Geomean: overall **0.976734x**, decode **0.992105x**, prefill **0.961601x**.

| Model | Backend | Tokens | C0 ms | A1 ms | A2 ms | C3 ms | C/A | Control drift |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 0.1710410 | 0.1727370 | 0.1727530 | 0.1710570 | 0.990182x | +0.009% |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 0.2913620 | 0.2994900 | 0.2998420 | 0.2917625 | 0.972957x | +0.137% |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 0.4362430 | 0.4687070 | 0.4684200 | 0.4359070 | 0.930664x | -0.077% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1.2527445 | 1.2966015 | 1.3073375 | 1.2330820 | 0.954641x | -1.570% |
| kimi-k3 | CuteDSL MXFP8 | 32 | 0.2993620 | 0.2995220 | 0.2994100 | 0.2995060 | 0.999893x | +0.048% |
| kimi-k3 | CuteDSL MXFP8 | 128 | 0.5202600 | 0.5214115 | 0.5214760 | 0.5207075 | 0.998159x | +0.086% |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 0.6749645 | 0.7086610 | 0.7079255 | 0.6746445 | 0.952719x | -0.047% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1.3374010 | 1.4204910 | 1.4186020 | 1.3718180 | 0.954255x | +2.573% |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 0.1822250 | 0.1828015 | 0.1828335 | 0.1823690 | 0.997153x | +0.079% |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 0.3073465 | 0.3151225 | 0.3147865 | 0.3064985 | 0.974498x | -0.276% |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 0.4767715 | 0.5044520 | 0.5027720 | 0.4787080 | 0.948627x | +0.406% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1.2389055 | 1.3457385 | 1.3477865 | 1.2361380 | 0.918886x | -0.223% |
| kimi-k3 | CuteDSL W4A4 | 32 | 0.1772330 | 0.1795050 | 0.1795855 | 0.1771375 | 0.986856x | -0.054% |
| kimi-k3 | CuteDSL W4A4 | 128 | 0.2973300 | 0.2989620 | 0.2994270 | 0.2973615 | 0.993821x | +0.011% |
| kimi-k3 | CuteDSL W4A4 | 4096 | 0.4148190 | 0.4359070 | 0.4360030 | 0.4150105 | 0.951738x | +0.046% |
| kimi-k3 | CuteDSL W4A4 | 16384 | 0.8979425 | 0.9712390 | 0.9714950 | 0.8975590 | 0.924214x | -0.043% |
| v3 | CuteDSL MXFP4x8 | 32 | 0.1005920 | 0.1005920 | 0.1006085 | 0.1005610 | 0.999764x | -0.031% |
| v3 | CuteDSL MXFP4x8 | 128 | 0.1357610 | 0.1357610 | 0.1359210 | 0.1358090 | 0.999588x | +0.035% |
| v3 | CuteDSL MXFP4x8 | 4096 | 0.2286900 | 0.2349615 | 0.2346900 | 0.2286090 | 0.973699x | -0.035% |
| v3 | CuteDSL MXFP4x8 | 16384 | 0.7406930 | 0.7544690 | 0.7253165 | 0.7025015 | 0.975273x | -5.156% |
| v3 | CuteDSL MXFP8 | 32 | 0.1654410 | 0.1653770 | 0.1654250 | 0.1654090 | 1.000145x | -0.019% |
| v3 | CuteDSL MXFP8 | 128 | 0.2303215 | 0.2296660 | 0.2301935 | 0.2302570 | 1.001564x | -0.028% |
| v3 | CuteDSL MXFP8 | 4096 | 0.3045460 | 0.3101465 | 0.3104500 | 0.3045780 | 0.981514x | +0.011% |
| v3 | CuteDSL MXFP8 | 16384 | 0.8111410 | 0.7853970 | 0.8103415 | 0.7858940 | 1.000812x | -3.113% |
| v3 | CuteDSL PER-TOKEN | 32 | 0.1062720 | 0.1063050 | 0.1064645 | 0.1063685 | 0.999394x | +0.091% |
| v3 | CuteDSL PER-TOKEN | 128 | 0.1426890 | 0.1461130 | 0.1462085 | 0.1429450 | 0.977123x | +0.179% |
| v3 | CuteDSL PER-TOKEN | 4096 | 0.2528660 | 0.2598580 | 0.2593455 | 0.2528500 | 0.974023x | -0.006% |
| v3 | CuteDSL PER-TOKEN | 16384 | 0.6837800 | 0.7203885 | 0.7205000 | 0.6835885 | 0.948976x | -0.028% |
| v3 | CuteDSL W4A4 | 32 | 0.1023205 | 0.1025930 | 0.1022410 | 0.1022405 | 0.998667x | -0.078% |
| v3 | CuteDSL W4A4 | 128 | 0.1385450 | 0.1423045 | 0.1423690 | 0.1381610 | 0.972012x | -0.277% |
| v3 | CuteDSL W4A4 | 4096 | 0.2113610 | 0.2171850 | 0.2172975 | 0.2112495 | 0.972676x | -0.053% |
| v3 | CuteDSL W4A4 | 16384 | 0.5617310 | 0.5981160 | 0.5974430 | 0.5619715 | 0.939897x | +0.043% |
| v41-flash | CuteDSL MXFP4x8 | 32 | 0.1228480 | 0.1245770 | 0.1245445 | 0.1225920 | 0.985222x | -0.208% |
| v41-flash | CuteDSL MXFP4x8 | 128 | 0.2553775 | 0.2555690 | 0.2557300 | 0.2554570 | 0.999092x | +0.031% |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 0.3605150 | 0.3724980 | 0.3723385 | 0.3605780 | 0.968123x | +0.017% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 0.8264850 | 0.8869650 | 0.8873990 | 0.8319260 | 0.934651x | +0.658% |
| v41-flash | CuteDSL MXFP8 | 32 | 0.2134735 | 0.2136650 | 0.2135700 | 0.2133450 | 0.999025x | -0.060% |
| v41-flash | CuteDSL MXFP8 | 128 | 0.4622105 | 0.4620350 | 0.4626910 | 0.4624990 | 0.999982x | +0.062% |
| v41-flash | CuteDSL MXFP8 | 4096 | 0.5870430 | 0.5940990 | 0.5939240 | 0.5870595 | 0.988283x | +0.003% |
| v41-flash | CuteDSL MXFP8 | 16384 | 1.0059910 | 1.0069185 | 1.0097505 | 0.9977195 | 0.993574x | -0.822% |
| v41-flash | CuteDSL PER-TOKEN | 32 | 0.1323845 | 0.1347840 | 0.1346725 | 0.1323365 | 0.982426x | -0.036% |
| v41-flash | CuteDSL PER-TOKEN | 128 | 0.2716180 | 0.2718735 | 0.2718730 | 0.2713930 | 0.998647x | -0.083% |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 0.4071540 | 0.4195380 | 0.4193135 | 0.4071380 | 0.970722x | -0.004% |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 0.8079870 | 0.8304045 | 0.8306440 | 0.8085160 | 0.973182x | +0.065% |
| v41-flash | CuteDSL W4A4 | 32 | 0.1270885 | 0.1290085 | 0.1291205 | 0.1270725 | 0.984628x | -0.013% |
| v41-flash | CuteDSL W4A4 | 128 | 0.2632015 | 0.2630090 | 0.2631850 | 0.2634570 | 1.000883x | +0.097% |
| v41-flash | CuteDSL W4A4 | 4096 | 0.3520175 | 0.3581775 | 0.3577620 | 0.3525140 | 0.984066x | +0.141% |
| v41-flash | CuteDSL W4A4 | 16384 | 0.6380020 | 0.6582105 | 0.6570750 | 0.6365150 | 0.969004x | -0.233% |

## V3 helper-isolated election

Candidate patch `96cfbfbe7c2c779fcdaf9e46ce76f19d2989d879903f5037c8eefeb152925dc8` against clean `9b4721b08057d0a488c1f0236467acb75c48cd00`. [Full summary](full_screen_v3/results-v3/full-screen-v3-summary.json); [collection hashes](full_screen_v3/results-v3/collection.json).

Opening C0 reuses the exact same-GPU/source/tactic final V2 control; A1/A2/C3 are fresh. Prior receipt bytes, result hash and timestamps are explicitly validated. No V2 candidate measurements are reused.

Geomean: overall **0.983157x**, decode **0.994848x**, prefill **0.971603x**.

| Model | Backend | Tokens | C0 ms | A1 ms | A2 ms | C3 ms | C/A | Control drift |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| kimi-k3 | CuteDSL MXFP4x8 | 32 | 0.1710570 | 0.1716170 | 0.1715050 | 0.1710410 | 0.997016x | -0.009% |
| kimi-k3 | CuteDSL MXFP4x8 | 128 | 0.2917625 | 0.2969135 | 0.2968340 | 0.2912820 | 0.981974x | -0.165% |
| kimi-k3 | CuteDSL MXFP4x8 | 4096 | 0.4359070 | 0.4584985 | 0.4586275 | 0.4360190 | 0.950716x | +0.026% |
| kimi-k3 | CuteDSL MXFP4x8 | 16384 | 1.2330820 | 1.2793370 | 1.2837850 | 1.2622810 | 0.973564x | +2.368% |
| kimi-k3 | CuteDSL MXFP8 | 32 | 0.2995060 | 0.2995700 | 0.2992665 | 0.2994260 | 1.000159x | -0.027% |
| kimi-k3 | CuteDSL MXFP8 | 128 | 0.5207075 | 0.5211870 | 0.5210430 | 0.5205955 | 0.999111x | -0.022% |
| kimi-k3 | CuteDSL MXFP8 | 4096 | 0.6746445 | 0.6984370 | 0.6984210 | 0.6753005 | 0.966415x | +0.097% |
| kimi-k3 | CuteDSL MXFP8 | 16384 | 1.3718180 | 1.3777530 | 1.3926175 | 1.3335940 | 0.976552x | -2.786% |
| kimi-k3 | CuteDSL PER-TOKEN | 32 | 0.1823690 | 0.1824490 | 0.1825455 | 0.1819850 | 0.998245x | -0.211% |
| kimi-k3 | CuteDSL PER-TOKEN | 128 | 0.3064985 | 0.3124495 | 0.3123705 | 0.3063060 | 0.980770x | -0.063% |
| kimi-k3 | CuteDSL PER-TOKEN | 4096 | 0.4787080 | 0.4973640 | 0.4971555 | 0.4785795 | 0.962563x | -0.027% |
| kimi-k3 | CuteDSL PER-TOKEN | 16384 | 1.2361380 | 1.3152420 | 1.3130510 | 1.2378335 | 0.941285x | +0.137% |
| kimi-k3 | CuteDSL W4A4 | 32 | 0.1771375 | 0.1787540 | 0.1788655 | 0.1776660 | 0.992126x | +0.298% |
| kimi-k3 | CuteDSL W4A4 | 128 | 0.2973615 | 0.2981140 | 0.2984825 | 0.2973465 | 0.996835x | -0.005% |
| kimi-k3 | CuteDSL W4A4 | 4096 | 0.4150105 | 0.4299875 | 0.4298910 | 0.4148350 | 0.965073x | -0.042% |
| kimi-k3 | CuteDSL W4A4 | 16384 | 0.8975590 | 0.9508710 | 0.9514150 | 0.8975105 | 0.943638x | -0.005% |
| v3 | CuteDSL MXFP4x8 | 32 | 0.1005610 | 0.1005920 | 0.1007845 | 0.1007050 | 0.999451x | +0.143% |
| v3 | CuteDSL MXFP4x8 | 128 | 0.1358090 | 0.1356010 | 0.1356490 | 0.1356170 | 1.000649x | -0.141% |
| v3 | CuteDSL MXFP4x8 | 4096 | 0.2286090 | 0.2324975 | 0.2325295 | 0.2283855 | 0.982727x | -0.098% |
| v3 | CuteDSL MXFP4x8 | 16384 | 0.7025015 | 0.7276370 | 0.7448380 | 0.7147085 | 0.962468x | +1.738% |
| v3 | CuteDSL MXFP8 | 32 | 0.1654090 | 0.1652810 | 0.1652015 | 0.1652970 | 1.000676x | -0.068% |
| v3 | CuteDSL MXFP8 | 128 | 0.2302570 | 0.2300495 | 0.2300650 | 0.2300170 | 1.000347x | -0.104% |
| v3 | CuteDSL MXFP8 | 4096 | 0.3045780 | 0.3080980 | 0.3080500 | 0.3044180 | 0.988392x | -0.053% |
| v3 | CuteDSL MXFP8 | 16384 | 0.7858940 | 0.8040525 | 0.8245980 | 0.7960690 | 0.971334x | +1.295% |
| v3 | CuteDSL PER-TOKEN | 32 | 0.1063685 | 0.1061930 | 0.1067045 | 0.1064325 | 0.999547x | +0.060% |
| v3 | CuteDSL PER-TOKEN | 128 | 0.1429450 | 0.1457290 | 0.1457285 | 0.1428810 | 0.980678x | -0.045% |
| v3 | CuteDSL PER-TOKEN | 4096 | 0.2528500 | 0.2576815 | 0.2587695 | 0.2529940 | 0.979462x | +0.057% |
| v3 | CuteDSL PER-TOKEN | 16384 | 0.6835885 | 0.7091080 | 0.7080360 | 0.6835240 | 0.964696x | -0.009% |
| v3 | CuteDSL W4A4 | 32 | 0.1022405 | 0.1023050 | 0.1024010 | 0.1023050 | 0.999216x | +0.063% |
| v3 | CuteDSL W4A4 | 128 | 0.1381610 | 0.1413125 | 0.1409285 | 0.1383050 | 0.979539x | +0.104% |
| v3 | CuteDSL W4A4 | 4096 | 0.2112495 | 0.2154410 | 0.2162730 | 0.2113455 | 0.978877x | +0.045% |
| v3 | CuteDSL W4A4 | 16384 | 0.5619715 | 0.5866590 | 0.5863550 | 0.5622595 | 0.958412x | +0.051% |
| v41-flash | CuteDSL MXFP4x8 | 32 | 0.1225920 | 0.1236800 | 0.1236805 | 0.1226730 | 0.991529x | +0.066% |
| v41-flash | CuteDSL MXFP4x8 | 128 | 0.2554570 | 0.2554095 | 0.2551855 | 0.2553300 | 1.000376x | -0.050% |
| v41-flash | CuteDSL MXFP4x8 | 4096 | 0.3605780 | 0.3678740 | 0.3680340 | 0.3604830 | 0.979825x | -0.026% |
| v41-flash | CuteDSL MXFP4x8 | 16384 | 0.8319260 | 0.8787260 | 0.8864535 | 0.8757170 | 0.967405x | +5.264% |
| v41-flash | CuteDSL MXFP8 | 32 | 0.2133450 | 0.2133610 | 0.2136330 | 0.2137295 | 1.000189x | +0.180% |
| v41-flash | CuteDSL MXFP8 | 128 | 0.4624990 | 0.4626275 | 0.4627075 | 0.4625145 | 0.999653x | +0.003% |
| v41-flash | CuteDSL MXFP8 | 4096 | 0.5870595 | 0.5916995 | 0.5917960 | 0.5871565 | 0.992159x | +0.017% |
| v41-flash | CuteDSL MXFP8 | 16384 | 0.9977195 | 1.0179420 | 1.0069820 | 0.9997350 | 0.986434x | +0.202% |
| v41-flash | CuteDSL PER-TOKEN | 32 | 0.1323365 | 0.1339210 | 0.1339680 | 0.1324970 | 0.988594x | +0.121% |
| v41-flash | CuteDSL PER-TOKEN | 128 | 0.2713930 | 0.2713930 | 0.2715055 | 0.2713290 | 0.999675x | -0.024% |
| v41-flash | CuteDSL PER-TOKEN | 4096 | 0.4071380 | 0.4161305 | 0.4157780 | 0.4071220 | 0.978786x | -0.004% |
| v41-flash | CuteDSL PER-TOKEN | 16384 | 0.8085160 | 0.8224680 | 0.8231250 | 0.8080520 | 0.982362x | -0.057% |
| v41-flash | CuteDSL W4A4 | 32 | 0.1270725 | 0.1284005 | 0.1282560 | 0.1270090 | 0.989967x | -0.050% |
| v41-flash | CuteDSL W4A4 | 128 | 0.2634570 | 0.2630720 | 0.2630890 | 0.2630570 | 1.000671x | -0.152% |
| v41-flash | CuteDSL W4A4 | 4096 | 0.3525140 | 0.3560020 | 0.3562900 | 0.3519695 | 0.989038x | -0.154% |
| v41-flash | CuteDSL W4A4 | 16384 | 0.6365150 | 0.6507710 | 0.6504990 | 0.6368510 | 0.978556x | +0.053% |

## Codegen and disposition

Each passing source gate covers64 changing-route exact replays per source and32 FC1/FC2×PDL×format/topology core pairs, with no spills or changed geometry/storage/UMMA commits. V2 adds653 static SASS instructions summed across the core variants. V3 removes the fixed-lane query peeling and most reconvergence scaffolding but still adds197 summed static instructions. [Worst-case source-bound explanation](config5-codegen-audit.md), [independent opcode audit](gate/sass-opcodes-v3.json), [V2 decision](full_screen/decision-v2.md), [V3 decision](full_screen_v3/decision-v3.md).

One-owner participation does not imply a32x instruction reduction: the original warp-converged shared loads and arrivals already issue through SIMT aggregation. FlashMLA remains a useful protocol reference, but its different direct-response queue/work assignment does not establish a MoE performance win. These results justify retaining the existing full-warp response scheduler. Broad correctness/sanitizers remain deferred; neither rejected version was committed or pushed.
