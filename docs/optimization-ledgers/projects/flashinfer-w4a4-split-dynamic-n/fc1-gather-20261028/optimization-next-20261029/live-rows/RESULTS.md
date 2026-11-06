# Live-row Gather4 screen: needs refinement

The source bounds Gather4 payload issuance and expected transaction bytes to the actual 16-rounded MMA N in each CTA. SF loading and all publication/acquire barriers remain unchanged. This follows the newer MegaMoE dynamic-gather pattern without model or dtype selection.

Seven existing exact tests and all applicable pre-commit hooks passed. Five same-GPU C-A-A-C jobs produced 44 cells and 17,600 strict CUPTI samples, with fixed routes and tactics against fb66a27e. Source and observer receipts are in `evidence/`, and the complete raw phase medians are in `report/cells.csv`.

- Affected geometric mean: +0.014%.
- Decode (8 tokens): +1.195%; 256 tokens: +0.112%; prefill: -0.620%.
- N3U EP W4A4 4K regresses -6.834%, with 0.001% control and 0.179% candidate repeat spread. Its16K point regresses -1.777%, also stable.

Do not retain this version. The source remains in the active live-rows review copy while generated-code inspection investigates whether predicate/liveness pressure explains the prefill regression. Kernel SHA: `da641f71d962c0873bdd2e08854fae5348c761ed07c75f6e4eb1e80deb0095a0`.
