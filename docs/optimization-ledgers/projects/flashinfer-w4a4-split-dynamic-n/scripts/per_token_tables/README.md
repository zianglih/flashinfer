# Dedicated per-token native tables

`run_model_tables.py`, `observe_table.py`, and `arm_contracts.py` are frozen; their hashes are in `evidence/per-token-public-audit-r1/helpers-frozen.json`. They run one fresh native AUTO sweep for each requested model/family. TRTLLM is the performance baseline. No CuTe before/after campaign or original-control adapter is part of this workflow.

The observer saves native medians after timed work returns, exact existing route identities, per-arm quantization contracts, and environment restoration checks. The runner preserves actual runtime/JIT versions and 85 source hashes. Ambient base quantization fast math remains enabled; dedicated per-token arms scope the disable setting around activation quantization and execution. Shared weights use the standard recipe outside that scope. Per-token status is arm-specific, never a global false claim.

NV default columns: CuteDSL W4A4, CuteDSL PER-TOKEN, CuteDSL W4A16, TRTLLM NVFP4, TRTLLM PER-TOKEN, TRTLLM BF16. MX default columns: CuteDSL MXFP4x8, CuteDSL MXFP8, TRTLLM MXFP4x8, TRTLLM MXFP8, TRTLLM BF16.

`audit_benchmark.py` validates the frozen source's explicit recipes and normal/exception environment restoration without CUDA. `launch_gate.py` uses GPU5 for bounded CUDA/CuTe quantization equality and public function/wrapper forwarding, followed by native dedicated-selector V3 T4 and V41 T32 smoke. `fetch_gate.py` copies existing output only. These are focused capability checks, not cross-backend numerical MoE equivalence or a broad sanitizer suite.
