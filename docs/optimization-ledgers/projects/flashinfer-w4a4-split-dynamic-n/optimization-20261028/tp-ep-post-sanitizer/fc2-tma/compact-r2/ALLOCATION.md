# Compact R2 allocation

BF16 scratch capacity equals the control: `tokens * top_k * hidden * 2` bytes. Additional metadata is four bytes per expanded route plus four bytes per reserved routing tile; no host readback, capacity-policy changes, or new alignment contract.

| Topology/model | Tokens | BF16 scratch MiB (both) | Extra metadata KiB range | R1 extra BF16 MiB avoided |
|---|---:|---:|---:|---:|
| v3 EP | 4 | 0.438 | 0.250–0.250 | 6.562–13.562 |
| v3 EP | 64 | 7.000 | 2.242–2.242 | 6.562–6.562 |
| v3 EP | 16384 | 1792.000 | 514.121–516.121 | 54.250–108.500 |
| v41-flash EP | 4 | 0.234 | 0.188–0.188 | 3.516–7.266 |
| v41-flash EP | 64 | 3.750 | 1.910–1.945 | 14.062–29.062 |
| v41-flash EP | 16384 | 960.000 | 387.371–387.371 | 118.750–118.750 |
| kimi-k3 EP | 4 | 0.438 | 0.500–0.500 | 6.562–6.562 |
| kimi-k3 EP | 64 | 7.000 | 4.547–4.660 | 11.484–23.625 |
| kimi-k3 EP | 16384 | 1792.000 | 1032.434–1032.434 | 97.125–97.125 |
| nemo3-ultra EP | 4 | 0.344 | 0.598–0.598 | 3.719–3.719 |
| nemo3-ultra EP | 64 | 5.500 | 5.832–5.914 | 7.750–15.750 |
| nemo3-ultra EP | 16384 | 1408.000 | 1413.746–1419.246 | 31.500–63.000 |
| v3 TP | 4 | 0.438 | 0.250–0.250 | 6.562–13.562 |
| v3 TP | 64 | 7.000 | 3.062–3.062 | 52.500–52.500 |
| v3 TP | 16384 | 1792.000 | 514.996–514.996 | 892.500–892.500 |
| v41-flash TP | 4 | 0.234 | 0.188–0.188 | 3.516–7.266 |
| v41-flash TP | 64 | 3.750 | 3.000–3.000 | 56.250–56.250 |
| v41-flash TP | 16384 | 960.000 | 386.992–386.992 | 955.000–955.000 |
| kimi-k3 TP | 4 | 0.438 | 0.500–0.500 | 6.562–6.562 |
| kimi-k3 TP | 64 | 7.000 | 7.531–7.531 | 91.875–91.875 |
| kimi-k3 TP | 16384 | 1792.000 | 1035.473–1035.473 | 777.875–777.875 |
| nemo3-ultra TP | 4 | 0.344 | 0.688–0.688 | 5.156–5.156 |
| nemo3-ultra TP | 64 | 5.500 | 7.719–7.719 | 30.000–30.000 |
| nemo3-ultra TP | 16384 | 1408.000 | 1415.492–1415.492 | 510.000–510.000 |

Per-cell source receipts and unchanged routing-capacity formula are preserved in `allocation-cells.csv`. Host allocations and descriptor construction are outside the warmed CUDAgraph GPU timer. The additional indirect index load and prefix work are inside the GPU graph and must pass the same EP/TP CAAC retention screen.
