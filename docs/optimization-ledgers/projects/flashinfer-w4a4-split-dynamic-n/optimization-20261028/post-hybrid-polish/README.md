# Post-hybrid pipeline polish

## Retained result

Pushed `33b7e5260132eb4ba2fdfdd97bd71a892f04a481`; only `moe_swap_ab_kernel.py` changes. [Decision](composed/RETENTION.md), [source binding](composed/retained-source.json), [full refresh](composed/full/analysis/summary.json), and [verified PR publication](composed/publication/publication.json). The full EP/TP external-comparison tables and plots use all468 refreshed cases and unchanged saved controls. Timing is effectively neutral; these changes remove unnecessary recurring instruction/synchronization work. Four completed local review clones are removed; all evidence and caches remain.

The preparation index R1/R2 candidates are rejected. R1 passed exact qualification but its full468-cell EP/TP refresh was slightly negative; fresh same-GPU CAAC reproduced K3 TP16K losses of2.47% W4A4 and1.71% per-token. R2's forced loop policy did not establish a benefit. No conditional rescue policy was added. The completed preparation review clone was removed after348-file/patch verification; source evidence, raw results, helpers and persistent native caches remain. See `prepare-index/integrated-full/confirmation/`, [decision](prepare-index/integrated-full/RETENTION.md), and [cleanup receipt](prepare-index/integrated-full/review-cleanup.json).

Fresh NSYS/NCU evidence is under `profile/` and `prepare-combine-ncu/`. Prepare plus combine account for roughly37–44% of the measured non-overlapped TP16K timeline in the two profiled MXFP4x8 cases; combine reaches79–86% DRAM throughput. These are diagnostic observations, not retention timing. The remaining large TP prefill gaps versus old fused MX implementations are not closed by this round. All eight GPUs are idle after the completed confirmations.

## Initial plan and execution history


Baseline: retained PR7290 commit61c2c367. Canonical source remains clean while
each active experiment has an independent project-local review clone.

The existing eight-B300 C3 devbox fi-moe-descriptor-recover-1028 is reused,
with NVIDIA PyTorch26.05-py3/CUDA13.2 and persistent native compilation caches.
Inventory verified all eight GPUs idle before this round.

- `sf-tail`: copy only the compile-time valid scale-factor prefix into TMEM
  for a peeled final K stage. No TMA, transaction-count, ring, layout or tactic
  change. Review: `flashinfer-sf-tail-review/`; qualification ownsGPU7.
- `fc2-drain`: skip final bulk-store drain/join only when no full slab issued
  any TMA store. SIMT-only tail calls have no pending output-SMEM read.
  Review: `flashinfer-fc2-drain-review/`; qualification ownsGPU6.
- `clc-terminal`: peel the one terminal metadata ticket out of the valid CLC
  ticket loop, preserving acquire-before-cancel and valid padding ticket draining.
  Review: `flashinfer-clc-terminal-review/`; qualification ownsGPU5.
- `profile`: fresh source-bound V3/K3 TP8 MXFP4x8 16K NSYS captures onGPUs0/1,
  preserving public functional-API paths, winners and routes. Diagnostic timing
  only; it does not replace CUPTI retention evidence.

After focused exact qualification, screen candidates independently with the
public benchmark, frozen winners, same-GPU C-A-A-C,10warmups/100strictCUPTI
cold-L2graph samples per pass. Four models, EP/TP, tokens4/64/4096/16384;
all supported scaled formats plus unchanged W4A16 sanity. Keep current
unsupported comparator cases excluded. NVFP4 includes initial quantization.
No sanitizer or external-baseline rerun. Broaden retained candidates to the
full13-token matrix before updating published performance claims.

The remote control snapshot predates the commit operation (HEAD61249 plus
the retained patch), but all348 relevant source files are byte-identical to
61c2. Qualification and benchmark receipts bind hashes, not just Git labels.
