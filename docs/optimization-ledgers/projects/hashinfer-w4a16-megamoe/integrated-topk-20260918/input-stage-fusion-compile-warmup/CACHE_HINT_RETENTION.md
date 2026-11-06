# Separate cache-hint trials

Base: frozen host-only `7dc9626909834bc70209e09784e9dfdebadceff2`. Qualify its128 CUBIN identities against f655 plus focused11 native graph cases and queued96 first. The two prepared successors each contain one existing patch; neither combines hints or adds an autotune knob.

| Trial | Frozen commit | Owned change | Existing patch |
|---|---|---|---|
| Activation source | `4d527ac603cc61eaee31ef490b03ca43cbb85883` |128-bit caller-activation loads use L1 no-allocation in the constexpr vector path; generic path unchanged | `4d20f000b26fc90c259b17e8bb304b8b534874e7` |
| FC2 partials | `8b8b1ec551635f85f43b965a46757e2b48a67933` |128-bit owned combine-partial loads use L1 no-allocation | `39fa0ef35a3d0f7486eb1cbb9a7058bd1df58893` |

For each trial separately:

1. Reuse the existing four-tactic/four-ABI capture workload and helper with exact new source pins. Confirm the intended PTX/SASS cache policy is attached to the specific source load, with preserved width, fences/barriers and resource limits. No hint is synchronization. Check exact outputs against the qualified base. Activation-source generic ABIs should retain baseline code; do not infer that from source alone.
2. Reuse the existing queued96 contract records after capture exactness and codegen review. Skip the focused11 graph-file suite for these isolated load-policy changes: host/ABI/capture behavior is unchanged, and activation-source generic CUBIN identity is checked in step1. The11-case gate remains required for the7dc host change itself. Stop on numerical/capture/lifetime failures; add no new numerical matrix or sanitizer suite merely for a cache hint.
3. Run one full1–8192 AUTO sweep per trial using the same100 cold-L2 CUPTI samples,3 warmups, EP8 H7168/I2048/E256/K8, O3 and rank-MAX methodology. Reuse the sealed7dc baseline arm rather than rerunning split or prior integrated controls. Report all14 token rows, selected tactics, median/MAD and `7dc/trial` speedup.
4. Use8–8192 for retention; retain1/2/4 in tables. Prefer a clear improvement without meaningful regressions in retained rows. Treat tiny or mixed movements as inconclusive rather than claiming a gain from the hint. Inspect sample spread/quarter trends before proposing an extra run. A source hint alone is not enough to promote a performance change.

Timing and profiling remain sequential under the sole GPU owner. No candidate is queued by this preparation. The measured7dc sweep is a prerequisite; f655 has no timing arm to silently substitute. Secondary f655 numerical/sanitizer results remain labelled by their actual source and transferred only through the explicit device-identity bridge.

Each trial directory contains its original patch, scoped-hook/whole-module AST reversal evidence and104-file frozen manifest. Preserve both older f655 trial checkouts and all existing evidence.
