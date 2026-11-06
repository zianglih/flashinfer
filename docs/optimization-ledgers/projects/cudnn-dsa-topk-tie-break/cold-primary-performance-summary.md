All cases use Q=8192, FP32 scores, `return_val=False`; milliseconds are medians of 50 graph replays, with a 256 MiB L2 flush before each timed call. Speedup is `time(0)/time(2)`; below 1 means the large-index policy is slower. CP is the **implied local shape**, not a distributed run.

| Input | KV | Implied CP | Rank | K | None (ms) | Large (ms) | Speedup |
|---|---:|---:|---:|---:|---:|---:|---:|
| random | 8K | 1 | 0 | 1024 | 0.1782 | 0.1782 | 1.0002x |
| random | 8K | 1 | 0 | 2048 | 0.1679 | 0.1678 | 1.0007x |
| random | 32K | 4 | 0 | 1024 | 0.4670 | 0.4690 | 0.9957x |
| random | 32K | 4 | 0 | 2048 | 0.4547 | 0.4567 | 0.9955x |
| random | 128K | 16 | 0 | 1024 | 1.8801 | 1.8883 | 0.9957x |
| random | 128K | 16 | 0 | 2048 | 1.8739 | 1.8822 | 0.9956x |
| random | 512K | 64 | 0 | 1024 | 7.8397 | 8.0461 | 0.9743x |
| random | 512K | 64 | 0 | 2048 | 7.8627 | 8.2730 | 0.9504x |
| random | 32K | 4 | 1 | 1024 | 0.4731 | 0.4733 | 0.9996x |
| random | 32K | 4 | 1 | 2048 | 0.4772 | 0.4772 | 0.9999x |
| random | 128K | 16 | 7 | 1024 | 1.7635 | 1.7695 | 0.9966x |
| random | 128K | 16 | 7 | 2048 | 1.7695 | 1.7757 | 0.9965x |
| random | 512K | 64 | 31 | 1024 | 7.7814 | 7.9513 | 0.9786x |
| random | 512K | 64 | 31 | 2048 | 7.8388 | 8.1337 | 0.9637x |
| duplicates | 8K | 1 | 0 | 1024 | 0.2048 | 0.2273 | 0.9009x |
| duplicates | 8K | 1 | 0 | 2048 | 0.1925 | 0.2171 | 0.8868x |
| duplicates | 32K | 4 | 0 | 1024 | 0.5550 | 0.6082 | 0.9125x |
| duplicates | 32K | 4 | 0 | 2048 | 0.5428 | 0.6308 | 0.8605x |
| duplicates | 128K | 16 | 0 | 1024 | 2.5917 | 2.6440 | 0.9802x |
| duplicates | 128K | 16 | 0 | 2048 | 2.5815 | 2.6655 | 0.9685x |
| duplicates | 512K | 64 | 0 | 1024 | 11.8267 | 11.8753 | 0.9959x |
| duplicates | 512K | 64 | 0 | 2048 | 11.8139 | 11.9035 | 0.9925x |
| duplicates | 32K | 4 | 1 | 1024 | 0.5571 | 0.6163 | 0.9038x |
| duplicates | 32K | 4 | 1 | 2048 | 0.5612 | 0.6595 | 0.8510x |
| duplicates | 128K | 16 | 7 | 1024 | 2.3571 | 2.4371 | 0.9672x |
| duplicates | 128K | 16 | 7 | 2048 | 2.3619 | 2.5119 | 0.9403x |
| duplicates | 512K | 64 | 31 | 1024 | 11.6111 | 11.7012 | 0.9923x |
| duplicates | 512K | 64 | 31 | 2048 | 11.6234 | 11.7914 | 0.9858x |
| sparse-left | 512K | 64 | 0 | 1024 | 3.0710 | 5.6995 | 0.5388x |
| sparse-left | 512K | 64 | 0 | 2048 | 3.0617 | 5.6791 | 0.5391x |

The large-index policy adds at most 5.2% on the random inputs and 17.5% on the eight-value duplicate inputs in this sweep. Sparse-left stress is 1.86x slower (up to 85.6% extra): two cutoff ties at the start force a reverse scan through almost the entire long prefix. These are synthetic selector costs, not end-to-end DSA slowdowns. Q=8K remained practical, so it was not reduced.
