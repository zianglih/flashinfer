# Candidate: separate current cleanup from next-launch count publication

Read-only design proposal; no implementation, launch or correctness claim.
Retained source is 7dc9626. Evaluate current smaller trials first.

## Motivation

The retained deterministic tail already overlaps reduction with counter
cleanup. Starting reduction earlier cannot shorten completion when cleanup
remains the longer side. One substantial remaining cleanup dependency is the
second tail NVLink barrier: it publishes zeros of the symmetric expert receive
counters before a fast rank can begin its next invocation's count writes.

Two alternating banks of only those counters may remove that cross-invocation
write/clear conflict, allowing removal of that *cleanup publication* barrier.
The input publication and FC2 drain barriers must remain unchanged. This is
different from consuming incomplete FC2 data or relaxing reduction precision.

## Proposed ownership

- Bank only `expert_recv_count` and `expert_recv_count_sum`. Source-token
  metadata, input buffers, FC1/FC2 buffers and combine storage retain their
  current allocation and lifetime. Counts are a small part of the workspace.
- Add one rank-local launch-bank word outside the bulk-zero prefix. Initialize
  both banks and this word to zero on workspace creation. The bank word is
  stable throughout dispatch/scheduler use; toggle it once only after the
  existing all-producer retirement rendezvous and FC2 drain. The next local
  invocation reads the toggled word through ordinary stream ordering.
- Do not derive the bank lazily from the live NVLink phase counter: that
  counter advances while this kernel is running. A stable launch-bank word
  avoids introducing a new startup barrier merely to capture its old value.
- Build the existing receive-counter views for the selected bank inside the
  owned kernel. All peer addresses must include the same bank displacement.
  Preserve universal shared transport helpers rather than editing the drop.
- Clear only the current receive-counter bank after drain. The next invocation
  writes the opposite bank, so a fast next invocation cannot race this clear.
  Rank-local counter cleanup remains after the final dispatch grid broadcast.

## Required proof before implementation

1. Ranks advance through the same sequence of collectives and hence agree on
   the bank for a given invocation, including eager/graph transitions, empty
   ranks and repeated graph launches. Host-side toggling is invalid for graph
   replay; this is a device-maintained generation.
2. A rank cannot enter invocation n+2's count publication while another rank
   still clears bank n: invocation n+1's input barrier requires that slower
   rank to have completed n and entered n+1. This is the candidate bound on
   reuse distance, not a claim that peer ranks finish their kernels together.
3. All consumers of the current bank and source-token metadata have retired
   before drain/cleanup. Current reduction reads only local routing scores and
   returned FC2 values. A fast peer's next input publication must still gate
   any next-generation combine writes until slow current reducers finish.
4. The last dispatch grid-sync counter is zero at completion before it is
   included in local bulk-zero. For the production path, input publication,
   drain and cleanup each currently contribute two grid phases. Removing the
   cleanup pair leaves four, also even. Verify all optional profiling/raw/IKR
   paths explicitly; do not generalize solely from the default count.
5. NVLink's existing two-slot/four-phase protocol must remain valid with two
   calls per production invocation and across back-to-back launches. Its
   phase counter already persists. Optional NCU padding requires separate
   analysis; do not silently retain obsolete call-count comments.
6. Workspace layout must provide equal aligned bank strides. Bulk-zero must
   select one bank rather than clear the entire doubled prefix. Pointer-bank
   selection must not happen after the launch-bank toggle, including compiler
   lowering. No post-drain consumer may reload the new bank accidentally.

If these conditions hold, reduction can overlap short local cleanup without
waiting for a second cross-rank publication. Costs include one persistent
generation word, one device load per actual bank-using role, one toggle,
additional pointer offsets and a few KiB of symmetric storage. Benchmark all
1–8192 rows and preserve bit-exact/sanitizer gates. Measure phase durations
with a separate profiling-only variant before claiming a meaningful available
window; full-set NCU replay counters do not establish that window.
