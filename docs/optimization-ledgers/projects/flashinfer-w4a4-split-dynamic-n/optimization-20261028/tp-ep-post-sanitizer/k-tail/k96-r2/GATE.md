# K96 source and numerical gate

Frozen kernel `56194bada350e57c76c937194816a209c256d1786fefcccae6e3725581fc62ec`; source receipt `57d81725f56fe836013858067c1fcb62ec81b993c572bcd1c933a918b5520c92`. The live review was moved onto retained tail commit `2cfb06afd` without changing any of its four source files. Remote source stays an immutable d1767-based snapshot; its kernel includes the identical retained tail change.

- 56 integrated geometry cases pass, with a second identical call exercising compiled-cache hits. H/I=(384,384) and (768,576); N16/32/128/256, M128/256/512, one/two CTA, explicit K4/K8 stage pairs, PDL off/on, shared CLC off/on, ordinary and per-token NVFP4. The one-expert workload usually lowers CLC to static through the existing residency policy.
- The same56 cases with96 experts/top2 pass and retain effective CLC across both CTA groups, both PDL settings, and both FC phases.
- Seven N256 extent cases pass:256,257,272,288,384,400,512 tokens. These cover actual native N below/at/above128 and full256.
- Twelve direct cancellation cases pass: N16/128/256 × one/two CTA ×1/257tokens. Products at K0/16/64 are 2^16,2^-16,−2^16. The native K96 result2^-16 survives Relu2 as exact BF16 2^-32; ordinary K64 would return0.
- The existing maintained shared oracle remains zero tolerance and follows the observed FC1/FC2 native update plans. Its independent producer qualification matched16,258 FP32 comparisons from8,129 native corpus pairs; no duplicated backend arithmetic or loosened tolerance.

131 passing test cases total. Captured172 owned kernels across all runs (including the preserved initial malformed probe) have matching PTX/cubin entry identity, `.shared .align1024`, K96 descriptor bit31, and zero stack/local memory.54 captures use effective CLC. This is not a claim that there are no uniform-register spills. The runtime mixed plans reset per acquired stage, e.g. K256→96+96+64 and K512→96+96+96+96+64+64; the short peeled stage has its own plan.

The initial N256 failure is retained in r1: only native N≤128 tails failed because K96 crosses a four-scale-word boundary and its implicit row-bank stride is set by the actual instruction N. R2 remaps the existing SFB copy destination once per tile: full `16*(2*k+b)`, narrow `16*(k+W*b)`. Both are bijections over the same2W packets; the live first bank becomes contiguous and the unused second bank follows it. MMA start addresses use the same effective stride. No extra TMEM, copies, waits, or barriers.

The first cancellation helper incorrectly allocated the logical6D weight-scale tensor contiguously. All12 such helper failures are preserved under `gate/integrated`; the corrected physical `(E,Mtiles,Ktiles,32,4,4)` buffer plus logical permutation passes all12 in `gate/adversarial-r2`. No kernel/reference change was needed.

Evidence archive: `gate-evidence-complete.tar.gz`, SHA256 `541380ad2e2ffdcc257c5cd63aac507f58f77c5dab0819b4cc683d6e68e58e40`,720 files, all manifest hashes verified. Every compile uses a private CWD/dump directory; no shared generic PTX filename reuse.
