# Routed FC2 allocation audit

Source-derived capacity with 87 actual frozen EP/TP winner cells at4/64/16384 tokens. No allocation-policy change. Existing capacity already caps active experts by `min(local_experts, tokens*top_k)`.

Exact formula: `tile * (min(E,L) + max(E-L,0)//tile)` where `E=tokens*top_k`, `L=local_experts`. All reserved rows are allocated regardless of actual route balance; GPU live-tile count does not resize graph storage. New BF16 scratch uses `2*hidden*routed_capacity` versus `2*hidden*E`.

| Topology/model | Tokens | Route tiles across formats | Current FC2 MiB | Candidate FC2 MiB range | Ratio range |
|---|---:|---|---:|---:|---:|
| v3 EP | 4 | 16,32 | 0.438 | 7.000–14.000 | 16.000–32.000× |
| v3 EP | 64 | 16 | 7.000 | 13.562–13.562 | 1.938–1.938× |
| v3 EP | 16384 | 128,256 | 1792.000 | 1846.250–1900.500 | 1.030–1.061× |
| v41-flash EP | 4 | 16,32 | 0.234 | 3.750–7.500 | 16.000–32.000× |
| v41-flash EP | 64 | 16,32 | 3.750 | 17.812–32.812 | 4.750–8.750× |
| v41-flash EP | 16384 | 128 | 960.000 | 1078.750–1078.750 | 1.124–1.124× |
| kimi-k3 EP | 4 | 16 | 0.438 | 7.000–7.000 | 16.000–16.000× |
| kimi-k3 EP | 64 | 16,32 | 7.000 | 18.484–30.625 | 2.641–4.375× |
| kimi-k3 EP | 16384 | 128 | 1792.000 | 1889.125–1889.125 | 1.054–1.054× |
| nemo3-ultra EP | 4 | 16 | 0.344 | 4.062–4.062 | 11.818–11.818× |
| nemo3-ultra EP | 64 | 32,64 | 5.500 | 13.250–21.250 | 2.409–3.864× |
| nemo3-ultra EP | 16384 | 128,256 | 1408.000 | 1439.500–1471.000 | 1.022–1.045× |
| v3 TP | 4 | 16,32 | 0.438 | 7.000–14.000 | 16.000–32.000× |
| v3 TP | 64 | 16 | 7.000 | 59.500–59.500 | 8.500–8.500× |
| v3 TP | 16384 | 256 | 1792.000 | 2684.500–2684.500 | 1.498–1.498× |
| v41-flash TP | 4 | 16,32 | 0.234 | 3.750–7.500 | 16.000–32.000× |
| v41-flash TP | 64 | 16 | 3.750 | 60.000–60.000 | 16.000–16.000× |
| v41-flash TP | 16384 | 256 | 960.000 | 1915.000–1915.000 | 1.995–1.995× |
| kimi-k3 TP | 4 | 16 | 0.438 | 7.000–7.000 | 16.000–16.000× |
| kimi-k3 TP | 64 | 16 | 7.000 | 98.875–98.875 | 14.125–14.125× |
| kimi-k3 TP | 16384 | 128 | 1792.000 | 2569.875–2569.875 | 1.434–1.434× |
| nemo3-ultra TP | 4 | 16 | 0.344 | 5.500–5.500 | 16.000–16.000× |
| nemo3-ultra TP | 64 | 16 | 5.500 | 35.500–35.500 | 6.455–6.455× |
| nemo3-ultra TP | 16384 | 256 | 1408.000 | 1918.000–1918.000 | 1.362–1.362× |

`allocation-cells.csv` contains every dtype and source receipt hash, plus the existing prepared FC1 activation payload/SF size. New FC2/output is2–4× input payload bytes depending activation type; SF padding reduces that ratio for narrow route tiles. This is incremental allocation, not an inferred DRAM transaction count. TMA additionally stores route padding for each live32/64-row slab, which must be measured separately.

First-call host tensor allocation and TMA descriptor creation are outside warmed CUDAgraph CUPTI timing. The experiment records their graph-memory footprint, and any claimed speedup must explicitly retain this boundary.
