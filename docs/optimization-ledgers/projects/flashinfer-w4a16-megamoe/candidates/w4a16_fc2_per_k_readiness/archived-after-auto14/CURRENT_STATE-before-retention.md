# Current state: retained F4; finer FC2 readiness under validation

Primary contains the five-file FC2 readiness experiment on pushed
`21fd7ce48b0a7406175191aa5542f0578a6371e8`.
Draft PR: https://github.com/flashinfer-ai/flashinfer/pull/5019.
No new best is claimed and the published Final performance table is unchanged.

## Exact tail reduction: closed, not retained

The complete four-F4 True sweep ran all 14 token counts 1–8192 with 100 cold-L2
CUPTI samples each on hu-pdx-15. Original session 36361 exited 0 in 434.662663s;
closure/fetch80425 passed. Actual measured source 0bf9 and native 06752caf are
preserved. Saved checks pass 14 rows,112 selections/winners,56 candidate rankings
and1400 samples: proof 36734a25, result 4ab0acec, comparison 20615c85.
The first local reader failed only because macOS /usr/bin/python3 is 3.9;
the unchanged saved checks passed under the existing modern Python.

Against the complete retained F4 run, geometric latency over 8–8192 changes
by **-0.175331%**, with 6/11 rows lower. All 14 selected dictionaries are unchanged
apart from the intended reduction flag. Matched hot scores generally save 0–3us;
several cold changes disagree with hot results. This is not a compelling gain
for 155 added implementation lines. No statistical-confidence claim, baseline
replay, split replay or row replacement.

[Full before/after and matched hot tables](logs/cu132-exact-tail-vs-retained-f4-auto14-comparison-001/README.md).
All native/resource, exact numerical, graph and grid-stride checks passed before
performance. That functional result remains valid despite non-retention:
18 EP1 cases,4 EP2 graph cases per rank,5 seven-round routing calls per rank,
and one additional H2048/I256/n512 grid-stride reference call per rank.

Before restoration, all six changed files were verified byte-exact against
measured source 0bf9. Complete patch 76c7d8c, full files and the preceding detailed
CURRENT_STATE are preserved in `candidates/w4a16_exact_tail_reduce/archived-after-auto14/`.
Primary was then restored exactly to 21fd. The failed first native attempt and
the successful descriptor correction remain archived too. The held ten-line
static metadata cleanup is unused. Remote restoration completed with
source/native/idle checks only, original 95355 exit 0 and receipt 26c73685.
Restored source 578f46ab matches 21fd; inventory 06752caf is unchanged.
No GPU work was replayed.

## Next experiment in preparation

The requested early weight-decode overlap already exists: the scheduler is
released after routing-count exchange, before remote payload pulls; weight
loading and both decode WGs proceed independently. Only activation loading
waits for its routed-token tile or FC1 result. N64/N128 retain D3/D2 TMEM rings.
See `candidates/w4a16_pipeline_orchestration_review/EARLY_WEIGHT_DECODE_AUDIT.md`.

A distinct candidate lets FC2 consume ready K256 activation regions while later
FC1 feature regions finish. Source/progress audits find no blocker, but the
useful overlap window remains unmeasured. The held design uses one completion
bit per 64 I CTA report, packed 32 per word, GPU-release one-hot ADD and cached
GPU-acquire masks. I=2048 can retain one completion word per token block; larger
I uses more words. A small payload-aware specialization should reuse existing
batching and phase flushing. No vendor body, weight layout, dequant instruction,
role count, stage policy or public tuning axis change is intended.

Reviewed patch `3d87ac8978817c4fbf08fa17896332d106c89c1ffac87c752784082ee2f0aed5`
under `candidates/w4a16_fc2_per_k_readiness/` is now ported to primary: five
files, seven net added lines. Scoped pre-commit hooks, including mypy and Ruff,
and whitespace checks passed. Frozen source is b65b7417, manifest 502c27a1.

Four native captures passed in 16.51 seconds: public N64/direct and N128/reuse,
I2112 word rollover and M128/C1 static-S3. All retain 96 registers, 640 threads,
zero stack/local memory and their expected raw/B/decoded stages. Actual code
review verifies per-lane release payloads, bitwise inclusion, cached acquires,
logical K versus stage wraps and the second mask word.

Original 85562 passed all existing-helper groups and closures: five routing
calls per rank (40.66 seconds), three EP1 graph cases (23.65 seconds), and two
EP2 graph cases per rank (28.72 seconds). Completion 85f77912. Manual graphs
cover epilogue batch1; routing covers batches2/32 and partial/empty/refill cases.

Full performance run `cu132-fc2-mask-f4-auto14-direct-001`, original session
3477, is now active on the public four-F4 catalog: all 14 token counts 1–8192,
100 cold-L2 CUPTI samples each. No concurrent GPU work. No speedup or retention
decision is claimed until the complete result is checked against retained F4.

Review caught that FC2 epilogue also consumes the scheduler peek bit to prefetch
return metadata before its accumulator wait. The revision preserves this path
by peeking input/metadata readiness for both phases, with one pointer and no
phase branch. FC2 activation still checks each independent K256 mask. The
superseded FC1-only peek draft a697 is preserved in preparation history.
Coverage includes partial-I thresholds 1–4, bit 31/word boundaries, delayed
batch flush, logical-K indexing, graph replay and empty/refill reset.
Source design: `candidates/w4a16_pipeline_orchestration_review/FC2_PER_K_READINESS_DESIGN.md`.

## Retained publication and validation

Public four-F4 catalog commit d6f8502 keeps N64/N128 × direct/reused return;
manual F8 stays supported. Measured F4 source 99681e83 / result d4f1a618 is exactly
the promoted ordered subset. Paired same-node split result a66e1894 supplies the
published full 1–8192 table: geometric split/Mega 1.142387284x over 8–8192,
all 11 rows favor Mega. Final table 99805930 is under
`candidates/w4a16_publication_split_refresh/recovery0911b/`.

Later cleanups remove 919 net implementation lines across their cohorts:
a26dc8b88 restores the useful winner field; c8155c6f inlines 32 host-only lines;
21fd7ce48 specializes 21 lines of required readiness-pointer state. The c815
AUTO lifecycle tests passed (2 EP1 and1 EP2/rank); the later False native
controls are byte-exact to saved N64/N128 encodings. Each result retains its
original source attribution. PR body 6489d840 was published/read back exactly
on draft 21fd; the Final section is unchanged since F4 publication.

## Runtime and operating rules

Sole remote executor: iteration_prep. Devbox fi-w4a16-mega-0911b, c2,
namespace ziangli, node hu-pdx-15,8 x B300, image nvcr.io/nvidia/pytorch:26.05-py3.
CUDA 13.2.78, driver 590.48.01, PyTorch 2.12.0a0+5aff3928d8.nv26.05,
CuTe DSL 4.7.1/native compiler 13.3.27, CUPTI 13.2.0, NSYS 2026.2.1.210,
NCU 2026.1.1.0. Native inventory 06752caf; environment 04b4b783.
Use managed /usr/local/bin/h from the project HAI checkout. No CUDA 13.0 work.

Every performance decision uses one complete 1–8192 sweep with 100 CUPTI samples,
reporting 1/2/4 but excluding them from retention. Reuse the completed Mega
baseline; split is only for a necessary publication refresh. Keep exactly two
decode WGs and five total. Closed CLC, custom transport, share_operand_release,
N256, K128 and one-decode-WG designs stay closed. Preserve experiment artifacts;
keep history local and PR Final concise. The detailed ledger is
`w4a16_optimization_experiments.md`.
