| Model | Scope | Count | Mean ns | Median ns | P95 ns | Max ns |
|---|---|---:|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | epi_cstore_acquire | 366 | 52.28 | 32 | 128 | 160 |
| ep-kimi-k3-w4a16 | transform_wait_tmem_slot_free | 14784 | 29.81 | 32 | 64 | 192 |
| ep-kimi-k3-w4a16 | transform_wait_raw_tma_ready | 14784 | 31.48 | 32 | 32 | 2784 |
| ep-kimi-k3-w4a16 | transform_load_decode_nvfp4 | 14784 | 325.96 | 320 | 416 | 544 |
| ep-kimi-k3-w4a16 | epi_body | 528 | 3878.00 | 4160 | 5792 | 6368 |
| tp-v41-flash-w4a16 | epi_cstore_acquire | 236 | 42.71 | 32 | 96 | 160 |
| tp-v41-flash-w4a16 | transform_wait_tmem_slot_free | 15360 | 29.77 | 32 | 64 | 96 |
| tp-v41-flash-w4a16 | transform_wait_raw_tma_ready | 15360 | 30.69 | 32 | 32 | 2880 |
| tp-v41-flash-w4a16 | transform_load_decode_nvfp4 | 15360 | 311.86 | 320 | 384 | 544 |
| tp-v41-flash-w4a16 | epi_body | 384 | 1895.67 | 1728 | 2560 | 2656 |

| Model | Cluster / CTA | Tiles | Body ns/tile | Acquire sum ns/tile | Instrumented fraction |
|---|---|---:|---:|---:|---:|
| ep-kimi-k3-w4a16 | 0 / 0 | 33 | 3895.27 | 152.24 | 3.91% |
| ep-kimi-k3-w4a16 | 0 / 1 | 33 | 3786.67 | 144.48 | 3.82% |
| ep-kimi-k3-w4a16 | 1 / 2 | 33 | 4022.30 | 156.12 | 3.88% |
| ep-kimi-k3-w4a16 | 1 / 3 | 33 | 3818.67 | 127.03 | 3.33% |
| tp-v41-flash-w4a16 | 0 / 0 | 24 | 1910.67 | 118.67 | 6.21% |
| tp-v41-flash-w4a16 | 0 / 1 | 24 | 1780.00 | 85.33 | 4.79% |
| tp-v41-flash-w4a16 | 1 / 2 | 24 | 2048.00 | 110.67 | 5.40% |
| tp-v41-flash-w4a16 | 1 / 3 | 24 | 1864.00 | 105.33 | 5.65% |
