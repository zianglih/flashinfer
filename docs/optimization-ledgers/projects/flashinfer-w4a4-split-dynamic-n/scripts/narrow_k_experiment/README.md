# Two-native-step K-stage screen

Frozen7829fc00, isolated NVFP4 K128/two native MMA steps per stage compared with
K256/four steps. Gather4 uses64-byte row payloads and matching64-byte swizzle;
scale TMEM reservation is8columns per SF plane. Operand stage counts6/8/10
increase lookahead within the smaller stage footprint. These are task-local
probes only; unsupported/non-NV cases were not expanded after the loss.

Actual native T16384 routing, M256N256/twoCTA, C1B200GPU3,
nvcr.io/nvidia/pytorch:26.05-py3. 10/100 cold-L2 CUDAgraph/CUPTI isolated phases.
All native FC1 output/SF and FC2 output byte comparisons passed.

| Variant | FC1 us | FC2 us |
|---|---:|---:|
| K256/four steps,5stages control |323.905|180.8005|
| K128/two steps,6stages |394.497|212.576|
| K128/two steps,8stages |392.705|207.8725|
| K128/two steps,10stages |392.161|207.056|

All regress; reject without broader checks or primary benchmark runs.
Raw samples: project `logs/narrow-k-*`, mirrored from the devbox.
