Validated `83dfef8a6563` on B300 / CUDA 13.2 (`nvcr.io/nvidia/pytorch:26.05-py3`): **95 pytest + 11 Linux cache tests passed**; memcheck, synccheck and racecheck each passed **128 graph replays / 64 compiled GEMMs**, with zero sanitizer errors/warnings. Compact FC2 covers all four blockscaled formats, static/CLC and PDL off/on, including live full/partial slabs and changing route-index mappings. All 64 memcheck cubins have assembled TMEM guard evidence; tracked options keep the native tensor checker disabled. This is focused final-head validation; the earlier full 150-case sanitizer remains d1767 evidence.

```text
33 passed, 1311 warnings in 140.70s (0:02:20)
62 passed, 2424 warnings in 95.41s (0:01:35)
Ran 11 tests in 5.687s

OK
memcheck:  ERROR SUMMARY: 0 errors; PASS 128 source-bound exact replays
synccheck: ERROR SUMMARY: 0 errors; PASS 128 source-bound exact replays
racecheck: RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)
           PASS 128 source-bound exact replays
```

Upstream precommit and docs passed; [GPU CI is pending authorization](https://github.com/flashinfer-ai/flashinfer/actions/runs/40717866793/job/122920420727) and was skipped.

[Commands/raw results](@@VALIDATION_COMMANDS_URL@@).
