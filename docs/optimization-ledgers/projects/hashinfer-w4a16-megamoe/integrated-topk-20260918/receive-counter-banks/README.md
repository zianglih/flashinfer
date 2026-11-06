# Alternating receive counters — isolated experiment

Candidate `b6fd43a026c4fb791e53e37da2cc1d4bc43a26aa` against retained
`7dc9626909834bc70209e09784e9dfdebadceff2`. **Unrun and unpromoted.** Only two
owned W4A16 files change (+66/-38). No protected shared-source edits or public
configuration options. Scoped pre-commit and `audit_source.py` pass.

The default tail already runs ordered deterministic reduction beside counter
cleanup. This experiment removes cleanup's cross-rank zero-publication barrier
by using two receive-counter banks; it leaves input publication, the FC2 drain,
both full-CTA tail rendezvous, and all producer fences unchanged. It is an
alternative based on retained 7dc, not a stack on the marginal local-ready trial.

## Implementation and lifetime

- Duplicate only the symmetric `expert_recv_count` and `_sum` regions. For
  E256/EP8 this adds 2,304 bytes; EP4 adds 2,560 bytes. Each bank is independently
  aligned. The reset prefix covers exactly one bank, including its padding.
- Keep one device-maintained bank word in each tactic's own local workspace,
  outside the zero prefix. Workspace creation zeroes both banks and this word.
  The word is stable during the entire dispatch/scheduler phase; one dispatch
  lane toggles it after cleanup. Eager and graph calls use this same device
  state. There is no host-side generation selection.
- At kernel entry, snapshot the selected bank and shift all related views:
  receive counts, packed count sum, the scheduler's Int32 stride-2 size alias,
  and the reset prefix. Cleanup uses that old selected view, not a reread of
  the changed bank word. Independent generated review must confirm this.
- Launch n+1 may begin publishing to the other bank while a slow rank clears
  bank n. Launch n+2 cannot publish to bank n until it has completed n+1's
  input barrier. Every participating rank must have completed n, including
  its bank-n clear, before it can enter that intervening input barrier. That
  barrier also carries the zero stores through the existing system release /
  acquire protocol before reuse.
- Next-generation combine writes remain behind that generation's input
  barrier. A fast peer cannot overwrite a slow current reducer's data before
  the latter finishes its current kernel and enters the next invocation.
- Input publication and drain each contribute two software-grid phases, so
  the grid counter is zero before rank-local reset. The NVLink counter remains
  persistent and runs two calls per ordinary invocation. The next opposite-slot
  barrier prevents reuse overtaking a slow old waiter. Optional kernel-replay
  padding becomes two extra calls (four total); that mode is not covered by
  the normal application-replay qualification and must not be claimed tested.
- The same protocol applies to staged/raw and deterministic/IKR modes. The
  default reduction still consumes BF16 returns in ordered FP32 arithmetic.

## Checks and next gates

The CPU check executes the actual shared-layout definition for 30 EP/expert
configurations and verifies both banks/aliases have equal byte displacements.
An abstract rank-interleaving model covers five invocations for 2, 3 and 4
ranks (155 / 697 / 3,167 reachable states). It checks the two-generation clear /
publication reuse bound and previous-output lifetime. This is **not** a GPU
memory-model proof: actual system publication, pointer lowering and the grid
barriers must still be reviewed and exercised.

Before timing: independent source review; 128-ABI generated capture and finite
bit-exact retained-output comparisons; check the bank read/toggle placement,
alias offsets and reduced barrier count; strict O2/O3 all-tactic numerics;
back-to-back graph/eager stress with repeated bank reuse. Run the existing
1–8192 full CUPTI sweep against same-node retained 7dc. Full accuracy and
mem/sync/race suites are required before any promotion. No performance claim
follows from the source reduction or existing NCU replay counters.

Artifacts are frozen in `frozen-source/`. The initial read-only design and
independent feasibility review are in the parent effort directory. A
profiling-only phase timestamp harness remains optional if end-to-end evidence
needs a causal explanation; it is not a prerequisite for measuring this
bounded implementation after the correctness gates pass.

Independent source review `f532230bba69e0c306d73a6335dc28b0df9f4cbd009cdc30b54a739fc2a8258b`
and prepared hu9 helper review
`121a755295f81d8d028f977a5929499805ded4723132e51463867c5f535589ec` pass.
Bounded capture is authorized only after the current 58dd sweep seals and its
GPU/process closure is verified. Expected generated transport barrier sites
change from 16 to 12; both 640-thread tail handoffs must remain. No GPU run has
started at this note. Raw/pre-staged and opt-in IKR existing-test coverage is
being prepared separately; queued fused zero-output calls are not a substitute
for the exported raw-thunk ABI.
