# Degenerate CTA rank gate

Source:105474 control, candidate kernel7932107248fa69ae0e843896d5931430d987be2ad4571fd15f77b1505238a5aa. The sole change is compile-time rank0 for a cluster with one CTA; two-CTA expression is unchanged.

All112 cross-source storage-bit exact comparisons pass, covering four blockscaled formats, FC1/FC2, static/CLC, PDLoff/on, live/empty/reactivated routing. All24 two-CTA SASS instruction streams and resources are identical. All32 one-CTA variants remove10–42 non-NOP instructions, with register changes−12..+2; only mixed staticFC1 increases registers by2. Local/stack spills remain zero and uniform spill/fill counts are unchanged. Ten combine pairs are unchanged.

Static one-CTA scheduling removes the activation limit global load used only to offset the second CTA. Source contains no runtime dtype/model/tactic branch. This is not a blanket dynamic-instruction reduction: SDK rank-read sites sometimes increase and branch layout changes. CAAC will decide retention.

597 archived files verified against the raw manifest; evidence-verification.json and evidence/GATE.json bind the source, results and generated PTX/cubin/SASS/resources. Existing immutable R1 controls were reused for the original four geometry cases; supplemental one-CTA cases ran their own source-paired controls. No sanitizer.
