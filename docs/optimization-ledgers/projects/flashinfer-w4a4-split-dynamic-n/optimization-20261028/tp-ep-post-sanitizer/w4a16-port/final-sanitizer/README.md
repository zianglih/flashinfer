# Focused retained W4A16 sanitizer — skipped, never launched

The user explicitly requested skipping sanitizer to speed iteration. No controller or tool process launched, and no new sanitizer pass is claimed. The preparation below is preserved for reference; GPUs0/5/6 are released. The W4-only retained head is `640877340375fee0169f659a329d08b660c33eca`. This follows the prior focused `tail-sanitizer/run.py` pattern and reuses the byte-identical final combined `gate.py` helper (`9db344a7...`). It does not rerun the 150-case manual suite or add repository tests.

Selected existing cases: **16,17,18,19,28,29,32,33**.

| Cases | Workload | CTA group | Scheduler / PDL | Layout |
|---|---|---|---|---|
| 16–17 | Direct FC2 K576, M128/N16 and M256/N128 | 1 / 2 | ordinary / off | FC2 shared layout |
| 18–19 | Direct FC2 K640, M128/N16 and M256/N128 | 1 / 2 | CLC / off | FC2 shared layout |
| 28,32 | Public MoE H384/I576, M256/N128 | 2 | CLC / on | old64 / new16 |
| 29,33 | Public MoE H512/I640, M256/N128 | 2 | ordinary / off | old64 / new16 |

Each tool runs **8 exact cases,56 graph replays,12 owned W4A16 compiles**. Direct cases vary random/±0/cancellation, alpha1/±0, expert order, partial route extent, and inactive NaN/canary storage. Public cases replay changing routes. Assertions use the existing zero-tolerance shared W4A16 reference. “Ordinary” refers to scheduling; unsupported test-forced static MMA-N configurations are excluded.

The thin instrumentation wrapper adds `--opt-level 3` to W4A16 GEMM compilation, and memcheck alone adds `--ptxas-options='-g-tmem-access-check'`. All PTX/cubin/SASS/resources are captured immediately by the unchanged gate. The controller obtains exact tool options and kernel filters from the retained repository's `_sanitizer_options(tool, 'w4a16', False)`; no suppressions, omitted checks, or reduced racecheck reporting. Compute Sanitizer2026.3 is required at the existing verified package path.

For each assigned idle GPU, run the matching command with the final retained checkout's source/runtime receipts. Commands are templates until retention supplies the immutable SHA and paths:

```bash
python run.py --source "$source_json" --runtime "$runtime_json" \
  --expected-head "$retained_sha" --output "$campaign_results" \
  --tool memcheck --gpu 0
python run.py --source "$source_json" --runtime "$runtime_json" \
  --expected-head "$retained_sha" --output "$campaign_results" \
  --tool synccheck --gpu 5
python run.py --source "$source_json" --runtime "$runtime_json" \
  --expected-head "$retained_sha" --output "$campaign_results" \
  --tool racecheck --gpu 6
```

Each controller checks the device idle before launching; source HEAD must equal the retained SHA, tracked diff must be clean, qualified combined kernel bytes must match `cf503fe4...`, and all recorded source hashes/native-cache symlinks must verify. Native compilation caches persist; source-private DSL caches are bypassed to force instrumented codegen. Launch the controllers detached using the existing task remote mechanism, retaining each PID/command/stdout.

Acceptance requires all three return codes0, all8 cases/56 replays per tool, and the exact two-line clean tool summary. Source hashes recheck after each process. Every memcheck cubin must contain the compiler flag, non-deallocation TMEM guard symbols with `BPT.TRAP` instructions, and direct calls to access-check guards. The ELF/SASS parser was checked CPU-only on the prior retained guard evidence (9 traps/7 calls for memcheck,2 default deallocation traps for synccheck). Actual W4A16 assembled guards remain unqualified until this campaign runs.

Outputs per tool: `receipt.json`, `stdout.log`, `sanitizer.log`, `worker/result.json`, `worker/compile-options.json`, `worker/guard-audit.json`, and12 owned codegen directories. Keep failures and tool logs verbatim. Memcheck uses the repository's documented `--check-tensor-ops no` workaround; assembled guards prove instrumentation presence, not execution of every failing branch. Instrumented stack/local accesses are not production spill evidence. This is a bounded W4A16 unfused check, not fused-path, exhaustive-tactic, other-dtype, or cross-architecture qualification.
