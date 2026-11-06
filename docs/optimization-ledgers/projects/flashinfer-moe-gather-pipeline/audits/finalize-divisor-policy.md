# Finalizer exact-divisor guard: closed without a prototype

The one-line removal of `and input_is_expanded` is not a new untested geometry. The old `geo128` proxy already measured the proposed H7168 permuted layout and repeatedly lost. No source edit, compilation, GPU call or new timing was made for this audit.

## Current callers and affected shapes

Retained49 `moe_finalize.py` SHA `2a7d7b445772d6c23d6b7f4cb2e37aceb886e46dd8dbb6998445b345ca478f95` selects 128 threads and four vectors above 1,024 tokens, then tries exact divisors 7, 6, 5 only for expanded inputs. Gathered swap passes `input_is_expanded=False` in `fused_moe.py`; W4 uses the same default through `moe_w4a16.py`. Non-swap and SM90 expanded callers remain eligible today. Fused finalization bypasses this kernel.

TP divides the intermediate width, not model hidden width; EP changes local experts, not hidden width. Replaying the actual constructor over all 468 recorded cells changes only 54 V3/V41F prefill cells:

| Model | H | Tokens affected | Vectors old → proposed | Hidden CTAs per token |
|---|---:|---|---|---|
| V3 | 7168 | 4096, 8192, 16384 | 4 → 7 | 2 → 1 |
| V41F | 5120 | 4096, 8192, 16384 | 4 → 5 | 2 → 1 |
| K3 | 3584 | None | 4 → 4 | 1 → 1 |
| N3U | 2048 | None | 4 → 4 | 1 → 1 |

The hypothetical deletion changes only launch geometry and its existing specialization key. Kernel addressing, contiguous BF16 strides, H-multiple-of-8/16-byte alignment checks, ordered FP32 accumulation, routing validity and PDL wait placement would be unchanged. The CPU proof checks 114,688 constructor cases and records every affected frozen cell in `finalize-divisor-policy.json`.

## Prior evidence

Authoritative raw files are under the old project `evidence/finalize-geometry-7196/raw/logs/finalize-geometry/`. The `geo128.py` host policy gives H7168 exactly seven vectors and one hidden CTA, the proposed shape here. Its kernel AST is identical to that experiment's control kernel.

| Raw file / permuted H7168 | Control phase medians (µs) | Candidate median (µs) | Diagnostic speedup |
|---|---|---:|---:|
| `geometry-r1.json`, T8192 | 50.0635 / 50.0800 | 52.5280 | −4.6761% |
| `geometry-r1.json`, T16384 | 91.1680 / 91.1840 | 94.4640 | −3.4807% |
| `shapes-r1.json`, T8192 | 50.1600 / 50.1285 | 52.5440 | −4.5671% |

All listed medians were recomputed from the old 100-sample records. These are B200/CuTe4.7.1 permuted proxy measurements with PDL off and sparse routing, not fresh B300 E2E evidence. Old captured registers rose 59 → 95, with no local/shared allocation. Current packed finalizer arithmetic differs from that old scalar implementation, so those resources are not a prediction of current codegen. The README's exclusion of permuted gains from the then-expanded native path does not erase these directly relevant permuted losses.

`geo128_prefetch` and H6144 gains are distinct changes/shapes. H8192 eight-vector, 32-thread, wide-256-bit and unbounded one-row trials also differ. Later `divisor-shapes-r1.json` kept permuted inputs at four vectors and cannot establish a benefit from deleting this guard.

The current V3 TP MXFP8 T16384 diagnostic uses this exact retained finalizer source: two hidden CTAs/token, 128 threads, 64 registers, zero dynamic SMEM, 84.82% DRAM peak and 92.08% long-scoreboard stalls. It supplies no causal evidence that fewer/wider CTAs improve latency. Preserve the existing guard; reopen only with a materially distinct mechanism and evidence.

Replay: `python3 audits/finalize_divisor_policy.py`. This is a source/history audit, not numerical qualification or a performance claim.
