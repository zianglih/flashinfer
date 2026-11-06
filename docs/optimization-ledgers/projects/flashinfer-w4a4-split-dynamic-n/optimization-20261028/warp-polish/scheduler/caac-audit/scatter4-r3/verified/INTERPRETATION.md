# Scatter4 r3 independent screen interpretation

The complete source/route/tactic/geometry/raw-sample audit passes, with 64 cells, 48 public processes and 25,600 CUPTI samples. The local frozen archive contains 1,024 hash-verified files.

Primary all-100-sample median GM: overall −0.167%, decode +0.010%, prefill −0.344%. Model GMs: V3 +0.141%, V41F −0.044%, K3 −0.606%, N3U −0.158%. Mode GMs: W4A4 −0.098%, per-token +0.237%, MXFP4x8 −0.208%, MXFP8 −0.597%. This screen does not justify retaining r3.

Prefill sample-order diagnostics (not substitute retention metrics): first25_diagnostic +0.269%, last25_diagnostic +0.114%, last50_diagnostic +0.191%.

All prefill native winners use bulk64; decode uses bulk0. Source correctness and memory/stack spill checks do not imply absence of uniform-register spills; the separate epilogue codegen report describes r3's uniform-register-to-GPR spill and unrolling cost. The root-authorized bounded r4 experiment is separate; this archive remains immutable.
