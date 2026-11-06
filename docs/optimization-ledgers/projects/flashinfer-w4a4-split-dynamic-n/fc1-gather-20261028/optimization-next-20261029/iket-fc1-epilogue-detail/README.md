# Bounded FC1 epilogue detail diagnostic

This extends the source-bound d9 N3U EP8 16K NativeDump trace with one range around existing nongated TMEM accumulator loads plus both ownership transposes. All non-marker AST nodes must remain identical. The frozen two-CTA winner is required because the diagnostic samples physical CTAs0–3. The same existing `epi_body` range encloses it; remaining time includes activation, quantization and stores, as well as marker overhead and loop/control work. Do not infer exact asynchronous completion or sum concurrent ranges.

Use the same no-cache instrumented compiler capture, explicitly created compiler-dumps directory, and actual CUBIN zeroLOCAL/LDL/STL prelaunch guards in both tracker and profiler. No timing result, source optimization or retention claim is produced here. Source9037 and d9 share the same swap kernel; retain the exact measured d9 source binding. Preserve all raw diagnostics and the prior unmodified range trace separately.

Prepared locally; no GPU launch yet. GPU ownership belongs to external_gap_audit until reassigned.
