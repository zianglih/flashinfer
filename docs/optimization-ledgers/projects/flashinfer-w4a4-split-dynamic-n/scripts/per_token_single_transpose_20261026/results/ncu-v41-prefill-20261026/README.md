# V41 T8192 per-token prefill diagnosis

Pinned0def601d, c3 B300 GPU2, nvcr.io/nvidia/pytorch:26.05-py3. Public saved native tactic N256, two-CTA FC1/FC2, k_steps4/4, static scheduler. Input quantization included; fused finalize disabled. Each capture selects one graph kernel with six-pass NCU kernel replay, cold cache/base clocks. This serializes the pipeline and is counter evidence only, never a replacement for native cold-CUPTI medians.

FC1 reads1.330GB, tensor-active46.20%, DRAM peak67.29%, barrier stalls35.05%, long scoreboard34.60%. It has148 persistent blocks,288threads,124registers and196480bytes shared storage including driver reservation. These prefill signals differ substantially from the T128 bandwidth-bound decode profile.

The intermediate quantizer launches73,472 CTAs (128threads,63registers,62.05grid waves), reads338.611MB, writes77.871MB and executes83.459M instructions. Its full BF16 input allocation is73,472×2304×2=338.559MB, almost exactly the measured read count. Issue-active64.61%, DRAM peak26.44%, long scoreboard24.95%, short scoreboard14.57%, not-selected18.28%. This identifies avoidable full-capacity quantization as a concrete next experiment: routing already exposes the live padded prefix length on device. The separate route-count experiment preserves SF final-atom padding and PDL ordering.

See receipt.json for source/cache hashes, environment and exact commands; summary.json contains the bounded requested counters; raw ncu-rep/CSV, compiler artifacts and logs are retained.
