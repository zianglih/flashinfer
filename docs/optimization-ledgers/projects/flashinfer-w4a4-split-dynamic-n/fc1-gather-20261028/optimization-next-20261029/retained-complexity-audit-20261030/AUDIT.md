# Retained swap-AB complexity audit

Read-only review under the user's optimization pause. No new source changes, GPU qualification, timing, or publication. Recommendations apply the new requirement that neutral performance does not justify added kernel complexity; they supersede earlier instruction-sanity retention recommendations where stated below.

The canonical checkout is still `1e4b127a`, with only the parent's uncommitted 3+/12− absmax revert. Its working kernel SHA256 is `da07805984c969fac5f6ad62146c3eb042681d78fd0978eede26e8cdc42763e9`. Revert preparation stopped locally before packaging/upload; GPUs2/3 were independently verified idle. `../absmax-linear-revert-1e4/paused-status.json` records that boundary.

| Retained change | Added complexity and measured effect | Recommendation under the new criterion |
|---|---|---|
| `ce4a7d8c` SF arrival participants, 8+/5− | Adds an owner predicate and a coupled barrier-count rule. Narrow code adds4–13 instructions and1–4 branch/reconvergence sites. Original12: −0.227% overall, +0.130% decode, −0.583% prefill. K3 TP8 MXFP4x8 gains +0.640%, repeated +0.670%; N3U EP8 NVFP4 is −0.401%, repeated −0.051%. | **Remove.** One reproducible sub1% decode benefit does not justify the extra branching/count policy across a broadly neutral screen. Restore the uniform128 SF arrivals plus the payload arrival. |
| `b8ccad2d` absmax tree, 12+/3− | Replaces one linear reduction loop with a16-entry temporary and nested constexpr tree indexing. Same eight FMNMX3 sites; dependency depth8→3. Affected40 cells: +0.107% overall, −0.022% decode, +0.235% prefill. N3U EP16K MXFP4x8 is −3.569%, repeated −0.938%; per-token unchanged control stays +0.100%/+0.068%. | **Remove as already requested.** The existing linear loop is simpler; reduced static dependency depth did not establish a broad measured benefit. The uncommitted revert remains unqualified because the user paused work. |
| `c1c5402d` TMEM completion plus tuple pairing, 70+/41− | Contains two separable changes: six necessary completion waits, and optional multi-fragment phase batching. Fixed-vs-fixed16 pairing screen is −0.222% overall. Two N3U prefill gains repeat tightly at +0.547%/+0.746% EP W4A4 and +0.431%/+0.477% TP per-token. | **Keep the correctness waits; simplify the optional tuple pairing under the stricter simplicity priority.** Do not revert the whole commit. Pairing has a real but modest targeted benefit, so simplification accepts that tradeoff rather than claiming it is wholly neutral. See the precise comparison boundary below. |
| `77391e28` accumulator exit wait, one deletion | Deletes one proven redundant terminal wait; no new interface, policy, branch or state. Original24 +0.111%; tight K3 TP8 loss −0.516%, repeated −0.310%. Most code loses2–22 instructions; inherited synthetic stack168→160B. | **Keep.** This removes complexity and synchronization. Do not claim a broad speedup; preserve the small accepted decode loss. |
| `b13963b0` FC1 protected span, 17+/10− | One private geometry-derived release-width value is consistently used by storage and both K planners. FC2 retains64; FC1 may use capacity/2. Two affected frozen N3U4096 winners improve +4.923% EP and +1.767% TP, with tight repeats and FC1 completion-frontier gains. | **Keep.** There is meaningful measured benefit from a general ownership rule. No model/dtype/tactic branch was added. This is a bounded two-affected-cell result, not universal benefit. |
| `b52e4e09` FC1 quotas, two literal replacements | Control120→128 and epilogue256→248; gather128, launch168, total64,512 registers unchanged. No new control flow/interface. Synthetic MX stack160→128B,20→16 LDL/STL pairs.20 cells +0.0669%, with tight N3U EP16K −0.205%. | **Keep.** Neutral performance is acceptable here because no kernel complexity was added, and inherited spill pressure fell. No further quota sweep is warranted by this audit. |

## TMEM correctness and optional pairing must remain separate

The completion fix can be expressed in the original serial helper with six extra calls: one entry load-completion wait, three store-to-load waits, and two load-to-overwriting-store waits. Existing caller release/end-of-tile waits must remain. The original helper plus the earlier seven-wait patch is preserved at `../tmem-phase-waits-b139/candidate.patch`; the new final helper wait is unnecessary under the documented true-register-dependency rule and the preserved caller/next-entry lifetime protection. The proof is `../paired-six-waits-7739/PROOF.md` and its independent lifetime receipt.

Optional pairing changes the helper argument into a tuple, its register tensors from `(16,)` to `(16, fragments)`, and the body into repeated constexpr fragment/half loops. It also adapts single-fragment callers to tuples/slices. That contract is not required to fix ordering. It shares phase waits across two fragments and reduces store-completion fence count in the affected bodies.

The appropriate isolation is the saved **completion-correct serial versus completion-correct paired** comparison, not paired versus the original insufficiently ordered helper:

| Case | Original pairing benefit | Separate repeat | Repeat control/candidate spread |
|---|---:|---:|---:|
| N3U EP16K W4A4 | +0.547% | +0.746% | 0.078% /0.035% |
| N3U TP16K per-token | +0.431% | +0.477% | 0.057% /0.156% |
| K3 EP16K per-token | −1.592% | +1.608% | 2.335% /0.122% |

The K3 sign change is inconclusive; original and repeat controls have >2% spread. The two N3U gains are reproducible and must not be dismissed. However, the complete16-cell comparison remains −0.222%, with noisy unchanged single-fragment controls included. These measurements use **seven-wait** variants on b139. They do not directly measure a proposed six-wait serial simplification on the current head. No such simplification was implemented or qualified during this paused audit.

The final paired six-wait versus original7739 screen measures −0.166% overall and tight N3U costs −0.856%/−0.943%. Those numbers include required ordering work; they are not grounds to remove necessary waits or a clean estimate of optional pairing overhead.

## Evidence and limits

- Every percentage is from a saved same-GPU C–A–A–C comparison, using the geometric ratio of phase medians and strict100-sample CUPTI phases. No new measurements were made. Original negative/noisy cells and separate repeats remain untouched.
- SF wide V3 EP16K MXFP8 remains negative in both campaigns, but native FC1/FC2 binaries are byte-identical. Its variation stays unresolved; it is not attributed to new instructions or excused through clock speculation.
- The FC1 release-span qualification admits96 columns under current legal K4/K8 shapes. Its affected epilogues become much larger statically because the existing cyclic path is now eligible; the concrete +4.923%/+1.767% benefit supports that tradeoff. FC2 planner/storage equivalence was separately proved.
- Qualification distinguishes inherited synthetic spill cases from native measured kernels. No statement here implies all compilation signatures were spill-free.
- `audit-proof.json` binds the six Git patches, canonical state, exact evidence hashes, and independently replayed pairing phase arithmetic. The full raw campaigns and prior independent audits remain in their original directories.

Primary records: `gather-sf-arrivals-screen/RESULTS.md`, `swap-absmax-ternary-repeat/ORIGINAL_AND_REPEAT.md`, `paired-vs-serial-tmem-screen/RESULTS.md`, `paired-vs-serial-tmem-repeat/summary.json`, `paired-six-waits-screen/RESULTS.md`, `accumulator-tail-screen/RESULTS.md`, `fc1-release-limit-screen/RESULTS.md`, and `control128-epilogue248-screen-r1/RESULTS.md`, all siblings under the optimization artifact directory.
