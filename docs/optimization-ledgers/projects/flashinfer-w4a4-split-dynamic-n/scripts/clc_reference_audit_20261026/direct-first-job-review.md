# Direct first-job reuse audit

Recommendation: defer implementation. Source inspection does not expose a free reuse of the startup prefetch metadata across worker roles. First establish whether the isolated TMEM startup separation leaves a material initial-info wait. This is a read-only audit of retained `9b4721b08057d0a488c1f0236467acb75c48cd00`; no source clone, source edit or GPU run was made.

## What is already available

In `blockscaled_contiguous_grouped_gemm_finalize_fusion.py`, common initial-work construction (1472–1488) computes the physical cluster's first coordinate. With prefetch enabled, only warp0 reads the live-count bound and initial expert (1496–1497), then primes A/SFA stages. It does not read valid rows, and the expert is a warp0-local value. At 1551–1552 the live count is read for ordinary work. Each worker role then calls `next_work` (1574,1809,1948), which waits for the metadata slot, reads tile/expert/valid, releases it and advances its consumer state (1233–1247). The scheduler supplies those fields once per CTA (2093–2146).

The direct coordinate is reusable without extra memory traffic. The complete record is not: producer SF loading and MMA require valid rows, and producer/epilogue roles also need the expert. Registers cannot transfer warp0's cached expert to other warps. Shared initial storage plus publication/wait recreates a handoff; CTA-wide publication adds a join. Independent per-role loads avoid that handoff but duplicate metadata loads. Reusing warp0's expert while other producer warps read independently also introduces ownership-dependent initialization and pointer/value lifetime concerns.

## Safe first-record bypass, if later justified by a trace

A clean semantic design omits the initial live item from the info stream entirely. Workers process their direct initial live item and leave info consumers at initial index/phase; the first canceled live item or terminal record is then the first ring entry. Scheduler must omit exactly the same initial live publication and not advance its info producer for it. Response query/consume/release state still advances once per issued query. No synthetic release or phase offset is needed.

This bootstrap must be separate from the ordinary tile loop to avoid a permanent first-tile predicate. It would require either a distinct initial-query sequence or factoring shared query logic. The initial slot is known empty, but retain an explicit acquire-before-claim contract; do not silently relax the later query ordering or introduce a deeper queue. Repeatedly acquiring the unadvanced initially empty slot is semantically valid but adds work, so it is not automatically a useful implementation.

Initial padded work cannot become a terminal worker item: the current scheduler may still cancel live work later. Such workers must wait for the first actual published item while the scheduler preserves its current padded-ticket claiming loop. If there is no live work, the existing terminal record must still wake every waiting worker. Both CTA ranks derive the same logical route/tile and must make the same direct-versus-wait decision; local rank-dependent channel offsets remain unchanged.

PDL permits pre-wait metadata reads only under the existing routing-publication prerequisite. When that prerequisite is absent, direct metadata decode must stay after the dependency wait. B/SFB and activation payload remain after the wait. The initial operand prefetch still skips precisely the same first tile/stages, and delayed scheduler wait, response tail, final join and TMEM free remain intact.

Leaving the initial scheduler publication in place while simply delaying its consumer release is unattractive: the one-slot metadata ring then holds the initial item until after first-tile computation, losing the lookahead currently enabled by immediate metadata release. Advancing consumers without the actual corresponding release is incorrect.

## Prior evidence and decision

The related static one-CTA `pdl_first_metadata_experiment` passed its changing-route gates and moved initial metadata before the dependency wait, but remained unretained because it introduced three first-tile branches for mostly noisy gains (`PDL_PIPELINE_AUDIT_2026-10-25.md:102–104`). Its corrected patch was `fb34e3e6ed0dfe871d7c1f34f513f3b7dfb0ec1b2159dc5f273acf3ceefea2eb`. This is not an equivalent CLC first-record bypass; the scoped ledger search found no such executed trial.

The FlashMLA reference derives a simpler first job directly. Our extra expert/valid metadata makes copying that policy a different tradeoff. The current TMEM candidate allows the scheduler to publish its first record while workers wait for allocation, which may remove the startup dependency without changing the record protocol. Until actual codegen/trace evidence demonstrates remaining first-info latency, a separate bootstrap, duplicated loads and phase-special treatment do not meet the requested small, maintainable optimization standard.
