# Boundary for earlier FC2 consumption

The current local-ready prototype overlaps reduction with the final local
broadcast/cleanup. It still waits for all ranks to finish all returns. Its flag
must not be moved before the inherited system acquire merely because a local
decoder or scheduler has retired.

A larger follow-up could publish completion per expert, letting retired
workers reduce tokens whose routed experts have all finished while other
experts continue. This is a different transport protocol, not a relocation of
the current flag. It is not implemented or queued.

- Dispatch-return mode already has a full-transfer wait for each returned
  token. An expert certificate would require counting **completed returns**,
  not reusing the existing expert-side FC2-production counter. A last returner
  could notify only source ranks that have routes to that expert.
- Epilogue-return mode writes hidden slices from several CTAs directly to
  peers. It would need a complete expert/tile accounting proof before issuing
  the same certificate; currently it does not maintain the dispatch mode's
  expert-done counter. Per-hidden-element or per-vector remote atomics would be
  an undesirable starting design.
- The certificate should identify the invocation. A boolean cleared during
  the next source prologue can race a delayed previous expert's notification.
  A consistent launch generation and unique expert producer would avoid that
  ambiguity, but initialization, empty experts and queued relaunch must be
  explicit. The existing all-rank next-launch publication still protects data
  overwrite after consumers finish.
- Consumers must read only after every required expert certificate is
  acquired. They must preserve route order and FP32 accumulation; readiness
  metadata atomics would never justify floating-point atomic reduction.
- Reduction work must not prevent a dispatch or epilogue role from completing
  the very expert it awaits. Any change to the first CTA rendezvous needs a
  new producer/consumer progress proof and explicit cleanup ownership.

Evaluate the smaller local-ready prototype first. If a broader protocol is
later justified, implement it as owned W4A16 transport/epilogue code for both
return modes, and measure the same full public forward. Current NCU replay
counters do not establish the available pre-drain window or justify this added
state by themselves.
