# Retained partial-K sanitizer qualification

**PASS:** memcheck, synccheck and racecheck each completed **96 graph replays**
with clean tool summaries: **288 replays, 144 captured GEMM compilations total**.
The independent CPU audit rechecked all **610 artifact hashes** and matched all
**347 recorded source files** to clean retained commit
`2cfb06afd4a6e180af37615dd5f1cea1fc188691`.

- **Source:** the frozen checkout still reports base `d1767be1`; its unstaged
  tail-only bytes match the retained commit. Kernel SHA256 is
  `3fe308714e0c450d3370bdc1d4f57c17957e420421d0ff588447d72103b75f23`.
- **Environment:** C3 NVIDIA B300, GPUs1/2/3, shared
  `nvcr.io/nvidia/pytorch:26.05-py3` runtime (CUDA13.2), Compute Sanitizer
  **2026.3.0.0, build38855100**. Existing persistent native caches were reused.
- **Workload:** H512/I384, 257 tokens, top2, 96 local experts of192; six explicit
  configs `[0,3,5,6,8,9]` cover NVFP4 W4A4, per-token NVFP4, MXFP4x8 and MXFP8;
  SiTU/SwiGLU; N16/256; one/twoCTA; M128/256/512. Both static/shared-CLC and
  PDLoff/on execute balanced, skewed, empty-local and reactivated routes.
- **Coverage:** each tool captures48 GEMMs;20 have a partial K stage, and28 are
  aligned controls. Output storage bits agree across the same-source scheduling
  and PDL variants, and across all three tools. Empty/reactivated checks pass.
  This is **not an independent numerical-oracle test**, exhaustive tactic
  qualification, or a repetition of the earlier150-node manual suite.
- **Instrumentation:** options exactly match the tracked manual script's
  `_sanitizer_options(tool, "w4a4", True)` filter union. No suppressions or
  reduced checks were added. Memcheck uses `--check-tensor-ops no` and requests
  `-g-tmem-access-check` for all48 GEMM compiles at optimization level3.
- **Assembled guard evidence:** all48 memcheck cubins contain the compiler flag,
  nine named `__cuda_sm10x_tcgen05_guardrail_trap_*` symbols, corresponding SASS
  `BPT.TRAP` sites, and direct calls into the guard routines. The same PTX in
  synccheck/racecheck has only the two default deallocation guard routines.
  This proves compiled guard presence, not execution of every failing branch.
- **Codegen boundary:** PTX/cubin/SASS/resources are retained for every captured
  GEMM. The instrumented memcheck builds contain local-memory accesses and
  stack usage; **these are not production spill findings**. The corresponding
  synccheck/racecheck builds have zero static LDL/STL sites. Codegen capture
  does not cover every routing/quantization/finalize kernel; filter names alone
  do not prove that each named native function ran.
- **Excluded:** W4A16, fused finalize, Hopper/Rubin, full shape/dtype cross-product
  and timing. The inherited probe's `role=control` and text saying “No sanitizer”
  describe its original standalone use; the outer controller commands and tool
  receipts establish this campaign's actual instrumented execution.

The exact commands, environment/source bindings and GPU UUIDs are in
[`audit-receipt.json`](audit-receipt.json). The controller was launched as:

```bash
python3 run.py --tool memcheck --gpu 1
python3 run.py --tool synccheck --gpu 2
python3 run.py --tool racecheck --gpu 3
```

Each command uses the pinned2026.3 binary and runs `probe.py --role control
--config-ids 0,3,5,6,8,9 --hidden 512 --intermediate 384 --local-experts 96`.
The reusable independent audit is `python3 audit_evidence.py`.

## Raw successful summaries

All three `stdout.log` files end with:

```text
PASS 96 source-bound exact replays
```

Memcheck (`evidence/memcheck/sanitizer.log`):

```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
```

Synccheck (`evidence/synccheck/sanitizer.log`):

```text
========= COMPUTE-SANITIZER
========= ERROR SUMMARY: 0 errors
```

Racecheck (`evidence/racecheck/sanitizer.log`):

```text
========= COMPUTE-SANITIZER
========= RACECHECK SUMMARY: 0 hazards displayed (0 errors, 0 warnings)
```

## Initial helper failures, preserved separately

`evidence/attempt1/` is **not passing evidence**. Its memcheck process exited255
before target execution because the default-PATH sanitizer rejected
`--check-tensor-ops`. Its synccheck/racecheck processes exited1 when the helper
attempted to read a missing cached cubin artifact; their “0 errors” lines do not
make these incomplete runs pass. The relaunch selected the pinned2026.3 binary
and used a per-tool compilation working directory. No product source, checks,
or suppression policy changed. All initial logs, receipts and helper files
remain hashed in the610-file evidence manifest.
