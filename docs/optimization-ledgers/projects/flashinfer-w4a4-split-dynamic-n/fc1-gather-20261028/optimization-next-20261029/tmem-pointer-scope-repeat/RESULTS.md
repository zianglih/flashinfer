# Pointer scope: rejected

The single predeclared repeat reproduces the N3U EP8 MXFP8 T16384 loss: **−5.307%**, after the original **−6.523%**. In both runs, both candidate phases are slower than both controls. The unchanged V3 EP8 W4A16 T8 control is +0.153% in the repeat. The original 20 affected cells remain −0.172% overall, −0.045% decode, and −0.299% prefill; the repeat is separate and does not replace any row.

|Model / mode|Tokens|Format|C1 µs|A1 µs|A2 µs|C2 µs|Speedup|C spread|A spread|
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
|N3U EP8|16384|MXFP8|787.908|871.605|849.572|842.709|-5.307%|6.955%|2.593%|
|V3 EP8|8|W4A16|68.160|68.064|68.224|68.337|+0.153%|0.259%|0.235%|

The original control/A spreads were 6.137%/0.075%; repeat spreads are 6.955%/2.593%. Quartile drift and occasional clock/power-event changes remain visible; these are not evidence that the repeated regression is external. No normalization, sample removal, additional repeat, shape gate, or source composition is used.

All 800 repeat CUPTI samples, 16 loaded driver guards, 514 source hashes, frozen routes/tactics and same-physical-GPU CAAC identities passed `raw-audit.json`. All loaded kernels have zero local bytes. Normal cached binary images were unobserved, explicitly; no runtime binary-equality claim is made. Numerical qualification remains 40 original exact cases plus one occupancy-qualified full-case rerun, not a single unbroken41 run. The original failed static REG guard is preserved.

Decision: reject the three-line scope relocation. Allocation/waits were unchanged and source semantics were sound, but this minimal cleanup does not justify the repeated measured loss. Preserve all helper, source, codegen, test and timing evidence; retire only the inactive review clone.
