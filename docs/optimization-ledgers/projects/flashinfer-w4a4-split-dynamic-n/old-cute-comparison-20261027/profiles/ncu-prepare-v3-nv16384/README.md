# Preparation counter profile

Current 0b7 native V3 EP8 NVFP4 T16384 winner; one B300, GPU0, exact deployment and command in receipt.json. NCU kernel replay serializes the selected kernel and clears caches; these counters are diagnostic, not native end-to-end timing.

128 threads ×2368 blocks. Duration28.896us. DRAM read34.782MB, write16.970MB;23.38% peak throughput. L2 traffic289.010MB,35.88% sector hit rate. Global load2,204,720 and store4,031,104 L1 sectors. Issue26.21%, activewarps88.72%, long-scoreboard stalls86.97%. This does not support HBM bandwidth saturation. Scattered scale-factor stores and load latency are plausible opportunities; the counters do not isolate which load causes stalls.

Raw report, exported CSV and verified source/cache receipt are preserved beside this note. Native NSYS preparation duration is25.841us under the full graph, which is distinct from selected-kernel replay.
