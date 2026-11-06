# R14 FC1 local storage

Joined native winner first-use order to FC1 compilation-cache order; validated unique compile count, N, CTA group, K tile, dtypes, and identical resources in both candidate phases. FC1 cache excludes runtime token count, so multiple token rows may reuse one executable. CLC is the selected tactic flag; small-grid normalization may disable it.

CUDA LOCAL_SIZE_BYTES is per-thread local storage; these records do not claim dynamic spill instruction counts.

| Job | Tokens | Backend | MMA M×N | Cluster | K steps | CLC | Initial regs | Local bytes |
|---|---|---|---|---|---:|---|---:|---:|
| ep-kimi-k3-nvfp4 | 4096, 16384 | CuteDSL PER-TOKEN | 128×128 | 1×1 | 8 | False | 168 | 16 |
| ep-nemo3-ultra-mxfp | 256 | CuteDSL MXFP4x8 | 128×32 | 1×1 | 8 | False | 168 | 8 |
| ep-nemo3-ultra-mxfp | 4096, 16384 | CuteDSL MXFP8 | 256×256 | 2×1 | 4 | False | 168 | 16 |
| ep-nemo3-ultra-mxfp | 4096, 16384 | CuteDSL MXFP4x8 | 256×256 | 2×1 | 4 | False | 168 | 16 |
| ep-nemo3-ultra-nvfp4 | 4096 | CuteDSL W4A4 | 128×256 | 1×1 | 4 | False | 168 | 16 |
| ep-nemo3-ultra-nvfp4 | 4096 | CuteDSL PER-TOKEN | 256×128 | 2×1 | 4 | False | 168 | 16 |
| ep-nemo3-ultra-nvfp4 | 16384 | CuteDSL W4A4 | 256×128 | 2×1 | 4 | False | 168 | 16 |
| ep-nemo3-ultra-nvfp4 | 16384 | CuteDSL PER-TOKEN | 512×128 | 2×1 | 4 | False | 168 | 16 |
| ep-v3-nvfp4 | 4096 | CuteDSL PER-TOKEN | 256×256 | 2×1 | 4 | False | 168 | 16 |
| ep-v3-nvfp4 | 16384 | CuteDSL PER-TOKEN | 256×128 | 2×1 | 4 | False | 168 | 8 |
| ep-v41-flash-nvfp4 | 16384 | CuteDSL W4A4 | 256×256 | 2×1 | 4 | False | 168 | 16 |
| ep-v41-flash-nvfp4 | 16384 | CuteDSL PER-TOKEN | 512×128 | 2×1 | 4 | False | 168 | 16 |
| tp-kimi-k3-nvfp4 | 8 | CuteDSL PER-TOKEN | 128×16 | 1×1 | 8 | False | 168 | 8 |
| tp-nemo3-ultra-mxfp | 8 | CuteDSL MXFP8 | 256×32 | 2×1 | 8 | False | 168 | 8 |
| tp-nemo3-ultra-mxfp | 8 | CuteDSL MXFP4x8 | 128×16 | 1×1 | 8 | False | 168 | 8 |
| tp-nemo3-ultra-mxfp | 4096 | CuteDSL MXFP8 | 256×256 | 2×1 | 4 | True | 168 | 8 |
| tp-nemo3-ultra-mxfp | 4096 | CuteDSL MXFP4x8 | 256×256 | 2×1 | 4 | True | 168 | 8 |
| tp-nemo3-ultra-nvfp4 | 8 | CuteDSL W4A4 | 128×32 | 1×1 | 4 | False | 168 | 16 |
| tp-nemo3-ultra-nvfp4 | 8 | CuteDSL PER-TOKEN | 256×16 | 2×1 | 8 | False | 168 | 16 |
| tp-nemo3-ultra-nvfp4 | 256 | CuteDSL W4A4 | 128×16 | 1×1 | 8 | False | 168 | 8 |
| tp-nemo3-ultra-nvfp4 | 256 | CuteDSL PER-TOKEN | 128×16 | 1×1 | 8 | False | 168 | 8 |
| tp-nemo3-ultra-nvfp4 | 4096, 16384 | CuteDSL PER-TOKEN | 128×256 | 1×1 | 4 | True | 168 | 8 |
| tp-nemo3-ultra-nvfp4 | 16384 | CuteDSL W4A4 | 128×256 | 1×1 | 4 | True | 168 | 8 |
| tp-v3-nvfp4 | 8 | CuteDSL PER-TOKEN | 256×16 | 2×1 | 8 | False | 168 | 8 |
| tp-v41-flash-nvfp4 | 8, 256 | CuteDSL PER-TOKEN | 128×16 | 1×1 | 8 | False | 168 | 8 |
| tp-v41-flash-nvfp4 | 4096 | CuteDSL PER-TOKEN | 256×64 | 2×1 | 8 | False | 168 | 16 |
