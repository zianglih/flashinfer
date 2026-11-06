# Fresh B300 CuTe phase diagnostic

Clean 0c1e00fc, V41 EP4/TP1, shared precomputed sqrtsoftplus routes (model gate computation excluded; internal expert sorting remains included). Saved fresh B300 AUTO tactics; no B200 cache reuse. Each case has separate10/100 cold-L2 graph/CUPTI native timing and five node-traced replays. All cases N16/M128 one-CTA for both FCs. GPU3.

Kernel lifetimes include PDL waits and startup; they are not additive. Pair resource sums are necessary bounds, not complete occupancy predictions. Kernel-level overlap can occur across different SMs.

| Format | T | Native us | FC1 us | FC2 us | Prep→FC1 overlap | FC1→FC2 overlap | FC2→combine overlap |
|---|---:|---:|---:|---:|---:|---:|---:|
| mxfp4 | 32 | 137.729 | 87.297 | 48.704 | 1.856 | 8.768 | 1.504 |
| mxfp4 | 128 | 284.690 | 186.882 | 95.393 | 1.632 | 8.609 | 1.472 |
| mxfp4 | 512 | 328.721 | 215.457 | 107.904 | 1.408 | 7.808 | 1.472 |
| nvfp4 | 32 | 130.689 | 79.137 | 47.616 | 1.408 | 6.944 | 1.248 |
| nvfp4 | 128 | 273.570 | 175.041 | 95.968 | 1.120 | 7.552 | 1.280 |
| nvfp4 | 512 | 316.546 | 202.402 | 106.496 | 1.184 | 5.888 | 1.408 |

- NV FP4 each FC requests197,504B SMEM; mixed each requests215,936B. The SM has233,472B. Either same-format FC1+FC2 pair exceeds one SM, so early successor blocks can only use already-free SMs while the previous kernel still has live blocks elsewhere.
- NV FC1=320threads/72registers, mixed FC1=192threads/70registers; both FC2=288threads/90registers. No per-thread local memory reported. Nsight localMemoryTotal is preserved raw and is not interpreted as per-kernel spill storage.
- AtT32/128/512, mixed FC1 lifetime exceeds NV by8.160/11.841/13.055us; FC2 differs+1.088/-0.575/+1.408us. Preparation adds0.448/0.512/0.736us; combine differs0.192/0.128/0.032us.
- This localizes the mixed cost toFC1 but does not distinguish inline producer epilogue from doubled outer K iterations (K256 versusK512); targeted iKET or the controlled dedicated-epilogue candidate can resolve that.
- TRT counterpart phase capture is pending first-use cubin tuning on reservedGPUs0/1. These results alone do not identify the TRT gap or constitute paired retention evidence.
