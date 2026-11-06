# Integrated public-chain startup prefetch

Unstaged source: `flashinfer-pdl-weight-prefetch-integrated-review`, based on retained853aaf69d706b291afee477f738956b997033f53. Frozen patch `a92c766dfdfc1ca8051b0e5c93afe90b77225391c1203271137debcbb3d3d685`; `source.json` pins all83 relevant source files. No production changes or retention decision.

This integrates the independently gated multi-stage core (`min(num_stages, k_tiles)` weight/SFA priming) with explicit public FC1 publication and FC2 prefetch knobs. Both default false. Known non-per-token Blackwell unfused chains pair the controls only for one-CTA static FC2. The MX benchmark's reused native split runner opts in using the same geometry contract. Generic standalone, Rubin, per-token, fused finalize and unsupported FC2 geometries retain their old defaults. Explicit unsupported requests raise. The high-level per-token path stays false because the intervening quantizer has no metadata release at its own trigger; the SF conversion is a view only.

Publication mode now confines both release and the first startup trigger to warp0 after the common all-thread dependency wait. Other startup configurations retain their previous trigger path. All FC2 threads, including no-work CTAs, still execute the dependency wait; B/SFB remain after it. Priming acquires each stage's full expected transaction count once and issues only immutable weights/SFA; the normal first-tile producer skips those primed acquisitions before completing B/SFB.

Validation:

- Ruff check/format, py_compile and gitdiffcheck passed on all5 changed files.
- `public-contract.json` and `admission-truth-table.json`:192 structural selections, safe public false defaults, complete-module AST equivalence for benchmark and high-level chain after deleting exactly the one new readiness assignment and two call kwargs. Inputs/routing/timing/table code is unchanged. Do not replace original receipt hashes with normalized hashes.
- `gate.json`, `chain-result.json`:324 exact captured replays over three dtypes, changing routes/input/weights, zero local work, N16/N128, one-CTA and two-CTA FC1, and two-CTA FC2 fallback. On merely observes/forwards actual public-selected kwargs; Off and PDLoff are task-local controls. All83 source hashes unchanged.
- `codegen-gate.json`:27 additional exact public N16NV replays with named FC1/FC2 On/Off/PDLoff PTX/SASS. FC1On PTX139 commonwait→warp!=0 branch141/142→release143→trigger145. Other warps skip both publication instructions.

Native AUTO evidence is separate: `evidence/pdl-integrated-native-campaign/launch.json` records both-model A1(default public tables)→A2(CuTe only)→C2(clean853) commands and GPU assignments. Fresh clean C1s were captured immediately before this campaign. V3 uses GPUs5/4, V41 GPUs7/6. Timing is unchanged10warm/100 cold-L2 CUDAgraph CUPTI, all13tokens,1/2 excluded from retention. No fixed-screen inference substitutes for those paired results.

The native paired summary must explicitly use `public-contract.json` to bridge the benchmark hash change: clean2c24363d52238fcb0dbe2b300fce0e3d5cf9162e725606544dc74a8117f1ea70→integratedd27791c660e644c8e70c83c6fb6fb66f37028d5a5df7bc59f75d38a51facabe5. The difference is the intended MX public-call readiness contract, not a measurement-method change.
