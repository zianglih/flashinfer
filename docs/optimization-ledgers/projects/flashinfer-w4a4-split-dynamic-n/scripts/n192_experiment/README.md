# N192 two-CTA geometry screen

Frozen7829fc00; isolated source only. The W4A16 ledger retained a192-token
capacity, so this tests the corresponding intermediate capacity in the new
blockscaled core. SFB row blocks use ceil(N/128), and all output/TMEM footprints
follow the actual192 geometry. No new production tactic was added.

Eighteen raw FP32 accumulator cases pass exactly against Torch for M384,
N1/17/129/191/193/385,K64/256/384, nonuniform scales, reversed scatter and one
persistent CTA pair. Native final BF16 output is byte-identical across
N256→192→128→256 for T16384. The first native attempt stopped at an unpatched
host helper alias before any N192 run; the corrected r2 explicitly patches both
host aliases in the experiment process only.

C1B200GPU3,nvcr.io/nvidia/pytorch:26.05-py3; actual native routing, H7168/I2048,
32local experts,topk8; 10/100 cold-L2 CUDAgraph/CUPTI diagnostics. Both phases use
M256/twoCTA, default current stage policy. Primary AUTO data is not replaced.

| Route N | Live route tiles | FC1 us | FC2 us | Full pipeline us |
|---|---:|---:|---:|---:|
|256 control first|77|323.697|180.785|618.0335|
|192|101|336.496|195.0565|648.0020|
|128|142|334.464|165.952|616.8970|
|256 control last|77|331.024|181.952|617.8735|

N192 is slower; reject the additional tactic. No old primary baseline rerun.
Complete raw samples: project `logs/n192-*`, mirrored from the devbox.
