# R4: flat internal FC1 scheduler choice

- Extend only the internal Blackwell tactic/cache tuple with an optional fifth boolean after the independent K pair. Strict boolean validation; legacy outer3/4 request CLC, preserving the retained one-CTA behavior without carrying forward the old cluster whitelist. Rubin legacy parsing remains unchanged and rejects Blackwell extra fields.
- Pass the choice through existing private runner/core/FC1 implementation arguments. Public functions/signatures are unchanged. The private direct default resolves `None` once to Blackwell=True/Rubin=False; explicit unsupported Rubin=True rejects clearly.
- Keep the existing resolved CLC admission and cache key. No separate pruning policy: equivalent static-resolved requests reuse compiled code but may be profiled twice. FC2 scheduling and every device method remain unchanged from R3.
- Existing complete-chain AUTO profiling preserves preparation, PDL, FC1, per-token quantization, FC2, combine, recipe and auxiliary stream kwargs. There is no nested runner, extra ranking pass, phase-only timing or model/shape scheduler rule.

## Cost and limits

The raw set grows180→360 and the currently resource-admitted set160→320 per representative format. Distinct phase geometry/K requests grow from28FC1+28FC2 to at most56FC1+28FC2 per configuration, before existing effective-admission/cache sharing. Thus the upper-bound GEMM specialization count grows50%, while candidate profiling calls double. These are static search-space counts, not measured compiler counts or a wall-time guarantee. Existing profile buckets and actual synthetic routing can still bias selection; the fresh native benchmark will decide retention.

## CPU validation

The existing tactic methods pass over360 JSON-roundtripped choices. Actual runner-forwarding stubs cover2172 combinations, preserving recipe/stream identity. The public gather functions are entire-AST unchanged and full MoE AST is identical after removing only the new private argument/keyword forwarding. Actual capability logic with the prior byte-layout SDK stubs admits320 candidates across6 formats. Core/prepare bytes remain exactly R3. GPU validation is separate.
