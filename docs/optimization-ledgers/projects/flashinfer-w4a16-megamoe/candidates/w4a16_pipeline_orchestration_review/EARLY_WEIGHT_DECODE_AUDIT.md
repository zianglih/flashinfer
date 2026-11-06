# Early weight/decode overlap

Source review at retained `c8155c6f23cc8374912019810fff8fa10ed3b056` (2026-09-11). No source mutation, capture, or performance claim. Paths below are relative to the project checkout `../../flashinfer/`; line numbers describe the reviewed files.

## Overlap already present

- Shared `flashinfer/moe_ep/kernel_src/cutedsl_megamoe/src/src/token_comm.py:719–804,1570–1623` completes the expert-count exchange, then arrives at scheduler barrier 9 **before** starting activation payload pulls. The scheduler needs this metadata to map expert ranges, padding and empty experts; it does not wait for payload completion. The atomic scheduler preclaims its initial linear tile before this handshake.
- Owned `flashinfer/moe_ep/cute_dsl/megamoe/nvfp4_w4a16/megamoe_kernel.py:1139–1228` publishes work to independent role consumers. Warp 5 loads packed weights/scales without an activation wait. Only activation-loader warp 6 waits for FC1 input readiness, or for FC1 completion before loading FC2 activations. Both decode WGs (`:1231–1299`) also have no activation-readiness wait. Therefore FC1 weights/decode already overlap remote pulls, and FC2 weights/decode can run while their activation loader waits for FC1 output.
- Owned `custom_ext.py:223–299` makes nonblocking readiness peeks and annotates work; it does not gate publication. The FC1 peek is live: kernel `:1017` passes `token_comm.fc1_ready_counter_ptr`, shared transport `:545` returns the actual pointer, and kernel `:596` binds `l1_arrival_count`.
- Owned `fc1_fc2_fuse_sched.py:250–255,769–1015` orders each expert group as FC1 then FC2 work. Claim order is not a global FC1-completion barrier. Universal `src/moe_nvfp4_swapab/moe_persistent_scheduler.py:146–196` copies each scheduler record into registers and releases its shared slot immediately; it does not retain that slot until tile computation finishes.

## What bounds further runahead

- `_MegaMixedInput` in owned kernel `:53–107` reserves 512 TMEM columns: ACC2 consumes `2*N`, and each decoded K256 stage consumes 128. N64 has D3; N128 D2. Production fitting (`:394–421`) supplies N64 raw5/B3 and N128 raw4/B3. Scheduler depth alone cannot add weight storage.
- The inherited split decoder, `flashinfer/fused_moe/cute_dsl/blackwell/moe_w4a16_kernel.py:310–435,457–565`, partitions each K tile across two decode WGs. It waits for raw input and acquires its decoded TMEM slot before loading scales/packed fragments. Raw release follows the last register-fed store issue; decoded publication follows the TMEM store fence. Physical index/phase survive work transitions.
- MMA (owned kernel `:1301–1352`) first acquires an accumulator, then consumes decoded and activation stages in K order. If activation or accumulator consumption stops, at most D complete decoded tiles plus the raw ring's packed/SF stages can remain ahead. The weight and decode streams cannot skip the remaining K tiles to start an arbitrary later work record.
- At M256/C2 a CTA's decoded 128×256 BF16 K tile is 64 KiB. H7168 FC1 has 28 K256 tiles (1.75 MiB/CTA if all retained), whereas the decoded ring holds only two or three. This is the real storage/ownership bound, not an absent early-decode path.

## Established patterns and prior trials

Split W4A16 `moe_w4a16_kernel.py:1380–1461,1463–1554,1559–1645` likewise waits for prior-stage readiness only in its activation TMA role and permits weights/decode to start earlier. Shared W4A4 `src/moe_nvfp4_swapab/megamoe_kernel.py:1520–1535` wires the same readiness hooks. MXFP8 `src/moe_mxfp8_glu/kernel_mxfp8_glu_fc12.py:1585–1605,1656,1847` uses the same metadata/publish handshake and activation-side wait, with a separate weight loader.

This is not a new first-fragment/late-acquire proposal. `candidates/w4a16_transform_acquire_audit/README.md` records the prior split ledger: full decode before acquire (5486–5510), next-32-fragment lookahead (5511–5533), immediate-fragment TMEM stores (5535–5570), and full packed preload (1264–1286) did not improve the relevant full sweep. The current effort ledger's first16 investigations (1500–1750), ACC1/N128 Entry059 and K128 Entry063 are also closed evidence, not new designs. `candidates/w4a16_cuda130/DECODE_RESOURCE_AUDIT.md:43` cautions that a full logical RMEM tensor does not prove all values are live: native code can interleave conversion and stores.

The older `candidates/w4a16_direct_epi_profiles/PC_WAIT_ATTRIBUTION_T1024.md` attributes most sampled work-record waits to startup after the metadata handshake, not steady-state mapping or decoded-ready starvation. Its instrumented source/rank-skew does not establish current end-to-end benefit or absence of stalls.

## Alternating whole-K ownership

Assigning even/odd K tiles to separate full-tile decode WGs is structurally different, but adds no decoded capacity and does not remove the activation/ACC limit. One full tile per WG doubles logical BF16 payload per thread (128 to 256 BF16 values, 64 to 128 register words), so bounded fragment streaming is essential under the 96-register decoder allocation; compiler liveness must be measured, not assumed from tensor declarations.

This requires a new raw-consumer/decoded-producer protocol: eight to four raw-consumer warps and 256 to 128 producer threads per CTA per tile, with unchanged multicast factors; stride-two physical indices/phases; global K-stream ownership across odd-K and FC1/FC2 boundaries; and correct tails when a WG owns no tile. Both WGs must still consume scheduler records to retain the existing 480-thread scheduler contract. D3/raw5 wraps do not assign each physical slot permanently to one WG. MMA must retain original K order even if later tiles finish first.

Aggregate decode arithmetic and traffic stay the same. Independent scheduling or fewer per-tile participants might help, but first-tile latency can rise, and both WGs still block once the same ring fills. There is no current profile identifying this as the dominant gap. Do not replace the existing compact split-decoder reuse with a larger owned transform implementation on this evidence alone.

## Concrete next candidate

Exact post-tail FP32 reduction is a smaller independently measurable change: preserve per-route BF16 return and its shared cross-rank drain, then use one all-640-thread local handoff and an owned warpgroup-striped reduction worker. Preserve the standalone reducer's ordered top-k packed-FP32 multiply/FMA and single final BF16 cast. The existing compile-time `in_kernel_fc2_reduce` selector can choose this owned meaning while shared transport and epilogue reduction flags remain False. No catalog expansion is needed for feasibility.

Old NSYS Entry033 measured the separate reducer at 2.492 us (global32) / 9.794 us (global4096), on historical source; these are only a motivation/ceiling reference, not current removable latency. Fusion retains all combine reads, score reads and output writes. See preserved `TAIL_REDUCTION_DESIGN.md`; the executable candidate will document dynamic output/cache and raw-launch contracts separately.
