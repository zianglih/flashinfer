# Rejected: R1 unsigned prepare indexing

Decision: reject the candidate. The retained source stays `33b7e5260132eb4ba2fdfdd97bd71a892f04a481`. No model-specific exceptions, dtype switches, or loop-policy knobs are added.

The one-file candidate is prepare `603dcdf240e23e958a35bee5f3666f83c51a078a1ab317ad48bdb15671d211e5` with patch `e271ae3a6833fdb4ec02bd5887ecdca43c0791189e22a0f14d9fd488ceddf674`. All348 source files are bound by `source-local.json`.

The full15-job EP/TP refresh collected468 cells and93,600 fresh CUPTI samples against93,600 saved retained samples. Displayed all-format geometric means were−0.087% EP and−0.120% TP. These original full results remain unchanged.

Fresh same-GPU C–A–A–C confirmation collected14 cells/5,600 samples. The decisive TP K3 prefill losses reproduced with both candidate pass medians slower than both control medians and every inspected sample stratum negative:

| TP K3,16,384 tokens | Full AA comparison | Fresh CAAC | First25 | Last25 | Last50 |
|---|---:|---:|---:|---:|---:|
| CuteDSL W4A4 | -2.287% | -2.468% | -2.682% | -2.533% | -2.325% |
| CuteDSL PER-TOKEN | -1.890% | -1.713% | -1.665% | -1.831% | -1.754% |

V41 EP W4A16 at8,192 tokens remained negative in the primary confirmation (-2.386%), but its pass intervals overlap and strata are mixed (first25 +0.059%, last50 -0.782%). It is not treated as the same stable separation evidence as the TP K3 rows.

Correctness qualification passed48 prepare graph replays per source and8 compiled pairs, including PDL on/off, changing/empty/reactivated routes and byte/padding checks. No spills/local memory were observed. V3 and BF16 variants reduce static instructions; K3 scaled grows85→301 static sites due compiler unrolling, with30→32 registers. This does not support a blanket claim of fewer executed instructions.

The source review clone is left untouched with only prepare.py unstaged for parent verification/removal. All GPUs are idle. No sanitizer, additional timing, source commit/push, or PR publication is performed. Preserve the helper scripts, original rows, raw archives, qualification receipts, and persistent native compilation caches.

Machine binding: `decision.json`. Complete full evidence: `full/evidence/raw`; confirmation: `confirmation/evidence/raw`; derived results remain under each campaign’s `analysis`/`report`.
