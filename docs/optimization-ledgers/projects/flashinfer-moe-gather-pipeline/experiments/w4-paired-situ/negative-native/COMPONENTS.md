# Tight-negative EP stage trace

All100 samples per phase are retained. Values below are medians in microseconds; component medians do not necessarily add to E2E.

| Tokens | Phase | E2E | Routing | FC1 start | Route/FC1 overlap | FC1 span | FC1 extension | FC2 extension | Combine extension |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 0-control | 120.2890 | 12.8000 | 12.6560 | 0.1600 | 71.9370 | 71.7930 | 32.1285 | 3.4875 |
| 32 | 0-control | 183.3295 | 7.3285 | 7.1690 | 0.1600 | 115.6170 | 115.4570 | 57.1845 | 3.3280 |
| 16 | 1-candidate | 121.0890 | 13.6960 | 13.5360 | 0.1290 | 72.0485 | 71.9050 | 32.1440 | 3.4245 |
| 32 | 1-candidate | 184.0500 | 8.4800 | 8.3360 | 0.1600 | 115.8730 | 115.7130 | 56.5445 | 3.2960 |
| 16 | 2-candidate | 121.1685 | 13.7440 | 13.6000 | 0.1290 | 72.1605 | 72.0010 | 31.9845 | 3.4240 |
| 32 | 2-candidate | 183.9700 | 8.5280 | 8.3680 | 0.1600 | 115.7125 | 115.5525 | 56.5285 | 3.2640 |
| 16 | 3-control | 120.2250 | 12.9125 | 12.7525 | 0.1290 | 72.0325 | 71.8730 | 32.0965 | 3.4240 |
| 32 | 3-control | 183.0255 | 7.3600 | 7.2000 | 0.1600 | 115.5850 | 115.4250 | 56.7680 | 3.2960 |

T16: candidate E2E +0.87175us; routing +0.86375us; FC1 span +0.11975us; FC2 extension -0.04825us. T32: E2E +0.83250us; routing +1.15975us; FC1 span +0.19175us; FC2 extension -0.43975us. All four phases report2032MHz and no throttle reason for these two points.

The changed SiTU instructions execute in FC1 epilogue. Most extra latency is already present before FC1 starts. This does not establish that packing arithmetic caused slower routing or a compiler scheduling regression; native instruction comparison and one opposite-order check can distinguish codegen facts from process/order-dependent execution. The original negative E2E rows remain valid observations.
