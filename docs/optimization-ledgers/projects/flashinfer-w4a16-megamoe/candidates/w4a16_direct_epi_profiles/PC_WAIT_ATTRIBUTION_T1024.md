# Actual T1024 PC wait attribution

The capture does **not** provide evidence to prioritize the held FC1 `(1,4)` completion-batch trial. All eight ranks have zero samples at the actual FC2 `fc1_done` counter loads/poll loop, and zero at the MMA accumulator-empty and decoded-operand-full slow paths. MMA activation-full slow-path samples are small and are not phase-specific. This does not prove that batching never delays readiness; it means this profile does not identify such a delay.

This is a read-only attribution of the completed T1024/EP8, M256/N64/C2/K256/S2/F4, direct-epilogue capture, source `eb036705ebe71f940bf567c94fdcb78020a5fdc21bdeb3e7ea361cc1d140a09d`. It uses actual report SASS, not addresses borrowed from the earlier T4096 fixture. No kernel execution, profiling, imports of runtime code, or primary-source changes were performed.

## Actual FC2 and MMA ownership

All offsets below are relative to function start `0x905c457180`, which is identical in these eight exported reports. Their 5,504 `(offset, instruction)` rows are also identical; samples remain separate by rank.

- **FC2 readiness counter, warp6:** the peek-ready branch at `0x5610` bypasses the load when ready was already observed. `0x5620` loads `fc1_done` base from `c[0][0x700]`; `0x5630–5670` builds the address from cumulative token-block count plus tile-N. `0x5680 LDG.E.STRONG.GPU`, `0x5690 CCTL.IVALL`, and `0x56a0` test threshold 32; slow loop `0x56c0 NANOSLEEP 0x1f4 → 56d0 LDG → 56e0 CCTL → 56f0 compare → 5700 retry` is the real completion wait. There are **zero samples throughout `5680–5700` on every rank**. The lone rank7 source-tagged readiness sample is `5620 LDC`, pointer setup, not a polling load or blocked wait. This corresponds to `megamoe_kernel.py:1228–1235`.
- **MMA accumulator-empty, leader warp4:** `8610` builds `UR11 = UR31 + 8*UR38`; `8640` waits at `[UR11+0xc0]`; `8650` branches to cold stub `144c0–14510`, with sleep at `144e0`. The stub's line 1358 tag is misleading: the caller and `+0xc0` establish accumulator-empty ownership, matching source line 1355.
- **MMA decoded-weights-full:** `86f0` builds `UR16 = UR31 + 8*UR13`; `8710` waits at `[UR16+0x50]`; `8720` branches to `14520–14570`, sleep `14540`, returning to `8730`. Source line 1358 calls the transform consumer wait.
- **MMA activation-full:** `8730` builds `UR15 = UR31 + 8*UR37`; `8750` waits at `[UR15+0x80]`; `8760` branches to `14580–145d0`, sleep `145a0`, returning to MMA setup at `8770`. Source line 1359 calls the activation consumer wait. Both FC1 and FC2 use this path, so its samples cannot be assigned to FC2 or to completion batching without further evidence.

Counts use `smsp__pcsamp_sample_count`. The cold-stub ranges include their setup/return instructions; the FC2 range includes the initial counter load and the complete slow loop. Sampling is not an exhaustive execution trace.

| Rank | Total samples | Initial work-record cold paths | Repeated work-record cold paths | FC2 counter load/poll | MMA activation-full cold path |
|---:|---:|---:|---:|---:|---:|
| 0 | 232,627 | 164,835 | 95 | 0 | 0 |
| 1 | 718,995 | 529,194 | 159 | 0 | 40 |
| 2 | 2,903,790 | 2,167,917 | 175 | 0 | 64 |
| 3 | 13,591 | 521 | 107 | 0 | 0 |
| 4 | 622,709 | 457,229 | 139 | 0 | 37 |
| 5 | 3,168,470 | 2,366,676 | 112 | 0 | 21 |
| 6 | 875,289 | 646,773 | 136 | 0 | 34 |
| 7 | 107,026 | 70,488 | 166 | 0 | 74 |

MMA accumulator-empty `144c0–14510` and decoded-full `14520–14570` are zero for every row. Consequently, a source-line ranking that groups their wait setup together with actual stalled instructions overstates evidence for those dependencies.

## Dominant waits are initial work-record publication

The five dominant cold paths wait for scheduler record **full** at shared base `+0xd0`; the record itself is loaded from `+0xf0` with a 32-byte stage stride. They are initial consumes before each role's tile loop, distinct from separately lowered repeated consumes. Source `moe_persistent_scheduler.py:184–190` waits, copies the record, then performs the CTA fence and consumer release. Its `from_rmem` line 187 is an outlined-wait location artifact, not a record-deserialization cost.

| Role | Initial caller/wait | Cold range; sampled sleep | Repeated cold range |
|---|---|---|---|
| Weight TMA, warp5 | `4370`, branch `4380` | `13b00–13b50`; `13b20` | `13c20–13c70` |
| Activation TMA, warp6 | `4f40`, branch `4f50` | `13e60–13eb0`; `13e80` | `13f80–13fd0` |
| Two decode WGs, warps12–19 | `5d40`, branch `5e70` | `14100–14150`; `14120` | `142e0–14330` |
| MMA, warp4 | `83c0`, branch `83e0` | `14460–144b0`; `14480` | `145e0–14630` |
| Epilogue, warps0–3 | `8f00`, branch `8f20` | `14690–146e0`; `146b0` | `14810–14850` |

The initial groups account for 65.86–74.69% of samples on ranks0/1/2/4/5/6/7, but only 3.83% on rank3. Their relative magnitude also follows the participating warp counts (8 decode, 4 epilogue, 1 each weight/activation/MMA). The repeated groups have only 95–175 samples per rank. This evidence points to startup availability of the first record, not sustained starvation of the steady-state record queue.

The scheduler's first publication follows `sched_warp_pre_init_wait` (`megamoe_kernel.py:1152`). That is NB9, released by dispatch after metadata exchange and before payload pull (`token_comm.py:1612–1622`). Thus initial consumer waits can accumulate while dispatch/control is still crossing startup synchronization; they cannot by themselves establish that the scheduler's tile-mapping or steady atomic claim is expensive.

## Dispatch and tail boundaries

| Rank | Scheduler NB9 and landing `f60–f80` | Dispatch grid-sync polling `d0e0–d120` | Dispatch NB10 and landing `d210–d240` | Final BAR8 and landing `11e80–11ea0` |
|---:|---:|---:|---:|---:|
| 0 | 11,033 | 9,003 | 32,634 | 1,842 |
| 1 | 35,368 | 28,999 | 105,262 | 2,303 |
| 2 | 144,576 | 119,176 | 430,791 | 2,609 |
| 3 | 57 | 0 | 0 | 1,806 |
| 4 | 30,530 | 25,011 | 90,844 | 2,239 |
| 5 | 157,795 | 129,794 | 470,100 | 2,119 |
| 6 | 43,181 | 35,522 | 128,580 | 2,181 |
| 7 | 4,737 | 3,924 | 14,112 | 2,584 |

`f60` is `BAR.SYNC.DEFER_BLOCKING 9,160`; the dominant sample is the following branch at `f80`. `d210` is the 128-thread dispatch BAR10, followed by address setup and the heavily sampled `d240 BSSY`. This is a **post-barrier landing region**, not evidence that BSSY itself is intrinsically expensive. `d0e0` is the grid-sync counter acquire load, with sign/phase test `d100` and backward branch `d110`; it precedes entry to payload pull. These are dispatch startup synchronization sites.

`11e80` is `BAR.SYNC.DEFER_BLOCKING 8,640`; `11ea0 EXIT` is its sampled landing instruction for roles that leave while dispatch performs cleanup. This is a kernel-tail rendezvous, separate from FC2 completion readiness. Other cleanup instructions are intentionally not swept into this small attribution range.

The reports have two aggregated PC-sampling passes, with zero dropped bytes and zero buffer overflow on each rank. Their kernel durations span 0.208–64.95 ms and are replay diagnostics, not an AUTO latency comparison. The large rank asymmetry and concentration at initial synchronization limit performance inference. Keep the held batch1 proposal separate; this capture supplies no causal evidence for delayed batch publication.

## Provenance and reproducibility

Inputs under `profiles/direct-epi-0910a-ncu-full-analysis/`:

- `pc-samples.json`: `9fe63b77db64bd685002385d41b984d38ed2d7158bb2d3191de7298b08c3127f`.
- `rank0-sass/sass.json`: `da2cd10ba0243474f3def66bed3f7b84fef7ae43d74f189367af9036f6d6e878`.
- `rank0-sass/sass.txt`: `317eb4396856856623528ab01bf243d17c5732c93e2dac112a6d3ba3e0ffd030`.
- Existing `ranking/wait-ranking.json`: `a955409adcdd55dc25556fbb1f2d7d6b3ac079ff7819600f181cd408d1746f8a`; source manifest `db4a5571b80679362414c68ed11154dfd316755c22ffc184f07c188b8e3325ad`.
- All eight SASS instruction-list SHA256 values are `abf075c540930c9fb70c2aa55bd5c0d7f1791240ae6d0098160046b29fb61928`, computed as SHA256 of Python `json.dumps([(row["offset"], row["sass"]) for row in rows]).encode()`; this verifies the common offset mapping without pooling rank samples.
- Embedded kernel source SHA256 `5d6d7c6c5a4265b98feef5603ad215909dd60262fae628878dcc89f154786fab`; epilogue `6026bd7a265c4be5e273c4c1af2cbe62dd4eda132ef0944b1f4f70489e69bfde`; generic scheduler `0a6293b8d544eb04d7f21b4f6abcdbc50ac37a0162d73d0fdb056f031cd98402`.

For each table range, subtract the report's `function_start_pcs[0]` from each `pc_rows[].pc`, select the inclusive offset range(s), and sum only `metrics.smsp__pcsamp_sample_count`. The exported report SHA256 and complete embedded source-hash map remain in `pc-samples.json`. No source-line-only assignment is used for the three MMA waits or dominant work-record waits.
