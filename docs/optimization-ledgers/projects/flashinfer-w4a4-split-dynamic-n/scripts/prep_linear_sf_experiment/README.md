# Destination-linear SF preparation: closed, unretained

The bounded decode screen passed its byte checks but saved only **0.04–0.08 µs** in preparation. Parent accepted closure without whole-chain or prefill extension. This is no claim of improved native MoE/TRT performance. Production and MegaMoE remain unchanged.

## Source and mechanism

Both independent clones are based on `98fd3566b5f945c100f48cddacf25deb2432cbc2`. Local candidate `../../flashinfer-prep-linear-sf-review` and remote `prep-linear-sf-98fd` have only `flashinfer/fused_moe/cute_dsl/blackwell/moe_prepare.py` modified, unstaged. Control is the clean `flashinfer-profile-98fd` / remote `profile-98fd` source. The remote control has the previously documented untracked `flashinfer/data` link; neither clone has staged changes.

- Control source SHA256: `ec2c70b178f828b769ab7d63128996bed8535f23f099591e1a5c046392bc292c`.
- Candidate source SHA256: `645691a9a0725ae1ae8491bf29a0259b7bf770625e5e81da38931a5b0d0efeca`.
- [Single-file patch](prepare-only.patch) SHA256: `f59e1b28042c7ab2d53688faac4f5502962846defdb10b0b8db0bd88578e1680`.

The valid-row payload loop is AST-identical after removing its old SF loop. Payload LDG/STG256 remains present in both generated cubins. Only SF word ownership changes: consecutive threads own consecutive destination `Uint32` words, invert the canonical 128-row SF layout, gather from `mapping[row] // top_k` for valid rows, and write zero otherwise. Each destination word has exactly one writer. The inverse was enumerated for 32 CPU cases, including zero atoms and non-power-of-two SF widths. A separate Int64 `while` loop retains 64-bit addressing without additional storage, barriers, allocation, launch, alignment requirements, or dimension-based dispatch. API, graph ownership, grid16 policy, PDL, full SF padding, and N16's extra physical rows remain unchanged.

This differs from the previously rejected shared-memory SF transpose and source-vector-width candidates: there is no SMEM tile or transpose, and source SF loads remain scalar words. The theoretical store-coalescing change is an address argument; no NCU traffic or bandwidth improvement was measured here. The candidate uses 32 registers versus control 30, with zero stack, shared, and local memory reported by `cuobjdump`.

## Exact checks and timing

Environment: C1 `fi-w4a4-pipeline-1025`, one B200, GPU2 UUID `GPU-894104cd-e66f-26ec-9d60-cc820c38ebc5`, `nvcr.io/nvidia/pytorch:26.05-py3`, driver580.178.04, CUDA13.2.78, torch `2.12.0a0+5aff3928d8.nv26.5.50603568`, CuTeDSL4.7.1, CUPTI Python13.4.0. Every execution sourced `scripts/recovery442/env_candidate.sh`, kept the candidate442 native cache epoch, and used private CuTe cache `cache/prep-linear-sf`.

**36/36 full-byte graph checks passed**, across six prep specializations and six changing-input graph replays each. Cases include FP4 and FP8 raw payloads, SF16/SF32, K64/K128/K7168, N16/N32, zero routes, shrinking/growing route counts, partial tiles, the N16 extra-row crossing of a 128-row SF atom, and capacity clipping. Source and destination allocations have poisoned padding and both-end canaries; invalid mappings are poisoned. Checks compare all payload/SF bytes, preserve invalid payload bytes and untouched SF suffixes, zero every required physical SF word, verify `mapping // top_k` original-token selection, and verify input/metadata immutability. Per-token scaling arithmetic is outside prep and was not changed or independently retested. FP8/SF16 cases exercise the raw prep geometry, not whole-GEMM format support.

The prep-only timing uses seed42 native NVFP4 input/routing, H7168/I2048, topk8/256 experts,32 local experts, N16, per-tensor activation scaling, and unfused finalize. Each process initializes routing once and retains the same input/metadata/output owners for both variants. It times only actual-source `prepare` calls, with allocation and the initial control native-chain invocation outside timing. Whole allocation bytes and input hashes are checked before and after every arm. Each arm has 10 warmups and 100 cold-L2 CUDA-graph/CUPTI samples; all 1,200 samples are preserved.

|Tokens|ABA medians, control / candidate / control (µs)|BAB medians, candidate / control / candidate (µs)|Geomean control/candidate|Mean arm-median saving (µs)|
|---|---|---|---:|---:|
|32|3.808 / 3.776 / 3.840|3.776 / 3.840 / 3.808|1.011268×|0.042667|
|128|4.000 / 3.904 / 4.064|3.968 / 4.0315 / 4.000|1.018856×|0.074500|

These small prep-only differences do not establish an end-to-end benefit. Optional 96-case prep matrix, sanitizer checks, candidate native-chain timing, and prefill guard were deliberately not run after the bounded result. This screen does not duplicate retained98fd numerical validation.

## Failed attempts and archive

- `history/int32_prelaunch`: unlaunched first source, replaced to preserve 64-bit SF indexing.
- `history/int64_shared_names` and `history/int64_range_unique_names`: two failed GPU compilations of the Int64 `cutlass.range` form; zero completed checks, no timing samples. Both reported an IR branch operand mismatch. A plain Int64 `while` compiled and passed. The compiler error alone does not prove a general DSL prohibition on Int64 ranges.
- `history/positional_capture` and raw `phase-t32-n16-r3`: timing helper asserted against positional host arguments before collecting samples. Signature binding fixed the observer; kernel source stayed frozen. The r4 phases completed successfully.
- Raw `commands-r3.json` contains the completed **r4** commands; the driver's output filename was not advanced. Earlier exact-r3 and failed phase-r3 logs/receipts remain present. `helper-sha256-prelaunch.json` and `manifest.json`'s `gpu_execution:false` record prelaunch states, not final status. [summary.json](summary.json) and [artifact-manifest.json](artifact-manifest.json) describe the final evidence.

Local raw archive: [raw.tar.gz](../../evidence/prep-linear-sf-98fd/raw.tar.gz), **1,402,133 bytes**, SHA256 `306e573ae17294475da7baea54bdfbb3d0ee23f58f931235ac79296372e93c04`. It preserves all remote logs, failures, source snapshots, helpers, full samples, per-phase cubins/PTX/SASS, environment, command receipts, and resource records. Per-phase named cubins are authoritative; the common CuTe dump directory can reuse generated filenames.

`python3 scripts/prep_linear_sf_experiment/summarize.py` performs CPU-only archive/source/sample/AST verification and regenerates the summary. The GPU driver refuses existing output paths; a deliberate future rerun requires fresh labels and GPU ownership. No more GPU work is planned. Final process query was empty and GPU2 was released.
