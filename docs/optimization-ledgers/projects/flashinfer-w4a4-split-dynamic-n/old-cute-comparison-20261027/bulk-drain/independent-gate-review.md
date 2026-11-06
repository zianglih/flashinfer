Paired bulk-drain gate: 48/48 replays have identical output digests; saved input identities and runtime match.
All 16 paired compiled resource plans match. All eight FC1 PTX and executable sections are byte-identical.

| Configuration | PDL | FC2 registers C/A | wait0 delta | transpose-join delta |
|---|---:|---:|---:|---:|
| nv-n256 | 0 | 126/118 | +1 | +1 |
| nv-n256 | 1 | 126/124 | +1 | +1 |
| mx8-n256 | 0 | 124/118 | +1 | +1 |
| mx8-n256 | 1 | 124/122 | +1 | +1 |
| nv-m512 | 0 | 124/124 | +1 | +1 |
| nv-m512 | 1 | 126/124 | +1 | +1 |
| mx8-m512 | 0 | 126/122 | +1 | +1 |
| mx8-m512 | 1 | 126/122 | +1 | +1 |

All compiled kernels report zero stack/local allocation. Only the kernel core and the exact recorded unused benchmark guard-removal pair differ in source.

Coverage is limited to static scheduling with separate epilogue owners. CLC, inline epilogues, sanitizer, and performance are outside this gate.
