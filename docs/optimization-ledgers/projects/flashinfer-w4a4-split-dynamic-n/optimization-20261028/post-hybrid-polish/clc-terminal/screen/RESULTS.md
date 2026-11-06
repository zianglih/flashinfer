# CLC terminal peeling: representative fixed-winner screen

The affected CLC rows are effectively neutral overall: **+0.086%** geometric-mean speedup. This supports instruction simplification, not a broad performance claim. The worst affected row is a small, consistent **−0.459%** at N3U EP MXFP4x8, 64 tokens; it is retained in the record rather than dismissed as noise.

The screen uses the unchanged existing public benchmark and frozen winners/routes: four models, EP and TP, tokens 4/64/4096/16384, strict CUPTI, 10 warmups and 100 cold-L2 samples. Fifteen jobs contain 144 cells, four CAAC phases and 57,600 samples. No autotuning occurred during measurement. Actual GPU UUIDs, source hashes, managed-cache copies, output hashes, routes and selected tactics were verified, with no same-GPU phase overlap. The only test-source change is the terminal-ticket peel; no external baseline was rerun.

| Group | Cells | Overall | Decode | Prefill |
|---|---:|---:|---:|---:|
| CLC affected | 50 | +0.086% | +0.063% (30) | +0.121% (20) |
| CLC affected EP | 32 | +0.032% | +0.044% (28) | −0.056% (4) |
| CLC affected TP | 18 | +0.183% | +0.328% (2) | +0.165% (16) |
| Static selected control | 62 | −0.068% | −0.011% (26) | −0.108% (36) |
| Unchanged W4A16 control | 32 | −0.166% | −0.038% (16) | −0.294% (16) |
| All scaled formats | 112 | +0.001% | — | — |
| Entire screen | 144 | −0.036% | +0.014% (72) | −0.086% (72) |

Positive percentages mean the candidate is faster. Primary ratios use the geometric means of the two standard 100-sample median passes, without replacing them with time strata. CLC admission is reconstructed from frozen tensor shapes and the unchanged host predicate, with the existing B300 148-SM assumption explicitly retained in `../winner-classification.json`. Forty-nine rows admit CLC in both FC1/FC2; one admits it only in FC2. All 62 static rows explicitly select static scheduling.

## Small negative CLC cases

| Case | C1 / A1 / A2 / C2 (µs) | Speedup | First25 / last25 / last50 |
|---|---|---:|---|
| N3U EP MXFP4x8 T64 | 126.7205 / 127.249 / 127.361 / 126.721 | −0.459% | −0.415 / −0.490 / −0.434% |
| V41F EP MXFP8 T4 | 50.144 / 50.225 / 50.2565 / 50.1445 | −0.192% | −0.223 / −0.160 / −0.319% |
| V41F EP per-token T4096 | 409.0455 / 409.221 / 409.4775 / 408.517 | −0.139% | −0.078 / −0.316 / −0.180% |

Both candidate medians exceed both control medians in these rows. The first row costs about 0.58 µs; it is a small repeatable negative in this screen. Time strata are diagnostic only.

Large negatives also occur in paths unaffected by the patch: K3 EP W4A16 T4096 −6.805% and V41F EP static MXFP4x8 T16384 −3.888%. They cannot establish a causal CLC-loop regression. Correspondingly large positive control rows exist. These rows remain unchanged in the full CSV; no timing result was replaced or filtered out.

## Evidence

- `report/cells.csv`: all 144 primary rows.
- `report/classified-cells.csv`: all rows with CLC classification and time-stratum diagnostics.
- `report/classified-summary.json`: affected/control groups, worst rows and qualification boundary.
- `report/contract-audit.json`: source, CLI, physical-GPU, cache, observer and no-overlap audit.
- `evidence/verified.json`: all 2,000 archive hashes verified. Archive SHA256 `f4a109ad2f313adfcfcb38e07b6e9f3804ff6ca24857694570f8a0c46e246b37`.
- `../GATE.json`: separate exact/codegen qualification; all 16 tested static PTX and encoded SASS streams match the retained source, and all resource/spill counts are unchanged. CLC loop envelopes contain 10–14 fewer static sites, although the complete CLC kernel has 0–7 more sites from the separate terminal block. These are static counts, not executed instruction counts.

The candidate remains frozen. No additional benchmark or sanitizer is required by this report; the parent-owned composed refresh remains separately provisional.
