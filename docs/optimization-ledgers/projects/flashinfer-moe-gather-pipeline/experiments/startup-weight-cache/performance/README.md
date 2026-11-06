# Startup weight cache priority: 56-cell CAAC screen

Prepared from the completed alpha56 machinery: 23 jobs, all 28 supported
non-W4A16 model/topology/dtype arms, tokens 32 and 16384. Each cell uses
control/candidate/candidate/control, 10 warmups and 100 strict CUPTI samples
per phase, cold L2 and CUDA graphs. NVFP4 includes input quantization.
The 12 execution/observer/resource helpers are byte-identical to alpha56;
frozen choices, routes and historical caches remain intact. No TRT timing.

Control is retained c1ac. Candidate is the same immutable source plus only
startup-cache R1 (`585aaeac`), using the qualification owner's snapshots and
current replacement-node release libraries. `screen/perf-config.json` SHA256
is `99227ebcb2ce2e874e54d25d9ede632aefe65a85c359bcfd8fc55a63c4ab5996`.

The launcher binds the six-call/nine-native-pair qualification and actual
count/hint proof, then checks current source guards, identical generated
release build descriptions, unchanged native libraries, Ninja no-op and
GPU UUID/idleness. Full 13,245-file inventories are checked by the campaign
before and after measurement. Root-authorized GPU lanes are 0/1/2/4/5/6/7, excluding the
separate GPU3 NCU diagnostic. One whole CAAC job runs at a time per lane. Source and timer remain unchanged.

The native pilots added three/two static non-NOP instructions in affected
FC2 kernels, with unchanged 76/82 registers and LOCAL0. The lifetime counter
and selector are real overhead; this is an unmeasured policy until the full
primary screen finishes. Preserve every negative cell and clock observation.
No repetition, retention or matrix expansion is authorized by this plan.

Launch PID20711 passed preflight8a0bb07f on seven lanes. Finalization uses
`close.py`, `fetch.py startup-weight-cache-screen`, then the unchanged
`harness/report_evidence.py` on the sealed data leaf.
