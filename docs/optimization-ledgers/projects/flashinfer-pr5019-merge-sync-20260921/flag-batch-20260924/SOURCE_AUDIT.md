# W4A16 MegaMoE fixed F4 versus F8 source audit

Date: 2026-09-24. Audited source: `../flashinfer` at
`19e8aebb541684df09e12cc79610338aa429a2cf`. This is a read-only source audit plus
a CPU-only enumeration check; it contains no new GPU measurements or numerical
validation. Source paths below are relative to that checkout.

## Current configuration and experiment isolation

`flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/autotune.py:17–45` returns eight
ordered candidates when in-kernel FC2 reduction is disabled:

- `group_hint`: 512, then 1024.
- For each group: `(256,128,256)`, then `(256,64,256)` MMA tiles.
- For each tile: `epi_warps`, then `reuse_dispatch_warps`.
- All use cluster `(2,1,1)`, two-CTA instructions, two dequantization warpgroups,
  atomic-counter scheduling, scheduler depth 2, `epi_flag_batch=(2,4)`, and F4.

The fixed-F8 experiment can use copies of these eight dictionaries changing
only `flag_batch` to 8. CPU AST enumeration confirmed exactly eight paired
dictionaries, the order above, and equality of every field except `flag_batch`.
Use the existing autotuner's `candidates=` argument, or a benchmark-only
override of its candidate factory. Passing only
`--megamoe-knobs='{"flag_batch":8}'` would bypass autotuning and would not be a
matched comparison of the eight-candidate searches.

Keep the native hot CUDA-graph GPU-event scorer and final cold-L2 CUPTI timer
unchanged. Each arm needs its own fresh knob cache. The experiment changes the
candidate policy only; it does not require changes to maintained kernel code
or the verbatim vendor drop.

## What flag batching changes

The call chain is frontend config → kernel constructor →
`W4A16TokenComm`, which inherits shared `TokenInPullTokenBackPush`:

| Source | Relevant behavior |
|---|---|
| `cute_dsl/megamoe/bf16_nvfp4/frontend.py:190–224` under `flashinfer/moe_ep/` | `apply_knobs` retains session numerical settings and invalidates compiled state/workspace when config changes. |
| `cute_dsl/megamoe/bf16_nvfp4/frontend.py:276` | Forwards `flag_batch` unchanged. |
| `cute_dsl/megamoe/bf16_nvfp4/megamoe_kernel.py:276,304` | Forwards F to transport and includes F in the kernel name. |
| `kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:413–417` | Constructor accepts F from 1 through 32; F is a Python compile-time integer. |
| `kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:578–598` | FC1 activation loading waits for the task's ready-counter threshold. |
| `kernel_src/sm100/cutedsl_megamoe/src/src/token_comm.py:1112–1146` | Every token's bulk store fully completes before its readiness address is accumulated; pending addresses are flushed at loop exit. |
| `kernel_src/sm100/cutedsl_megamoe/src/src/flag_batch.py:46–88,111–119` | Rotating lanes hold pending addresses; the batch fires at its threshold or phase change, with one GPU-release `+1` per occupied lane. |

F4/F8 controls dispatch-side FC1 input-readiness publication. Increasing F
allows more pending lanes to publish in one warp instruction episode while
delaying readiness of earlier tokens. It does **not** coalesce eight tokens
into one counter increment: eight tokens still require eight increments.
Dispatch passes a constant phase zero, so changing expert/counter address does
not itself flush the batch. Both values retain the unconditional tail flush.

F does not change payload TMA size, the per-token full bulk-store wait,
outstanding-store depth, buffer dimensions, workspace extents, or SMEM layout.
The normal frontend lifecycle still reallocates/recompiles when F changes, and
the kernel name distinguishes F4/F8. Compiler-generated resource usage can
nevertheless differ and should not be inferred solely from source dimensions.

`epi_flag_batch=(2,4)` is a separate epilogue publication policy and remains
fixed in this experiment. F4/F8 introduces no intentional arithmetic, weight
layout, activation, routing-weight placement, or combine-precision change.
That source conclusion is not a substitute for the run's output checks.

## Existing W4A4 pattern

`flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/shim/autotune.py:59–92`
tunes N128/N256 × F4/F8 × three return modes, giving 12 candidates with
in-kernel FC2 reduction disabled. W4A4 therefore already treats F as a curated
tactic axis. This validates the existing interface/mechanism, but does not
establish that F8 benefits the different W4A16 compute and fused staging/combine
pipeline.

## Why F4 was previously retained

Historical source:
`/Users/ziangli/playground/projects/flashinfer-w4a16-megamoe/w4a16_optimization_experiments.md:8374–8416`.
The earlier trial measured frozen source `99681e83066e76ede3dc4054582f130e96bc7da15dfe97c5ee3ebde9c60a3ebc`
on eight B300 GPUs in `hu-pdx-15`, CUDA 13.2 / DSL 4.7.1. Each fixed-F arm
searched four candidates, N128/N64 × epilogue/reused-dispatch return, with the
then-current group policy. It ran 1–8192 tokens, three warmups and 100 cold-L2
CUPTI samples per row, F4 followed by F8, using fresh caches.

| Historical metric | F8 relative to F4 |
|---|---:|
| Geometric latency ratio over 8–8192 | 1.016189412, or 1.62% slower |
| 4096-token latency | 5.933% slower |
| 8192-token latency | 4.592% slower |

F8 won several small-token cold rows, but their corresponding matched hot
scores did not show a clear advantage. At 4K and 8K, F8 was slower in all four
matched geometry/return pairs. Commit
`d6f8502b7f69da64e78641203917186280d01ebb` retained only F4 in the curated
catalog; manual F8 remained supported.

Limitations of that evidence: EP8 only; older four-candidate kernel; no 16K
measurement; serial whole-arm runs without confidence bounds or drift
adjustment; and the then-current retention range differed from today's decode
focus. Subsequent input-staging/final-combine fusion and the G1024 candidates
make a fresh EP4/EP8 comparison meaningful. The historical numbers must not be
presented as measurements of the current implementation.

## Decision criteria for this experiment

Use the existing paired-sweep methodology for both EP4 and EP8. Prioritize
decode 4–512 tokens, with EP4 the current optimization focus. Report 1/2 tokens
without using them in retention. Check 4096/8192/16384 prefill separately;
minor prefill loss can be acceptable for useful decode improvements, but should
be explicit. Do not add 1024/2048 back to the production retention workload.

Compare complete fixed-F4 and fixed-F8 AUTO results, actual selected tactics,
per-sweep stability, and matched-candidate tuner scores. Small changes on rows
where another tactic field also changes cannot be attributed exclusively to F.
Useful reproducible F8 niches can justify restoring the axis even without an
aggregate win. Restoring F4/F8 doubles the current eight-candidate default
search to sixteen, so noise-level wins alone would not establish its value.


## Small-token publication bound

`ep4-post-campaign-device-properties.json` and
`ep8-runtime/results/post-run-identity.json` confirm 148 SMs on every measured
EP4/EP8 B300 device, queried only after each full campaign exited. The frontend
uses `max_active_clusters = sm_count // 2` for these two-CTA candidates
(`frontend.py:249–253`, `frontend.py:351`); the persistent grid always launches
`(1, 2, max_active_clusters)` (`fc1_fc2_fuse_sched.py:184–189`). The kernel thus
passes `num_sms = 148` (`megamoe_kernel.py:465–466`), and shared token transport
has four dispatch warps per CTA (`token_comm.py:361–363`), for 592 pull warps per
rank. `dispatch_pull` assigns received routed tokens in this 592-warp stride
(`token_comm.py:869–870`, `token_comm.py:1142`), so even if every global route
lands on one rank, global N4/N8 at top-k8 produce only 32/64 pulls on that rank:
each active warp pulls at most one token. Neither F4 nor F8 can reach its batch
threshold before the common tail flush (`token_comm.py:1144–1146`). For these
small workloads, a measured F8 gain therefore cannot be explained by batching
more release publications. Compiler/code-layout, cache or system effects remain
possible; this is a source-level bound, not profiling that identifies the cause
of the cold-L2 timing difference. Both EP4 and EP8 use this verified grid. Do
not extrapolate exact random per-rank receive counts to larger token sizes
without recording those counts.

Relative paths above are under `flashinfer/moe_ep/cute_dsl/megamoe/bf16_nvfp4/`,
except shared `token_comm.py`, which is under
`flashinfer/moe_ep/kernel_src/sm100/cutedsl_megamoe/src/src/`.
