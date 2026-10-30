# W4 paired SiTU: primary full26 screen

Unstaged candidate5e61d045 versus retained49c91adf. Same K3 EP8/TP8 public API, frozen routes/winners, source-bound native CUPTI100 samples/10warmups/cold-L2 graph replay, four phases C-A-A-C on the same GPU per arm. Raw1/2-token rows are preserved but excluded from retention. This is the primary campaign; the separate six-cell ACCA diagnostic does not replace these observations.

| Tokens | K3 EP8 | K3 TP8 |
|---:|---:|---:|
| 1 | -0.769% | +0.087% |
| 2 | +0.415% | +0.482% |
| 4 | -0.040% | -0.065% |
| 8 | +0.873% | -0.204% |
| 16 | -0.720% | +0.284% |
| 32 | -0.452% | +0.254% |
| 64 | -0.415% | +0.025% |
| 128 | -0.271% | -0.069% |
| 256 | -0.210% | +0.243% |
| 512 | +0.127% | +0.112% |
| 4096 | +4.376% | +1.068% |
| 8192 | +0.410% | +0.276% |
| 16384 | +0.090% | +0.460% |

Primary retention geomean: **+0.275% overall**, −0.047% decode4–64, −0.011% middle128–512, and +1.103% prefill4096–16384. Nine of22 retention cells are negative. Prefill has up to6.28% candidate repeat spread;37 clock-exception quartiles and one missing quartile remain in the raw evidence. The prefill average is not established as a stable benefit.

The EP16/32 losses are tight (−0.720%/−0.452%). Their E2E changes are +0.872/+0.833us, primarily accompanied by routing +0.864/+1.160us. FC1 spans only rise +0.120/+0.192us, while FC2 extension falls. FC1 starts approximately0.13–0.16us before the router ends in every phase; most extra routing time therefore occurs before FC1 has started. This localizes the recorded difference but does not identify its cause.

Exact winning-kernel captures at EP16/32 confirm24/48 fewer FC1 non-NOP instructions,96 registers,LOCAL0, and raw-identical FC2/finalizer images. Count deltas are only FADD/FMUL→FADD2/FMUL2, with same FTZ scalarSFUs and no FMA contraction. The compiler reorders SFUs and BF16 packing/shared stores within the epilogue, so instruction-count savings must not be described as unchanged scheduling.

Evidence:

- Primary raw: `evidence/w4-paired-situ-screen/1793379864881706000/data`.
- Complete original tables/components/clocks: corresponding `report/`.
- Native source/exact gate: `qualification-summary.json`; independent `audits/w4-paired-situ-gate-peer.json`.
- Tight-negative component replay: `negative-native/component-summary.json` and `COMPONENTS.md`.
- Exact winner native images: `negative-native-r2/evidence`; comparison `native-summary.json`, `schedule-boundary.json`, `RESULTS.md`.
- Root native peer: `audits/w4-paired-situ-negative-native-root.json`.
- Six-cell ACCA: separate held/launch receipts in `acca-screen/`; complete; see `ACCA.md` and `campaign-comparison.json`.

No retention decision or source commit has been made.
