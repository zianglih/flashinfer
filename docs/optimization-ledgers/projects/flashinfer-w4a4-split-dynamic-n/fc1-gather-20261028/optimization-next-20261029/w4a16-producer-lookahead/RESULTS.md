# W4 Gather4 empty-barrier lookahead

Status: rejected by parent after the bounded screen. Added instructions have no robust measured benefit. Local review copy retired after all514 source hashes and exact patch equality were verified; all helper/evidence artifacts preserved. No broad screen or new tactic.

The candidate saves the current stage index/barrier, advances its private producer cursor, and probes the next empty barrier before issuing the current static Gather4 batch. A false token still performs the ordinary blocking acquire. Four arrivals, expected transaction bytes, shared-memory capacity, registers, CLC/static scheduling, PDL, metadata, FC2 and issue traversal remain unchanged. See DESIGN.md for dependency and resource proof and the Rubin/CUTLASS precedents.

Source: logical retained control `6c6515f2f804af420661d95e4595b5663d7f92d1`, verified across514 source files; control W4 kernel `b8f124f187ec169b101c56a72cce2732833b89bf6ef3b72eaa0695f7a04b5da7`. Candidate local review has that Git parent plus an unstaged11+/6− delta; W4 kernel `ee28acbfc19376bf3d4c8fd9775a73a871810d37781f15fa706539050dc966fe`. Remote materialized copies have actual Git HEAD `1b0f1f69acbb7e20055d5aaf76cc29c840779304`; source/patch hashes, rather than Git HEAD alone, bind each measured arm. No commit or push.

Validation:33 existing W4A16 cases passed, zero failures/errors/skips, including route boundaries, partial/padded outputs, weight-scale updates, SiTU and GeGLU. All33 captured kernels have zero local bytes and zero LDL/STL sites;22 use Gather4. Representative N16/N128/N192, two-CTA codegen retains the same launch/register quotas, no added R2UR or SHFL, and unchanged non-gather role instruction counts.

| MMA N | Whole non-NOP C/A | Gather non-NOP C/A | Max gather GPR C/A |
|---:|---:|---:|---:|
|16|1626 /1637|213 /224|11 /13|
|128|1955 /1964|275 /284|13 /11|
|192|1985 /1995|344 /354|13 /13|

The candidate adds9–11 static instructions, including another branch and two static TRYWAIT sites. It needs a performance benefit; it is not an instruction-count improvement.

Method: stock-clock B300 GPU3 (`GPU-828e523f-00a8-c70b-c818-2837a056cc49`), image `nvcr.io/nvidia/pytorch:26.05-py3`, CUDA13.2.1/CuTeDSL4.8.0, strict source-keyed persistent caches. Sequential C-A-A-C, fixed pre-existing native W4 winners, exact frozen routes, functional API, unfused swap-AB, cold-L2 CUDA graphs,10 warmups and100 strict CUPTI samples per cell, no AUTO. Read-only2ms NVML telemetry; no sanitizer or clock modification. All phase source/route/winner/runtime/executable/CUPTI guards passed.

A phase latency is the median of100 CUPTI samples. Each arm latency is the median of its two phase medians (equivalently the arithmetic mean for two values); it is not a geometric mean. Cell gain is control/candidate−1. Repeat spread is max/min−1 within an arm. All raw rows are included below.

| Case | Tokens | C ms | A ms | Gain | C spread | A spread |
|---|---:|---:|---:|---:|---:|---:|
|K3 EP8|4096|0.568707|0.558283|+1.867%|3.027%|0.555%|
|K3 EP8|8192|1.028270|1.022359|+0.578%|0.167%|0.590%|
|V3 TP8|8|0.057135|0.057232|−0.168%|0.055%|0.166%|
|V3 TP8|4096|0.478940|0.479560|−0.129%|0.254%|0.477%|

C-A-A-C phase medians, milliseconds:

```
K3 EP8 4096: 0.577187, 0.556739, 0.559827, 0.560227
K3 EP8 8192: 1.0291255, 1.0193505, 1.0253665, 1.0274145
V3 TP8    8: 0.0571195, 0.057279, 0.057184, 0.057151
V3 TP8 4096: 0.4795485, 0.480701, 0.4784195, 0.478332
```

K3 phase quartiles slow roughly10–16% from the first to last quarter across both sources, so the small aggregate benefit is not established as a source effect. K3 EP4K control repeats differ3.03%. NVML mostly reports2032MHz and reason mask0; one K3 EP8K candidate window includes1620–2032MHz. Its coarse reporting cannot prove frequency causes every timing change, nor rule out utilization-dependent behavior. V3 is near neutral with small negative signs. No clock-normalized speedup is claimed.

Artifacts: `screen.csv`, `summary.json` (all phase medians and25-sample quartiles), `telemetry-summary.json`, `codegen-analysis.json`, source manifests, executable guards, raw100-sample CUPTI activities, exact logs and cubins. Full archive SHA256 `d6f62bd8723a9b8e43151dabc8845addfc7c3137ac4539a87408ae7b039404f0`,7,228,771 bytes. `fetch_chunked.py` verified individual2MiB chunks and the complete archive. GPU3 released after the completed run and idle check.
