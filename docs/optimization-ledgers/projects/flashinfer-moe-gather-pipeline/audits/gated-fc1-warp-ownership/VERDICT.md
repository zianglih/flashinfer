# Gated FC1: 32 channels × 16 tokens per warp

Closed without a prototype. With the retained up16/gate16 weight layout and MMA/TMEM allocation, the proposed direct ownership is not legal: one warp can load only half of the raw rows needed for 32 gated channels. Reducing its token count changes TMEM columns, not the permitted rows. A legal post-load redistribution would exchange full activation fragments across warps and still need publication/reuse ordering; it is more work than the existing exchange of maxima.

Source: retained `bf072d26b163e71458e7e4dfb12e615b19bd2c9a`, swap kernel SHA `788b7f58267a773f049b25216d689ab6f60649ec168e1d278e0f3ef8ae6c8e17`. The CPU-only [mapping proof](mapping-proof.json), replayed by [prove_mapping.py](prove_mapping.py), binds the actual helper permutations and CUTLASS copy-traits file. No source edit, compilation or GPU execution.

## Hardware and current ownership

CUDA 13.2.2 PTX §9.7.16.8.1 restricts each warp, by its index within a warpgroup, to one 32-row TMEM region: warp 0 uses rows 0–31, warp 1 uses 32–63, and so on. All columns are available, but a warp cannot load a neighboring warp's rows. TMEM load/store addressing also requires a uniform address within the warp. [Official PTX specification](https://docs.nvidia.com/cuda/archive/13.2.2/parallel-thread-execution/index.html).

`prepare.py:_cute_dsl_gated_weight_group_size` and `_interleave_linear_and_gate` preserve `[up16, gate16, up16, gate16, ...]`. Consequently, each warp's 32 raw rows contain only 16 post-activation output channels. `_run_token_group` derives `scratch = ptr + warp*(32<<16)`, loads up and gate at row offsets 0 and 16, and ultimately stores output channels at `channel_start//2 + warp*16`.

For `Ld16x64b.x16`, the FP32 copy-traits mapping is:

```
channel row = 8*(lane & 1) + lane//4
token column = 2*register + ((lane>>1) & 1)
```

Replaying every load, store and retained permutation of `_blockscaled_transpose16x32` produces `lane=token, register=channel` for all 512 values of one fragment and all 1,024 values of the paired up/gate path. The one-fragment and paired paths stay inside the same 32-row warp-owned scratch. A virtual channel tile changes a column range; its next 16-channel output block is not the neighboring SF32 half. Two-CTA MMA does not widen one warp's local TMEM row access.

The desired 32-output-channel block contains 64 raw up/gate rows. For each warp's proposed 16 tokens, 512 of 1,024 required raw values are in the neighboring warp's inaccessible region. A warp shuffle cannot repair this because it is warp-local.

The local Blackwell and Rubin MegaMoE epilogues independently document the same `regs_in_pair_threads` boundary: gated FC1 yields 16 intermediate values per token per warp, and SF32 joins adjacent warps through shared memory. Rubin's `TmemTranspose32x32Inplace` combines the two raw up/gate halves; it does not make 32 gated outputs warp-local.

## Cost of a legal redistribution

| Per 32-token, four-warp slab | Retained maxima exchange | Redistribute activated values into 32-channel × 16-token warps |
|---|---:|---:|
| Shared payload written/read | 512 B / 512 B | At least 4,096 B / 4,096 B |
| Cross-warp ordering | Publish + scratch reuse | Still needs publish + reuse, or additional buffering/state |
| TMEM transpose | Retained | Still needed before the proposed post-transpose exchange |
| Register ownership | 16 channels per thread, one token | Can retain 16 values/thread using two lanes/token; extra exchange/address lifetime remains |

The 8× traffic lower bound sends half of each warp's 16-channel × 32-token fragment to its neighbor. Exchanging only the maxima instead reduces to the current algorithm. Processing 32 channels in one active lane instead would enlarge its working fragment; that is optional, not an unavoidable register-count prediction. Neither form is a measured improvement. A full new shared-memory transpose would be a separate redesign, not free elimination of two barriers.

## History exclusion

The bounded ledger search found no exact prior 32-gated-channel × 16-token experiment, but these related mechanisms are closed:

- `native-tmem-fc1-screen/RESULTS.md`: native eight-channel × two-token lane ownership and shuffle-based quantization; N3U EP 16K W4A4 −16.04%, per-token −17.30%. It retained the SF32 exchange and is not this proposal.
- `shared-fp32-transpose-screen-r2/RESULTS.md`: shared FP32 transpose, −1.638% overall and −2.898% prefill; unchanged-stage cases also regressed. This is not permission to try another shared transpose without a new signal.
- `ld-red-epilogue-audit-7739/VERDICT.md`: retained physical rows mix tokens, so row reduction cannot replace the token-wise maximum.
- `optimization-20261028/warp-polish/epilogue/README.md`: adjacent-pair 64-thread barriers retained both waits and were rejected (−0.094% overall).

The first three paths are relative to the old project's `fc1-gather-20261028/optimization-next-20261029/`; all original evidence remains untouched. This lead stops at the hardware/ownership boundary. Slab-indexed maxima scratch, if considered separately, does not require the illegal row remap.
