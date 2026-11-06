# Independent synthetic-routing review

Source: `1e69d0a39` plus patch `ef52e932454d125d70452690ce479a0fe15faefc1cb190ea2d7d00ad80ae40cf`.
No source or harness edits and no GPU work by this reviewer.

## Source scope

`source-scope.json` independently checks both source hashes and AST boundaries.
Only `CuteDslFusedMoERunner.__init__` changes among existing runner methods.
The separate W4A16 runner is AST-identical, and all existing swap-AB tactic
functions are AST-identical. Every existing GPU implementation and public API
callsite remains unchanged.

The swap-AB constructor picks a private seeded global FP32 score/top-k
initializer and omits the balanced pre-hook. The False branch retains the old
seeded randint initializer and `CuteDslMoEInputsHelper.inputs_pre_hook` without
arithmetic changes. Rubin cannot enter the new branch through the public API:
existing swap-AB device validation still restricts the mode to SM100/103.
There are no other production consumers of `runner._inputs_helper` that require
it on the new branch. Shape/stride/cache-key/tactic logic is untouched.

The generator is newly allocated and seeded on the supplied device per profile;
it does not capture caller tensor references, mutate serving inputs, retain
profile state on the runner, or read tensor data on the host. Top-k returns
unique in-range IDs even with tied scores. The initialized tensor has the
requested device, shape and dtype. Nonzero EP offsets operate by selecting
ranges from the same global routing draw, without an offset-specific branch.
The existing autotuner rejects input synthesis during outer capture; warm
captured cache hits skip the initializer. `None` pre-hook is valid generic
TuningConfig behavior.

Largest score storage is O(tokens * experts), e.g. 56MiB for K3/16384, plus
transient top-k outputs/scratch. This is outside tactic timing and needs the
recorded allocator measurement; it is not claimed to reduce setup cost.

## Gate and orchestration review

Route-gate source covers four models, four formats, all22 native buckets, all
EP offsets, uniqueness, deterministic shape-local draws, CPU/GPU global RNG
preservation, rank-count conservation and capacity bounds for all five route
tiles. Its nonzero offsets and zero-local cases are route-allocation coverage;
the separate eight-case public API/capture gate uses an all-local offset-zero
fixture and checks input byte immutability, warm graph behavior and two profile
sizes. No new kernel arithmetic is introduced. The immediately preceding
zero-local holdout independently executed all320 admitted N3U4096 tactics with
zero local work on the same retained GPU implementation.

The paired runner preserves fresh per-source native AUTO, the original native
NV eager/MX graph mode, no fused finalize, included NV input quantization,
separate source-private compile caches, and frozen C-A-A-C with100 CUPTI samples
per pass. It verifies identical admission count/hash for every full profile,
unchanged saved winners, prepared cold-batch pointers and candidate routing
hashes against the independent route gate. The SystemExit(0) completion fix is
present in the wrapper.

One prelaunch evidence improvement was requested: persist `route-gate.json` SHA
in the receipt and verify it before each phase, since profile-route validation
uses that artifact. API-gate SHA was already pinned. No functional blocker was
found. The final source/cache/sample audit is complete below.

## Separate eager/graph diagnostic adapter

Read-reviewed `tuning-measurement-audit/tools/observe_policy.py`. It changes only
the two existing public `autotune_use_cuda_graph` keyword expressions through
an asserted AST rewrite, uses unchanged source/native observer, and preserves
native v1 event timing, repeats and delay settings. No wrapper/source edits by
this reviewer. Recommended orchestration assertion: require complete nonempty
profile records matching admitted tactics and shapes, so native tactic-error
handling cannot silently swallow a timer-contract assertion. Its
`local_histogram` field contains global expert counts (a label issue only).

## Archived gate verification

`gate-audit.json` independently verifies all352 route cases,2,464 rank
histograms,88 distinct model/token shapes,16 legacy configurations and8 public
API/capture cases. Rank totals, nonzero offsets, per-expert counts, allfive tile
capacity bounds and all recorded hashes agree. Seed515 has zero-local draws
only at1/2tokens; none occur at tokens>=4 for any model or EP offset.

The16K transient allocator peaks are17.5MiB(V3),25.125MiB(V41F),
83.4375MiB(K3),60.5625MiB(N3U), including top-k scratch. These are untimed
setup measurements, not throughput claims. Both source manifests and launch
source identities match the reviewed patch. The gate launch config predates
addition of instrumentation metadata; its candidate source record is identical
to the final config. The initial immutable sidecar pins both outputs, final
config, runner, instrumentation and launches. The final receipt is checked below.

## Final independent result audit and disposition

`result-audit.json` verifies all18 phases,1,800 CUPTI samples and86 native
profile records (43 paired geometries), including identical admitted tactic
sets, source/cache identities and route-gate bindings. Recomputed speedups
(control/candidate minus one) are -1.5132% for N3U MXFP4x8 T4, -0.2637% for
N3U PER-TOKEN T4096, and -0.2849% for N3U W4A4 T4096. Control endpoint drifts
are -0.0827%, +0.1100%, and -0.3073%, respectively. All winner changes are
K-step choices. The W4A4 change is within drift; no case demonstrates a gain,
and the MXFP4x8 loss is larger than either arm's drift. Reject the candidate
and stop the broad screen.

The sidecar proves an initial hash pin during control AUTO and unchanged final
hashes. Its first watcher failed with a preserved Python syntax error; the
corrected watcher started after all workers completed and recorded one final
snapshot. There is no claim of continuous per-phase monitoring. Original
errors, sidecar versions, initial pin, source, results and gate artifacts remain
archived. Candidate cleanup belongs to the implementation owner; retained
control and compilation caches are preserved.
