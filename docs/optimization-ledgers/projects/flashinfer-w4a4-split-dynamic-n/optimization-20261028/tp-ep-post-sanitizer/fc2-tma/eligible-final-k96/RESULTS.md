# Retained compact FC2 output: final handoff

Root retained the measured R3 implementation. The final patch is based on `21fbe72c6f70643a2b61c7461f42937dbfb307e9` and was integrated by root as `83dfef8a656384f5cd10db847602593bb6f9b2c6`. Its five files match the frozen source hashes. The inactive review checkout was removed after all tracked bytes matched canonical; `integration-receipt.json` records the check and preserved local caches. `source.json` binds the patch and exact source bytes.

The final delta from measured R3 is required formatting plus removal of the redundant host `output_rows` alias. `ast-equivalence.json` proves every GPU implementation AST is identical to the measured source and the host core differs only by that explicit alias substitution. `cleanup-only.patch` shows the entire final cleanup. All selected-file pre-commit hooks and `git diff --check` pass. No full timing repeat was needed for formatting. No new final-source GPU artifact identity is claimed.

The common-STMatrix R4 rewrite is rejected: 256 exact comparisons passed, but 48/128 kernels grew by up to 40 instructions and 44 grew by up to 18 registers. No R4 timing ran. Evidence remains in `../eligible-r4-k96/rejection-analysis.json` and `../eligible-r4-k96/RESULTS.md`.

## Retention evidence

Measured R3: `../eligible-r3-k96/RESULTS.md` contains the complete 144-cell four-model EP/TP C-A-A-C table, with 576 medians / 57,600 strict CUPTI samples. Geometric means of paired pass medians are used per cell. Source/winner/cache/route/GPU/argv and raw samples were independently verified. All previous baselines remain unchanged.

| Affected formats | Decode | Prefill | All |
|---|---:|---:|---:|
| EP | -0.009% | +0.027% | +0.009% |
| TP | -0.000% | +4.678% | +2.312% |

Largest affected loss is N3U EP W4A4 T16384: -2.153%; largest gain is +13.089%. No affected cell loses more than 3%. The unchanged W4A16 sanity cells remain visible in the full table.

Exact/codegen qualification: 256 paired output-bit comparisons, changing routing and graph replay, PDL off/on, static/CLC, one/two CTA, all four affected formats, 32/64-row stores, compact prefix/index invariants, and original caller maps unchanged. The 128 paired compiled kernels show identical FC1 and non-bulk FC2 instructions. Bulk FC2 adds 80–328 instructions with register deltas -14…+30. All have zero local/stack traffic; uniform-register spills/fills are explicitly reported and exist in both sources. No compact-candidate sanitizer run has been claimed; integrated-source qualification remains with root.

The BF16 output allocation is unchanged. Only eligible plans allocate int32 metadata; non-bulk plans compile it out. No new model, dtype or token policy, public knob or tactic axis. The automatic planner proof covers 336 cases and independent review covers 1260 admitted geometries including retained K96 alignment.
