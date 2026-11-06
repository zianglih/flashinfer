# Paired transpose: six internal waits and original caller completion

The candidate is based on retained `77391e28`. It omits only the new final helper load wait from the measured paired seven-wait variant, while retaining helper-entry completion, three store-to-load waits, two load-to-overwriting-store waits, and every original caller wait/release. One documentation sentence makes the final-load ownership obligation explicit.

The CUDA 13.2 PTX ISA section [Register dependencies, same thread](https://docs.nvidia.com/cuda/archive/13.2.0/parallel-thread-execution/index.html#tcgen05-memory-consistency-model-canonical-synchronization-patterns-register-dependencies-same-thread) guarantees true register dependencies from `tcgen05.ld` without an explicit wait. That does not order conflicting memory accesses. Returned-register permutations, arithmetic, conversion, shuffle input and output stores consume the loaded registers; separate explicit waits protect scratch reuse and accumulator ownership transfer. This argument does not rely on undocumented SASS scheduling.

| Path | Final read lifetime protection |
|---|---|
| Gated per-token FC1 paired up/gate | Original conditional wait immediately before early consumer release remains; otherwise next helper entry or final work-tile wait completes pending reads. |
| Ordinary gated FC1 single activated fragment | Same original early-release wait; final values can feed absmax/quantization by register dependency. |
| ReLU2 / nongated paired top/bottom | Original early-release wait remains before MMA can overwrite; no scratch store occurs during arithmetic/output. |
| FC2 `_scale_pack_transpose` | Bitcasts, permutations and vector stores consume register values. Original `_run_token_group` wait remains before early release. |
| Serial bottom-fragment reference | Next helper entry waits for preceding final reads before its first scratch store. Both original accumulator fragments were loaded before the first scratch store. The serial source remains a frozen reference. |
| Skipped protected slab/group | Existing wait before consumer release remains even when no helper is called. |
| FC2 partial-to-full transition | Native full-group path only reads TMEM. Its original wait precedes early release; ordinary paths reach the final work-tile wait. |
| No-overlap and nonrelease slabs | Next helper entry protects reuse; the unconditional work-tile load wait precedes advance/next work, ordinary release, and terminal deallocation. |
| Empty bulk output channel | Issues no reads; overlapping bulk output requires one channel tile, and previous work-tile reads completed at tile end. |

The actual-helper AST rectangle model verifies one- and two-fragment sequences, including the cross-alias middle phase. Six waits leave only final read regions pending; caller completion drains them. `caller-proof.json` enumerates the only helper callers and verifies unchanged original caller fence/release AST sequences. The model proves address/lifetime ordering, not arithmetic numerics or compiler resources; fresh paired codegen and the existing 39-case exact matrix remain required.

The earlier four-caller-wait deletion proposal is superseded. Its files and measured R1/R2 source snapshots remain unchanged. No timing claim is made for this six-wait composition.
