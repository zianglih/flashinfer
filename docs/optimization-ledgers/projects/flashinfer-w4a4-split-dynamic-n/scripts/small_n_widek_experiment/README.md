# Wider K for small routed-token tiles

Frozen control:7829fc00. Task-local immutable modules only. C1 B200 GPUs3/7,
image nvcr.io/nvidia/pytorch:26.05-py3. Native benchmark inputs H7168/I2048,
32 local experts, top-k8, no per-token NVFP4, no fused finalize. Phase timing
uses10 warmups/100 cold-L2 CUDA graph CUPTI samples. These diagnostic measurements
are not primary AUTO retention evidence; raw medians/samples are in results/.

Select eight native MMA K steps and four operand stages for one-CTA N16/32/64,
for both FC1 and FC2. The128-byte Gather4 descriptor is unchanged; two chunks
populate the wider K stage. SF TMEM storage expands accordingly. Existing
one/two-CTA geometry, runtime N and numerical arithmetic remain unchanged.

Repeated NVFP4 N16 FC1 T4/128/512 improves34.849/97.569/108.481us to
33.073/93.776/98.704us; FC2 17.184/53.952/60.288us to16.832/53.248/56.944us.
N32/N64 gains are smaller but positive in both phase screens. MXFP8 reverse
N16 FC1 improves56.496/164.225/184.512us to53.312/151.057/164.224us;
FC2 28.096/90.112/101.152us to26.528/85.568/92.000us. Mixed W4A8 N16
FC1 improves43.761/120.272/143.360us to43.344/106.304/124.800us;
FC2 20.016/62.832/75.520us to17.600/54.081/63.360us. MXFP8/mixed N64
also improve. No stage5 selection: NVFP4 exceeds SMEM capacity, and SF32
measurements do not justify another policy branch. Stage3 is not consistently
better than stage4.

Focused exact coverage:48 FC1 pairs across all six operand/SF formats, K64/128
and384, N16/64, per-token BF16 or generated FP4/FP8 outputs/SF;24 FC2 format,
channel-tail and per-token pairs. Reset full outputs/SF to their original
sentinels before each arm, then compare complete bytes. Native phase outputs/SF
also compare exactly before timing every variant.

The first test attempt inherited an undersized generated-SF allocation from a
probe restricted to route capacities divisible by128. N16 produced144 routed
rows, but the prepared SF layout requires256 padded rows. The test allocation
was corrected to round rows to128; production allocation was already correct.
The failed logs and corrected r2 are preserved. One mixed native launch also
used the wrong CLI label (mxfp4 instead of w4a8); argparse rejected it before
GPU execution, and the corrected w4a8 records are separate.

build.py records initial snapshot construction; current probes and manifest
are the authoritative final harness. Do not rerun it over the final probes.
