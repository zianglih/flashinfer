# Active optimization state

Primary checkout is clean at `49c91adf47d30fc2049c76cbaf34d0ccf3291434`.
Fork PR: https://github.com/zianglih/flashinfer/pull/9
Upstream PR7290 remains unchanged. Do not stop this effort without user direction.

## Initial publication (historical)

- Three retained instruction cleanups, 11 additions / 7 deletions.
- Full historical comparison: 468 cells, 93,600 samples, +0.059% GM (neutral).
- Four heatmaps, 15 native tables, 62 original logs. Artifact commit
  `fa66f71f9ddfaa814089cfa2d0a5d0a75fbded4c`, directory `02de7785/`.
- PR body and four native table comments read back exactly; see `publication/`.

## Rejected terminal PDL wait deletion

- Rejected worktree `flashinfer-terminal-pdl-review` and its branch were retired
  after exact source/patch/status checks. Patch, source, ignored cache and receipt
  remain under `experiments/terminal-pdl/retirement/`.
- Candidate kernel `ec0f3685f42df89160ad1840ad561e728ec757623327bdb2ced29e51d74adb02`.
- Source and native qualification pass: six exact numerical pairs and four
  active/empty/partial graph cases per arm; 27 kernel pairs, zero stack/local.
  FC1/combine/PDL-off binaries identical; nine affected FC2 captures remove one
  ACQBULK and 2–5 non-NOP instructions, no register growth.
- Complete CAAC screen: 56 cells / 22,400 samples, −0.0373% GM; decode +0.0895%,
  prefill −0.1640%. All 25 negatives preserved. Independent raw peer passed.
- The same-UUID ACCA follow-up repeated all three losses: K3 EP MXFP4x8
  −3.967%, N3U TP MXFP8 −1.104%, V41F TP per-token −0.364%. Actual native
  FC2 images show register growth106→118 and150→152 in the latter cases,
  which the small qualification matrix did not expose. Rejected; no rescue,
  further timing or full refresh. Native image audit and retirement are complete;
  both order blocks and all native images are preserved. Never replace the
  original CAAC. Primary source and published plots remain unchanged.
- Evidence: `validation/terminal-pdl/`, `experiments/terminal-pdl/`,
  `evidence/terminal-pdl-screen/1793367348696239000/`.

## Retained W4A16 partial-K dequantization

- Pushed follow-up commit `bf072d26` on fork PR9. Upstream PR7290/base remain unchanged.
- Exact source: kernel `25aa126d6e8e7bec5a42467349496b10a5aa1ef1b2a66b92bbe312c58889e34e`;
  Mega caller `66ec9ae8caf4dbf66ad8f4293a75833e3713bbc279328b2ef43165cf19978c87`.
- Skip a whole transform group outside consumed K; preserve all synchronization.
  Aligned/all-live tails fold to the old path. Mega explicitly passes padded K.
- Existing exact oracles: 12 split calls, four Mega calls. Unaffected representative
  PTX/cubins/SASS identical; affected registers and local-memory use unchanged.
- Full affected CAAC: 39 cells / 15,600 samples, 33 retention cells excluding 1/2.
  All 24 token 4–512 cells improve; decode +1.70%, middle +2.11%. Six prefill
  losses remain, worst −0.75%; the noisy positive aggregate is not a reliable gain.
- Both independent raw audits passed. Evidence and rationale:
  `experiments/w4-tail-dequant/{combined39,RETENTION.md,retention-source-freeze.json}`.
- Completed review source copy retired after exact committed-content checks.
  Publication is verified in `publication-w4-tail/`: 39 fresh cells + 429 reused,
  original external baselines, artifact commit `a9a53858`.

## Retained FC1 integer-carried output stores

- Pushed `49c91adf`: concatenate converted nongated FC1 halves as integer words.
  Preserve quantization arithmetic; widen FP4 stores to 128 bits and FP8 to 256.
  Existing fused FP32 uses typed atomic adds; no new API, tactic, or sync policy.
- Full affected 104-cell N3U EP/TP matrix: 41,600 paired CUPTI samples.
  Excluding 1/2 tokens, +0.64% overall, +2.31% prefill. All 18 quantized prefill
  cells improve (+0.39% to +5.97%). Decode and middle are neutral.
- Per-token is neutral overall; EP 8K (-0.79%) and 16K (-0.54%) regressions
  remain visible. No rescue policy. All 155 timed resource pairs unchanged/LOCAL0.
- Final 16-call exact qualification includes direct fused FP32 boundary cases;
  eight additional gated exact calls yield 12 byte-identical native pairs.
  Representative source/native proof supports reuse, not 364 individual compiles.
- Exact source `482b636a`; scoped pre-commit passed. Review checkout retired
  after committed-content checks.
- Full heatmap/table refresh is published and read back in `publication-integer-store/`:
  104 fresh cells + 364 reused, original historical external baselines. Artifact
  commit `c6f937236e6d91251d7f27c14e4da793c4400497`; all four native table
  comments and PR body verified exactly. Five plots and full XZ archive published.
- Slab-indexed scale scratch and terminal-join deletion are closed read-only:
  no exposed reusable wait; larger scratch loses stages. SiTU is correctly
  classified as Swiglu plus situ_beta. Shared routing publication stays unchanged
  because current generated TRT consumer coverage is incomplete.

## Diagnostics and rejected work

- New W4 N3U TP profile: tensor86.88% FC1 /73.29% FC2; post-store waits negligible.
  `profiling/n3u-tp-w4a16-16k/`; raw native PC/ELF peer passed.
- V3 TP MXFP8 combine:84.82% DRAM, negligible MIO, no barrier stalls. No new
  combine candidate; prior LDG256/vector-outer experiments remain closed.
- Adjacent FC1 payload-store join rejected before timing: explicit local-memory
  lowering, no wider stores. Source copy removed, patches/evidence preserved.
- Both fixed weight-cache policies rejected. Static-SF source copy retired after
  retaining its change. The rejected terminal-PDL worktree is also retired;
  completed W4 tail and integer-store worktrees are also retired.

Original C2 devbox `fi-gather-pipeline-1030` remains active. The parallel infra
node was released; persistent C++ caches remain intact. Current GPU ownership is
coordinated by agents; verify before launching. No sanitizer runs.

## Rejected FC1 store transaction granularity

- Candidate `faae8834` passed 16 exact calls, zero local memory and source gates.
  Quantized paths were identical; BF16 restored the pre-join cubin but added
  46 static instructions, and fused FP32 restored lower register use.
- Full 26-cell / 10,400-sample CAAC: +0.085% overall, TP -0.009%. EP 8K/16K
  gain +0.700%/+0.692%, EP4K loses -0.229%. All 10 negative retention cells,
  30 unchanged resource pairs and 416 normal clock quartiles independently verified.
- Rejected: broadly neutral outcome does not justify another kernel loop.
  Completed review checkout removed; source/patch/receipts remain under
  `experiments/fc1-store-granularity/retirement/` and performance evidence under
  `experiments/fc1-store-granularity-performance/`. Main stays clean49c91adf.
- At retirement there was no active source review checkout; subsequent active
  experiments are listed below. Persistent caches remain intact.

## Completed native diagnosis and current leads

- N3U TP MXFP4x8 T32 profile, retained49c-equivalent input, frozen tactics;
  GPU4 is released. Owner report and independent native/dependency audits pass.
  Existing200 CUPTI samples establish125.569us; NCU is diagnostic only.
- 385 live experts, max7tokens/expert; both FCs read about269MB, nearly all weights.
  FC1/FC2 DRAM54.01%/69.03%; physical/logicalM128, channel_tiles1, routeN16,
  one CTA, static schedule. Mixed FP4 weights occupy unpacked Int8 SMEM slots.
  FC1K256/five stages versus FC2K128/ten stages; same215936B shared footprint.
- FC2's hot multiply waits for global expert alpha, not its earlier TMEM load.
  That alpha-prefetch mechanism is already closed history. No stage sweep,
  cache rescue, or new tactics follow from these counters alone.
- Wider activation-SF cp.async through a different shared descriptor is closed:
  the required sub-16-byte permutation cannot be expressed while retaining the
  current TMEM image. See `audits/sfb-vector-layout/`; no GPU experiment.
- Current bounded lead: distribute independent gather-barrier initialization,
  retaining every barrier/count/fence and rendezvous. Check actual native lowering
  before timing; lane-varying addresses may serialize despite fewer PTX sites.
- `flashinfer-gather-barrier-init-review` is the sole initializer candidate,
  unstaged kernel SHA35238828. Four exact calls pass; native initialization lowers
  to two predicated shared stores plus one cache invalidation, with no address
  serialization. Registers/local memory unchanged; narrow hot-body instruction
  churn remains a concern. Additional SF16/CLC/PDL qualification uses GPU6;
  a bounded cross-model EP/TP timing screen is being prepared for GPUs0–1.
- W4 read-only lead: a partially live transform group may contain wholly unused
  decode/store fragments. Require concise compile-time clipping and unchanged
  full-stage scheduling before any source or GPU experiment.
- W4 source prototype is authorized in `flashinfer-w4-partial-group-review`,
  based on49, final kernel SHA b25dacfa. It rounds clipped K to the existing
  32-value decoder unit to preserve generic M-major K16 acceptance. Root source
  review passed; bounded exact/native qualification is authorized on GPU2.
- MMA early-readiness TEST candidate e9088366 is rejected and its local source
  worktree/branch retired. All56 CAAC cells passed raw/union audits: −0.03633%
  overall, 36 negatives, no exposed clock exception; added state/instructions and
  five FC2 register increases are not justified. Original11 and recovery12 whole
  jobs retain separate native-library cohorts. See `experiments/mma-readiness/`
  for source patch, retirement receipt, qualification and complete raw/results.
- Initializer qualification now totals eight exact calls / 12 native pairs,
  with unchanged resources and unaffected FC2/combine binaries. Root setup audit
  passes for its 56-cell, 22,400-sample CAAC screen; launch on GPUs0-1 is authorized
  after the remaining independent setup and runtime cache/idle checks.
  Main and published PR9 remain clean at49c91adf.
