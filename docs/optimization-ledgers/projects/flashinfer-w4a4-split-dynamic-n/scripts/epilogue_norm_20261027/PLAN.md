# Invariant epilogue normalization hoist

Both sources are b85eff41 plus the identical six-field all-CLC enumeration. The candidate moves only norm_const[0] outside the scheduled-tile loop for the existing inline and dedicated epilogue roles. Expert-alpha placement and arithmetic stay unchanged. The branch is the existing optional norm/epilogue contract; no model/dtype/geometry condition is added.

The global PDL dependency wait precedes the load. Norm remains an API-provided invariant scalar for the kernel launch. Empty local work may read the valid scalar once, but does not publish or process any tile. When norm_const is None, constexpr specialization should leave generated device instructions unchanged. The invariant value now stays live across tiles; check registers, spills and instruction movement before deciding to time.

Use the existing64-replay exact source-paired gate with16 paired core compilations. Inspect SASS tile backedges to prove dynamic repeated-load removal. Only after useful codegen and resource validation, run the same public10/100 cold-L2 CUPTI fixed-all-CLC CAAC across three models/four affected formats, with initial activation quantization included for NVFP4. No new upstream tests or broad correctness matrix.
