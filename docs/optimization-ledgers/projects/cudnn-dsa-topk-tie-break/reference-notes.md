# Standalone DSA top-k tie-break references

Source audit only. These are existing owned local snapshots, not a claim about the latest released packages. No GitHub operations, account changes, source edits, or GPU tests were performed for this note.

## Provenance

| Project | Exact inspected commit | Local checkout |
| --- | --- | --- |
| cuDNN Frontend | `7371bd889683b99064c044f185bcdb1f5ff516c8` | `/Users/ziangli/playground/projects/miles-dsa-backend-audit/cudnn-frontend` |
| FlashInfer | `f81c30caa94c279618c6393072c3478df423153b` | `/Users/ziangli/playground/projects/flashinfer-pr4421/flashinfer` |
| CCCL | `b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4` | `/Users/ziangli/playground/projects/flashinfer-cub-topk-gap-audit/cccl` |

Inspected reference paths are clean relative to their recorded HEADs. The cuDNN source is the prior FP32-head-weight branch; the top-k files are outside that change.

## Contract

FlashInfer `TopKTieBreak`: NONE=0, SMALL=1, LARGE=2. SMALL/LARGE choose the lower/higher original source-column indices among equal boundary keys; they do not require stable output-slot order. See [Python enum](https://github.com/zianglih/flashinfer/blob/f81c30caa94c279618c6393072c3478df423153b/flashinfer/topk.py#L41) and [API contract](https://github.com/zianglih/flashinfer/blob/f81c30caa94c279618c6393072c3478df423153b/flashinfer/topk.py#L549).

CCCL separates selected-set determinism/tie policy from output ordering. A concrete tie preference requests `determinism::gpu_to_gpu`, while `output_ordering::unsorted` remains valid; this is not a promise of deterministic output slots. See [DeviceBatchedTopK contract](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/device/device_batched_topk.cuh#L378).

Both inspected implementations compare radix-transformed bit keys without signed-zero canonicalization. Therefore `+0` and `-0` are distinct keys (`+0` ranks higher for largest-K), and NaNs follow transformed sign/payload ordering rather than a universal Torch-compatible NaN policy. Ties are equality of the selection key. Preserve cuDNN's existing bit ordering instead of introducing zero/NaN normalization with this feature:

- [FlashInfer FilteredTopKTraits](https://github.com/zianglih/flashinfer/blob/f81c30caa94c279618c6393072c3478df423153b/include/flashinfer/topk.cuh#L2444): FP32 coarse key at 2449, exact key at 2458; FP16/BF16 traits at 2468/2488.
- [CCCL extract/identify radix keys](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/device/dispatch/dispatch_topk.cuh#L74), using [floating-point TwiddleIn](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/util_type.cuh#L937).

## Efficient algorithm reference

FlashInfer's [DeterministicContiguousCollect](https://github.com/zianglih/flashinfer/blob/f81c30caa94c279618c6393072c3478df423153b/include/flashinfer/topk.cuh#L300) scans the original row in forward/reverse contiguous tiles, counts matching pivot keys with a block prefix scan, emits only the first remaining-K matches, and stops early. It uses four items per thread. The boundary invocation is [collect_det_eq_pivot](https://github.com/zianglih/flashinfer/blob/f81c30caa94c279618c6393072c3478df423153b/include/flashinfer/topk.cuh#L2773). Strictly better winners can retain atomic unordered placement.

CCCL uses the same index-ordered principle but narrows the scan to the boundary-crossing CTA/tile, with known-all/known-none portions retaining cheap placement. See [set-determinism and reverse direction](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/agent/agent_batched_topk_cluster.cuh#L245), [cross-CTA prefixes](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/agent/agent_batched_topk_cluster.cuh#L1220), and [boundary-only final filter](https://github.com/NVIDIA/cccl/blob/b1fa3f6c3bfd0e05b6f673229b6c7580255e47e4/cub/cub/agent/agent_batched_topk_cluster.cuh#L2086).

For cuDNN's one-CTA-per-row standalone path, a single forward/reverse pivot scan is the smaller adaptation. Worst-case scan work is O(row length), not O(K * number of ties); all-equal rows terminate after approximately K examined entries. Unique-value/fully-selected-bin cases already exit radix refinement before the final unresolved tie branch, so no scan is necessary there.

## Review of proposed cuDNN implementation

Proposal: retain current final atomic tie selection to obtain an exact pivot; after the final candidate fence/barrier, read `score[s_indices[K - remaining]]`, scan original row in the requested direction, and overwrite only the last `remaining` slots. No new kernel, global scratch, or default-path operations.

This is a sound minimal implementation, subject to these details:

1. Invoke after **both** shared-memory and global-spill candidate loops are finished and visible. Reading a selected tie slot before that point races the existing writes. The first trailing tie slot is valid when `remaining > 0`.
2. Keep strict winners in `[0, K-remaining)`. Only rewrite tied slots; do not sort the full output or perturb scores.
3. Reuse dead `s_histogram` storage for warp-scan scratch: its 257 entries exceed the maximum 32 warp totals. Existing `s_warp_sums` holds only eight histogram warp totals even when the CTA has 512/1024 threads; it cannot serve a full-CTA scan without resizing.
4. Pass the actual CTA thread/warp counts and request the total. [block_prefix_sum_kernel](https://github.com/zianglih/cudnn-frontend/blob/7371bd889683b99064c044f185bcdb1f5ff516c8/python/cudnn/deepseek_sparse_attention/indexer_top_k/block_scan.py#L58) has no final barrier after reading shared warp totals (lines 94–103). Add a CTA barrier after each tile consumes totals/emits, before the next tile overwrites scratch. Every thread must reach the same barriers and make the same loop-exit decision.
5. Predicate tail loads before reading a score. For row windows, scan `row_start .. row_start+length` and emit the original source index. Rejecting tie mode with the private candidate-merge path is appropriate: physical candidate positions there are not original source indices.
6. Make the mode a compile-time specialization, include it in both object and kernel-cache keys, and leave NONE compiled out. Do not add deterministic output ordering or GPU-to-CPU reads.
7. Keeping old atomic tie writes adds no new atomic work relative to the existing implementation, but the opt-in scan rereads some scores. Benchmark rare/sparse boundary ties at long context as well as all-equal/tie-heavy rows; the former can scan most of a row. Vectorizing two/four items per thread is a later tuning option if measurements justify its code cost.

Avoid the compressed path's running atomic-min insertion algorithm as the model for this feature: it can take O(K) atomics per tie. Its existing deterministic policy also prefers SMALL and belongs to a separate combined forward/top-k API.

## Verified FlashInfer PR references (2026-10-01)

Public GitHub metadata and PR commit lists were read with `gh` after selecting and verifying account `zianglih`; the active account remains `zianglih`. No GitHub content was changed.

- [FlashInfer #3095 — feat: implement configurable `tie_break` for filtered topk](https://github.com/flashinfer-ai/flashinfer/pull/3095). Author: `zianglih`. Created 2026-04-17 00:02:53 UTC; merged 2026-04-22 00:17:16 UTC. Introduced NONE/SMALL/LARGE and the shared tie-break API. Its original implementation also promoted deterministic output behavior; cite the follow-up below for the current separation.
- [FlashInfer #4295 — perf(topk): skip output index sort for tie-break selection](https://github.com/flashinfer-ai/flashinfer/pull/4295). Author: `zianglih`. Created 2026-07-31 09:56:53 UTC; merged 2026-08-05 17:19:41 UTC. Separates deterministic boundary selection from deterministic output ordering; plain tie-break with `deterministic=False` skips the index finalizer, while transforms retain required remapping. This is the closest precedent for deliberately omitting output-order guarantees in the cuDNN feature.
- [FlashInfer #4442 — feat: CUB `DeviceBatchedTopK` top-k backend with variable-length support](https://github.com/flashinfer-ai/flashinfer/pull/4442). PR author: `NaderAlAwar`. Created 2026-08-10 13:46:03 UTC; merged 2026-08-27 16:39:20 UTC. Integrates CUB into plain and transformed Top-K with tie policies, device-read variable lengths, CUDA graphs, and dispatch gates. Verified `zianglih`-authored contributions in its commit list:
  - [`fc685815334bad5536fe59b1602bf0b029c5df90`](https://github.com/flashinfer-ai/flashinfer/pull/4442/commits/fc685815334bad5536fe59b1602bf0b029c5df90): Move CUB transform tail padding into C++.
  - [`f1af586521e064093b4c5540e97112697a96912f`](https://github.com/flashinfer-ai/flashinfer/pull/4442/commits/f1af586521e064093b4c5540e97112697a96912f): Consolidate CUB tie-break coverage.
  - [`812cbb4305743689c9db59f8464e1c8499a8b5c4`](https://github.com/flashinfer-ai/flashinfer/pull/4442/commits/812cbb4305743689c9db59f8464e1c8499a8b5c4): Expand tie-break test matrices.

Suggested concise PR-body reference: “Follows the SMALL/LARGE boundary-selection contract introduced in FlashInfer #3095 and separated from output ordering in #4295; also references the CUB integration in #4442 (authored by Nader Al Awar, with my padding and tie-coverage contributions).” Avoid claiming authorship of #4442 itself or transferring its benchmark results to the cuDNN implementation.
