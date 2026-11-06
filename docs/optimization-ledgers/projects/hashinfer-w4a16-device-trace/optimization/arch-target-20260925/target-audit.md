# Captured trace target audit

PASS: all four original tracker CUBINs declare **sm_103a**. Source `40d0ceb67aa67dbf366ff61f85309e8ef53aa743`; source+fixture SHA-256 `9a673e60c3e54ad5ebf064c2c32ad307a02cc73c20477dc79f13940c4f5447ee`.

CUBIN SHA-256 `c399006d8b25d26c9633d71d41d39a043358cd3c779da6a833e86fb19cdcf5cf`; decode context `6129cb7d0424eea6`. Each file contains one matching W4A16 MegaMoE function and 115 PMTRIGs. Four fresh CPU-only remote disassemblies hash identically to the earlier source/binding-audited SASS.

| Rank | Tracker PID | Capture PID | CUBIN target | ELF flags |
|---:|---:|---:|---|---|
| 0 | 12588 | 12928 | sm_103a | `0x6006702` |
| 1 | 12589 | 12929 | sm_103a | `0x6006702` |
| 2 | 12590 | 12930 | sm_103a | `0x6006702` |
| 3 | 12591 | 12931 | sm_103a | `0x6006702` |

Tracker rank mapping comes from the tracker pass’s four source-bound `W4A16_TRACE_JSON` records, not PID sorting. Capture PIDs are the separate native instrumented pass. All current local package/fixture bytes and copied inputs were rechecked against the successful trace audit.

The source facade resolves `get_cutedsl_target_arch` to `src/common/host_utils.py:5`, which reads `CuTeDSL._get_dsl().get_arch_enum()`. `bf16_nvfp4/megamoe_kernel.py:210` stores that active architecture. The frontend calls `cute.compile` at `frontend.py:371`; its compiler options control registers/O-level/IKET but do not hardcode SM100. Thus `Sm100W4A16MegaMoEKernel` and the `sm100` module path do not establish the actual binary target.

- The declared .target comes from original CUBIN disassembly; retained PTX was not present in this trace collection.
- This confirms this captured winner, not every historical benchmark target.
- Sm100 class/module naming is not evidence of compiler target.
- Source attribution inherits the direct harness pre-launch source snapshot and native tracker/config binding; no after-run source receipt exists.
