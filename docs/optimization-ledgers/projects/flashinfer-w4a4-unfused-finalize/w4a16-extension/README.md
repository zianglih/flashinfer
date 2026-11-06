# W4A16 unfused-finalize extension to FlashInfer PR #5319

Work extends the existing independent clone on branch `codex/w4a4-unfused-finalize-pdl`, parent `fff0070cbeefda46e8f3c987a2bdc8e20584f062`. Tested and committed extension: `ca2692a62679336301758d1b83b193b3c5b1170c`. All five current CuTe files match the frozen measured source snapshot.

- Runtime stays official nightly `0.7.0.dev20260917`, with matching Python/cubin/JIT-cache packages and shared unchanged JIT directory. Both arms overlay the PR-base W4A16 host/kernel because those differ from nightly; only candidate adds the shared finalizer and early FC2 hint.
- Devbox: `fi-w4a16-finalize-0918`, C2 namespace ziangli, bare, 8 B300, explicit `nvcr.io/nvidia/pytorch:26.05-py3`, no size option. Live NGC catalog and release notes rechecked before creation: 26.05 is latest CUDA13.2 PyTorch image (26.06/26.07 are13.3 and26.08 is13.4).
- Setup: `scripts/setup_nightly.sh`; source snapshots: `source/baseline` and `source/candidate`; setup bundle and remote overlay hashes retained.
- Benchmark: `scripts/run_benchmark.sh ARM fused|unfused`, 1–16384 powers of two, H7168/I2048/top8, TP1, simulatedEP8, activation-quant flag (BF16 no-op), graphs+PDL+coldL2+CUPTI,10warmups/100timed, single native median perpoint andoneforward sweep perarm. Independent tactic caches; physicalGPU0.
- Validation: `scripts/run_validation.sh` (small40 + production4 + partial8 matched pipeline cases then30native tests, GPU1); `scripts/run_standalone.sh` (200permutedfinalizercases,GPU2). Details and limitations in `W4A16_VALIDATION.md`.
- First setup-bundle upload exceeded the Linux argv-size limit; fixed the remote helper to upload bounded chunks with SHA256 validation. No valid benchmark/test result came from that failed setup attempt. Subsequent runtime shared `moe_utils` helper needs a first-use C++ build; source iterations remain CuTe-only.

## Final results

- W4A16 full-MoE speedup: 14/15 points improve; 1.0814x at1token and1.0361x at16384. At8192 candidate is1.22% slower, with identical selected tactics. Independent autotuning differs at4/8/16tokens. One sweep; no statistical significance or universal non-regression claim.
- Native tests:30passed,965deprecationwarnings,50.85s; both W4A4 modes plusW4A16. External W4A16 pipeline:52phasecases byte-exact acrossbaseline/candidate, PDLoff/on, eager/graphs/changeddata, includingallnonlocal zero-work andH384partialtiles. Standalone:200casespassed (192nonempty native exact +8candidate zero-token no-op).
- Fixed-tactic cold-L2 Nsight diagnostics (20iterations): at4096FC2/finalize span174.6575→167.3455us, overlap0.656→11.6325us; at8192span259.986→248.962us, overlap1.120→10.320us. Both arms selected identical observed tactics. These separate partial-span diagnostics do not replace the full-MoE CUPTI medians or eliminate the observed8192regression.
- Full remote evidence:78files SHA256-verified against the remote manifest. `artifacts/final-remote-evidence.tar.gz`,107290726bytes,SHA256 `636b80f52bb17c094ab239c4fa43395706434e92ea3eae14e4040ec271cf843a`.
- `artifacts/summary/BENCHMARKS.json` and `.md` contain all45nativeCSVrows and detailedratios. HistoricalW4A4evidence remains scoped to parentfff0070c; W4A4performance wasnotrerun aftersharedhelperextension, butcurrentnativecorrectness testsrecheckbothscalingmodes.
- Commit hooks and changed-file checks passed; no upstream test orbenchmarkfile added. Final PRdiffagainsteb5f05be isfiveCuTeDSLfiles,+286/-4.


- GPU cleanup: managed `/usr/local/bin/h delete fi-w4a16-finalize-0918 -c c2 -n ziangli --force` returned0 and confirmed StatefulSet, Services, ConfigMap, Workload, anddevboxdeleted. Evidence preserved beforecleanup; see `artifacts/devbox-cleanup.txt`.

Publication verification: upstream PR #5319 is OPEN and draft at `ca2692a62679336301758d1b83b193b3c5b1170c`; its title, exact body, and five-file CuTe-only diff were read back from GitHub and verified. See `w4a16-extension/artifacts/published-pr.json` from the project root.


Full audit and cleanup published at `11b786f6fdda99d22eea62afbb82aab5cd5c412f`; PR remains OPEN/draft, exact body and five CuTe files verified from GitHub. Runtime logic is unchanged from measured `ca2692a`. Detailed audit: `audit/README.md` from the project root.
