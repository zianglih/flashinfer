# W4 singleton cluster-rank audit

Retained by parent as an instruction cleanup; no latency speedup claim. Base `1054743780dda2919c1424124c1e3258248b8c19`, candidate kernel `8acbdcf47b61cbe6256ff21023a4d15e78b0cf6c1b8ffa0d6f9469afb806af17`.

- Gate: eight exact cases and56 reference graph replays per source;12 paired compiled kernels. Five singleton-CLC pairs remove exactly two non-NOP instructions, seven streams are identical. Registers remain128; zero local/stack and uniform spill/fill traffic.
- Timing:32 fixed-winner CAAC cells,128 independently verified medians/12,800 strict CUPTI samples. All-cell geometric speedup -0.14889%; decode +0.01738%; prefill -0.31489%.
- Twelve provably affected singleton-FC1/CLC cells: geometric speedup -0.00282%; worst EP V41F T4 -0.16454%. C1/C2=0.038848/0.038816ms; A1/A2=0.038912/0.03888ms. C spread -0.08237%, A spread -0.08224%.
- Production FC2 has activation_type=None and never uses CLC. Both selected cluster shapes are (1,1) in all13 singleton FC1 cells. Twelve have216–11840 problem clusters, above the148-SM max-SMEM one-CTA occupancy ceiling. TP V3 T4 has128 problem clusters; its actual occupancy return was not captured, so that one is excluded from affected statistics. All other19 cells have two-CTA FC1. No extra occupancy query or GPU run.
- No overlap: last GPU1/GPU2 W4 phases ended1793220481.7472048/1793220465.91337; scheduler gates started1793220855.6832664/1793220856.0236878. Unchanged/two-CTA prefill variation is preserved in the complete table and is not attributed to this instruction change.
- Source/helper/winner/cache/routing/GPU UUID/public-argv/100-sample-median and native source348-file bindings verified. No sanitizer or external baseline rerun.

Raw immutable archives: `gate-evidence.tar.gz` (120files, SHA `9e7cd01ea2d53e6995982c866e44b3097be40f9cd4866e0a36519105a13a4cbb`) and `perf-evidence.tar.gz` (1294files, SHA `460b19f951bd45f5d2a6287922bd21fb429385bf6671b53aa1b823a5c3ad4cd0`). Full32-cell values/spreads: `analysis/cells.csv`; exact source and audit bindings: `qualification.json`.
