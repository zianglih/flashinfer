The V3 T4096 per-token slowdown is concentrated in requantization. All four source snapshots used the same saved two-CTA N256 tactic, exact routes, actual CUDA13.2/CuTe4.7.1, and sequential GPU6 traces. FlashInfer CuTe persistent disk caching was disabled equally for every arm; native C++ artifacts remained shared.



Copy → general PDL changes the complete requantizer PTX by exactly one `fence.acq_rel.gpu;` after the dependency wait. It emits `MEMBAR.ALL.GPU`, `ERRBAR`, `CGAERRBAR`, and `CCTL.IVALL`. All variants retain56 registers/thread,128 threads, min8CTAs/SM, and zero stack/local spill bytes.



| Variant | Trace span us | FC1 lifetime us | FC2 quantize us | FC2 lifetime us | Prepare us | Combine us |
|---|---:|---:|---:|---:|---:|---:|
| v3-t4096-copy | 252.290 | 99.553 | 63.040 | 58.369 | 9.792 | 24.224 |
| v3-t4096-late | 259.010 | 98.497 | 71.520 | 58.464 | 9.728 | 24.160 |
| v3-t4096-pdl | 272.706 | 98.785 | 82.849 | 60.001 | 10.016 | 24.544 |
| v3-t4096-startup | 264.579 | 98.465 | 76.609 | 58.433 | 10.080 | 24.224 |


The median quantizer→FC2 lifetime overlap is0.288us(copy),0.320us(PDL/late), and1.024us(startup). The quantizer already spends the added time before FC2 starts; sustained concurrent weight-prefetch traffic is therefore not the observed explanation. FC1 stays98.5–99.6us. The narrower warp publication variants lower the fence cost but still exceed copy.



These are five profiled native-PDL graph replays, not replacement performance medians. They identify this workload’s bottleneck; CTA0-only publication must still be judged by its exact gate and native screens. No new kernel timing or NCU replay is needed to establish the emitted-fence difference.
