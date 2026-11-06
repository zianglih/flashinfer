# Peer TMA profiler evidence

All six arms complete: **True**.

Prepared/replayed requester measurements. Counts below are requests; payload columns are bytes.

| Arm | NCU passes | Requested B | Total | Lookup hit | Lookup miss | Total−hit−miss | RX payload B | TX payload B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| first_passes1 | 4 | 65536 | 0 | 0 | 0 | 0 | 65536 | 0 |
| first_passes64 | 4 | 4194304 | 0 | 0 | 0 | 0 | 4194304 | 0 |
| normal_passes1 | 4 | 65536 | 0 | 0 | 0 | 0 | 65536 | 0 |
| normal_passes64 | 4 | 4194304 | 0 | 0 | 0 | 0 | 4194304 | 0 |
| last_passes1 | 4 | 65536 | 0 | 0 | 0 | 0 | 65536 | 0 |
| last_passes64 | 4 | 4194304 | 0 | 0 | 0 | 0 | 4194304 | 0 |

## Policy request counters

| Arm | Observed policy | Total | Lookup hit | Lookup miss | Total−hit−miss |
|---|---|---:|---:|---:|---:|
| first_passes1 | first | 0 | 0 | 0 | 0 |
| first_passes1 | normal | 0 | 0 | 0 | 0 |
| first_passes1 | last | 0 | 0 | 0 | 0 |
| first_passes64 | first | 0 | 0 | 0 | 0 |
| first_passes64 | normal | 0 | 0 | 0 | 0 |
| first_passes64 | last | 0 | 0 | 0 | 0 |
| normal_passes1 | first | 0 | 0 | 0 | 0 |
| normal_passes1 | normal | 0 | 0 | 0 | 0 |
| normal_passes1 | last | 0 | 0 | 0 | 0 |
| normal_passes64 | first | 0 | 0 | 0 | 0 |
| normal_passes64 | normal | 0 | 0 | 0 | 0 |
| normal_passes64 | last | 0 | 0 | 0 | 0 |
| last_passes1 | first | 0 | 0 | 0 | 0 |
| last_passes1 | normal | 0 | 0 | 0 | 0 |
| last_passes1 | last | 0 | 0 | 0 | 0 |
| last_passes64 | first | 0 | 0 | 0 | 0 |
| last_passes64 | normal | 0 | 0 | 0 | 0 |
| last_passes64 | last | 0 | 0 | 0 | 0 |

## One-to-64-pass comparison

| Policy | Demand growth | RX payload growth | RX growth / demand growth | Incremental RX / added requested B |
|---|---:|---:|---:|---:|
| first | 64 | 64 | 1 | 1 |
| normal | 64 | 64 | 1 | 1 |
| last | 64 | 64 | 1 | 1 |

## Arithmetic and replay diagnostics

- first_passes1: aggregate total − three policy totals = 0; status = complete.
- first_passes1: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/first_passes1/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "47883", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "47883  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "435", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/first_passes1/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`
- first_passes64: aggregate total − three policy totals = 0; status = complete.
- first_passes64: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/first_passes64/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "49157", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "49157  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "25131", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/first_passes64/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`
- normal_passes1: aggregate total − three policy totals = 0; status = complete.
- normal_passes1: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/normal_passes1/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "49881", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "49881  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "435", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/normal_passes1/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`
- normal_passes64: aggregate total − three policy totals = 0; status = complete.
- normal_passes64: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/normal_passes64/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "50652", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "50652  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "25131", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/normal_passes64/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`
- last_passes1: aggregate total − three policy totals = 0; status = complete.
- last_passes1: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/last_passes1/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "51393", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "51393  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "435", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/last_passes1/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`
- last_passes64: aggregate total − three policy totals = 0; status = complete.
- last_passes64: replay evidence `/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/last_passes64/ncu_%p.csv:31`: `{"ID": "0", "Process ID": "52136", "Process Name": "python3.12", "Host Name": "127.0.0.1", "thread Domain:Push/Pop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "52136  \"<default domain>:peer_tma_measure:none:none:none:none:none:none\"  \"NCCL:ncclCommInitRankConfig:none:none:none:none:REGISTERED:ncclCommInitRankConfig\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\"  \"NCCL:ncclCommInitRank:none:none:none:none:REGISTERED:ncclCommInitRank\" ", "Id:Domain:Start/Stop_Range:PL_Type:PL_Value:CLR_Type:Color:Msg_Type:Msg": "", "Kernel Name": "kernel_cutlass_peer_tma_kernel___main__mainlocalsPeerTmaProbe_object_at___tensorptri64gmemalign16o11___0", "Context": "1", "Stream": "7", "Block Size": "(32, 1, 1)", "Grid Size": "(1, 1, 1)", "Device": "0", "CC": "10.3", "inst_executed": "25131", "Metric Name": "profiler__replayer_passes", "Metric Unit": "pass", "Metric Value": "4", "csv_file": "/Users/ziangli/playground/projects/blackwell-sysl2-megamoe-audit/results/peer_profiles-v4/last_passes64/ncu_%p.csv", "csv_line": 31, "csv_format": "wide"}`

## Interpretation limits

- SysL2 values count requests, not 32-byte sectors or payload bytes.
- total - hit - miss is an unconstrained counter residual, not a proven bypass count or PTE VOL measurement.
- A policy bucket indicates request-policy attribution, not allocation, retention, or owner-side cache behavior.
- Compare requester RX payload growth with logical demand growth; requester counters do not distinguish owner VidL2 from HBM.
- Prepared/replayed measurements are not cold-cache results. CUDA-event timings under NCU are not native performance evidence.
- Unknown replay-pass counts remain null. Source progress lines are retained; request counts never substitute for replay-pass counts.
- probe.jsonl retains the last application invocation; launcher_probe_records retains JSONL emitted to launcher stdout across invocations.
- Unit normalization uses decimal SI for K/M/G/T and binary factors only for explicit Ki/Mi/Gi/Ti units; raw values and units are always retained.
- Application replay recreates allocation, initialization and preparation on each invocation. Counter arithmetic across passes depends on counter definitions and workload reproducibility; do not assume requester warming accumulates across invocations.

Use `--format json` to retain every original metric/probe row, original units, manifest, and replay evidence line.
