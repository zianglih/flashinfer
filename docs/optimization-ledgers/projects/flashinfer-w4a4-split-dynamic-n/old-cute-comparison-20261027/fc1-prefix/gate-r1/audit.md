# V1 exact/resource gate: stopped

48 control and 27 candidate exact replays passed. The next candidate FC1 specialization spilled before launch; no timing ran. Nine completed FC2 pairs have identical executable section bytes.

| Configuration | PDL | FC1 registers C → A | Stack C → A | First TMEM → release sites C → A | Last TMEM → release gap C → A |
|---|---|---|---|---|---|
| nv-gated | 0 | 90 → 122 | 0 → 0 | 459 → 372 | 1 → 1 |
| nv-gated | 1 | 92 → 124 | 0 → 0 | 459 → 372 | 1 → 1 |
| nv-situ | 0 | 84 → 116 | 0 → 0 | 910 → 822 | 1 → 1 |
| nv-situ | 1 | 94 → 119 | 0 → 0 | 911 → 823 | 1 → 1 |
| nv-per-token | 0 | 121 → 153 | 0 → 0 | 355 → 336 | 1 → 1 |
| nv-per-token | 1 | 123 → 155 | 0 → 0 | 355 → 336 | 1 → 1 |
| nv-relu | 0 | 118 → 168 | 0 → 0 | 532 → 385 | 3 → 2 |
| nv-relu | 1 | 120 → 166 | 0 → 0 | 532 → 403 | 2 → 3 |
| nv-relu-per-token-m512 | 0 | 120 → 168 | 0 → 0 | 287 → 301 | 1 → 1 |
| nv-relu-per-token-m512 | 1 | 122 → 168 | 0 → 8 | 287 → 306 | 1 → 2 |

The failed ReLU² per-token M512/N128 PDL-on artifact has one `STL.64` and two `LDL` sites. Inactive and one-slab candidate controls were not reached. Release distances count static SASS sites, not dynamic instruction execution or time. Full source/artifact hashes and paired live FC1 payload/SF checks are in audit.json.
