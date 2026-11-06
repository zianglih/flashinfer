# V41 T128 FC1 bounded NCU diagnosis

Pinned0def601d, c3 B300 GPU2, nvcr.io/nvidia/pytorch:26.05-py3. Saved native public AUTO tactics with initial quantization, no fused finalize. Six-pass NCU kernel replay, cold cache/base clocks, one FC1 kernel. Serialization removes native PDL overlaps: durations are diagnostic and are not retention timing evidence. Source/cache identities and exact commands are in receipt.json; raw reports/CSV are retained.

Per-token N16 and ordinary NVFP4 N32 both read about1.09GB and reach84.82%/85.29% of DRAM peak. Tensor-active is7.02%/7.08%; long-scoreboard stalls78.68%/79.69%. The observed82 nonempty local experts require1,088,225,280 bytes for one copy of FC1 packed weights and their SF. Per-token measured1,091,847,936 bytes, only0.33% higher. This supports a bandwidth-bound decode FC1 whose read volume is near the required weight payload. It does not establish that broader pipeline scheduling has no opportunity.
