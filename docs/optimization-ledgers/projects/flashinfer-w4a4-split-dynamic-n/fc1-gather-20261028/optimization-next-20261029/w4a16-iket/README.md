# W4A16 optional iKET ranges

Unstaged source: `flashinfer-w4a16-iket-review`, retained base374ed4c0. Only `blackwell/moe_w4a16_kernel.py` changes. The constructor has opt-in `enable_iket=False`; no public wrapper flag, tactic, pipeline or register-budget change. Optional iKET import follows the swap-AB pattern. The existing transform hooks are reused, preserving the MegaW4 override contract and leaving Mega files untouched.

Ranges cover PDL dependency/signal, scheduler item/CLC ready, weight TMA empty/issue, regular activation TMA empty/issue, Gather4 empty/issue, transform raw wait/TMEM-slot wait/load+decode/store+commit, MMA accumulator availability/A-ready/B-ready/issue/release, and epilogue accumulator wait/body. A-ready is observed before B-ready in the existing program order; zero B-wait alone does not establish the activation delivery latency.

Default-off AST is identical after removing the added configuration and disabled markers. Paired33-case exact gates on GPUs5/7 both pass. All33 corresponding PTX and CUBIN files are byte-identical, including FC1 and FC2. No sanitizer or extra retention timing is needed to qualify the disabled markers within this compiled coverage.

Diagnostic sampling is artifact-only and has its own AST proof. It selects the first two complete CTA clusters using the flattened cluster coordinates; a blockIdx.x-only predicate would incorrectly sample every z cluster in W4's ordinary persistent grid. Sampling does not change non-marker AST nodes.

Current diagnostic: K3 EP8 4096/8192, same existing native winners/routes as the paired W4 screens, public profiler path, one graph iteration, iKET NativeDump, no autotuning and no timing backend. All source/cache/winner/routing identities are guarded. Instrumented ranges are not retention performance evidence; instrumentation can alter instruction scheduling and resource usage.

Environment: B300 GPUs5/7, `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2, CuTeDSL4.8.0; persistent C++ cache and stable native data/header links. Source manifests distinguish actual remote Git parent1b0 plus materialized patch from the source-equivalent retained374ed4c0.
