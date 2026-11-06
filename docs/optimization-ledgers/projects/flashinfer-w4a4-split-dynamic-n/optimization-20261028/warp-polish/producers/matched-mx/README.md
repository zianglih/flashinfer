# Matched MX retention diagnostic

Completed6400 CUPTI samples on GPUs0/1/4/5: V3 and K3 used ABBA, V41F and N3U
BAAB; A is clean99f4, B is frozen polish-combined. Each phase ran tokens64/16384
and both MX formats with the public observer, ten warmups,100 cold-L2 samples,
unfused swap-AB, frozen native winners and identical routing. No autotuning or
external TRTLLM/legacy baseline was run. Existing native compilation caches
were reused. All source/cache/routing/timer checks passed.

The normal100-sample medians are preserved in
`evidence/diagnostic/summary.md`: all eight decode cells improve0.19–0.48%; the
16-cell geometric mean is−0.57%. Several prefill medians move substantially.
They are not uniformly causal patch effects: V3 MXFP4x8 initially appeared
−3.51% with stable phase medians, but raw sequence strata show almost matching
low/high latency groups. The phase medians straddle the transition between
those groups. The earlier interpretation of that cell as a clear regression
is withdrawn. See `temporal-diagnostics.json` and the follow-up
`../v3-mx-isolate/` evidence.

One-second GPU telemetry undersamples the short measurement bursts. It cannot
prove equal in-measurement clocks or establish the cause of the transition.
No clock or benchmark policy was changed. This diagnostic is separate from
public benchmark tables and does not replace their standard median metric.

Archive SHA:
`3edb8da2b9d03196d8d1efbb293374239eba441acc5f2364f706f9dc56592183`.
All190 archived file hashes were verified locally. GPUs0/1/4/5 were idle when
the job completed; only GPU0 was subsequently assigned the isolate follow-up.
