# Dispatch flag batching: source audit

Read-only audit of retained checkout `4733b0602` after the N256 revert. No new timing, source edits, or runtime validation. Paths below are relative to `flashinfer/`.

## What F4/F8 changes

W4A16 forwards `flag_batch` to the shared `TokenInPullTokenBackPush` constructor (`flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py:279`). The transport accepts values1–32 (`flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py:413`). It drains each token's payload bulk store before accumulating that token's FC1-ready counter address, using constant phase0; it flushes any remaining addresses at the end (`token_comm.py:1112–1146`). F4/F8 therefore does not change payload TMA size, outstanding-store depth, or the per-token completion wait.

The tracker assigns each pending address to a different lane and fires at the batch threshold or phase change (`src/src/flag_batch.py:69–88`). Each occupied lane then issues its own GPU-release `+1` reduction (`flag_batch.py:111–119`). **This is not atomic-count coalescing:** eight tokens still require eight counter increments. F8 can reduce warp-level publication instruction episodes by publishing more active lanes together, while delaying earlier tokens' readiness. The dispatch tracker does not flush merely because the counter address/expert changes. FC1's activation loader waits until the task counter reaches its valid-token threshold (`token_comm.py:580–598`). Batches shorter than four reach the same tail flush under F4 and F8.

`epi_flag_batch` is independent. W4A16's pair controls publication of completed FC1 work tiles and completed FC2 work tiles. FC1 updates its task counter; FC2 publishes only for dispatch-warp return. These use the next work phase and a final tail flush (`nvfp4_w4a16/epilogue.py:188–199,224–236,370–389`). The default autotune catalog fixes this pair at `(2,4)` while varying dispatch F.

## Actual catalog and default scopes

| Backend | Current default AUTO catalog | Cache-miss/default profile |
|---|---|---|
| W4A16 | Eight: N128/N64 × F4/F8 × direct/reused dispatch return; fixed S2 and epi `(2,4)`. | F4, N128, direct return, epi `(2,4)`. |
| NVFP4 W4A4 | F4/F8;24 candidates for default BF16 combine with in-kernel reduction enabled,12 when disabled. | F4 below2048 tokens; F8 at2048+, alongside geometry/return-mode changes. |
| MXFP8 | F4/F8 × two return modes: four candidates; two when in-kernel reduction restricts return mode. | F4 in both size profiles. |
| BF16 | One candidate, F1 and epi `(1,1)`. No default F4/F8 sweep. | Same F1 fixed profile. |

Sources: `nvfp4_w4a16/autotune.py:102–123`; shared `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/shim/autotune.py:52–122`; `shim/tuner.py:85–169,202–209`. The broader shared enumeration exposes F1/2/4/8/16 (`shim/tuner.py:53–70`), distinct from these curated AUTO lists.

W4A16's direct frontend dataclass defaults are **F1/epi `(1,1)`** (`nvfp4_w4a16/frontend.py:41–42`). An absent knob dictionary resolves the cache/default profile, whereas an explicit dictionary, including `{}`, bypasses that lookup (`frontend.py:473–503`). Thus constructor F1 and cache-miss F4 describe different entry paths. Cached winners can override the profile.

## Simplification decision

The readiness-versus-publication-cost tradeoff makes F a meaningful tuning axis in principle; sibling inclusion alone does not establish a W4A16 gain. Matched fixed-F4 and fixed-F8 sweeps should each retain N128/N64 × both return modes, identical source/inputs/timer, and independent fresh knob caches. Compare the completed rows and actual same-tactic scores without attributing noise on unchanged choices to F. If F8 supplies no material benefit, fixing F4 halves the current candidate count from eight to four while retaining both geometries and return modes. The source audit does not establish a universal winning F value.
