# Distributed TMA source and pipeline audit

CPU-only review, 2026-10-25. **No material source issue found; one warp0 joint empty-ring drainer is safe under the preserved producer schedule.** Independent peer review reached the same conclusion. No CUDA module imports, GPU launches, production edits, or prior-result changes were performed.

## Frozen source

- Base HEAD: `98fd3566b5f945c100f48cddacf25deb2432cbc2`.
- Control core SHA256: `2ca679d3a87e412218e4d75e9e98f892dd3b2ccd1b3d777621d16ae8d03fa58e`.
- Candidate core SHA256: `e2c7089c2fe266a7ec12bd303e7b5602c9e0bfb97bd5d9af9a5724c7a69dcbf6`.
- Control and candidate copied `custom_pipeline.py` are byte-identical: `13dcd385670bb2a14b7134ea12ce5d7a1862be413947068da6ff06dc8e824662`.
- The only tracked candidate change is the core. Both core files parse as Python AST; staged paths are empty. This does not establish CuTe compilation.
- [receipt.json](receipt.json) records the manifest, hashes, exact read-only managed-Hai command, installed method excerpts with individual hashes, and review boundaries.

## Arrival and byte accounting

[Candidate core](../../../flashinfer-producer-distributed-tma-review/flashinfer/fused_moe/cute_dsl/blackwell/blockscaled_contiguous_grouped_gemm_finalize_fusion.py) lines918–919 initializes three TMA full-barrier arrivals. Lines1076–1098 admit exactly warps0/1/2, wait on the same empty phase, then announce each issuer's own bytes before its own copy. A/SFA/B issue work is assigned to warp0/1/2 respectively. The whole issuing warp stays active; the public arrival method and TMA lowering elect internally.

For native NVFP4 K512 with one channel tile, the per-stage byte counts are A32768 + SFA4096 + B8192 =45056, matching the existing aggregate. SFB4096 belongs to the separate unchanged cp.async SF pipeline. No ordinary TMA `producer_acquire` is called in addition to the explicit arrival.

An early issuer can finish while another has not yet announced, but the full barrier still has pending arrivals. Each issuer atomically arrives and adds its own expected bytes before its own transfer can complete. Completion therefore requires all three arrivals and all three announced transfers. The code does not have each issuer expect the aggregate byte count.

## Why one joint tail drainer is sufficient

All128 SF producers keep their commit and state advance at1216–1222 and cloned SF tail at1267–1268. Warp0 alone clones the next producer state, waits, and advances through exactly `num_stages` empty slots at1269–1276. Those states cover the latest use of every ring slot, including partially filled or unused rings, without arming unused full phases.

The MMA role waits the joint full barrier at1465 and releases the single operand empty barrier after MMA at1544. A release cannot precede the three arrivals and operand transfer completions required by that full wait. Other producer warps cannot invalidate storage or exit the CTA early: the unchanged whole-CTA named barrier at1560–1562 joins all roles before TMEM cleanup. Three redundant per-issuer drains are unnecessary.

This proof relies on the preserved identical producer iteration count, stage order, initial phase, and one state advance per K tile. It would need revisiting if an issuer skipped work or used an independent ring.

## Installed public API evidence

Read directly from `fi-w4a4-narrow-1025`, C1, using `/usr/local/bin/h ssh` and the existing `env_candidate.sh`. The installed package metadata reports **nvidia-cutlass-dsl4.7.1**. No CuTe or CUDA package was imported.

Installed base: `/workspace/flashinfer-w4a4-split-dynamic-n/.venv/lib/python3.12/site-packages/nvidia_cutlass_dsl/dsl_packages/cutlass/pipeline/`.

| File | SHA256 | Relevant lines |
|---|---|---|
| `helpers.py` | `87baa220853a4f64179300293f747f75a9f10008f5df3c91bdbc4f5c7d74243c` |254–287 derives arrival count from group size;328–352 initializes it;456–468 explicit arrive+expect;511–529 wait |
| `sm90.py` | `2d5fae60151278072a92dd21ffc445c16932abdcd69bb070cdcf87f9a179a32a` |337–356 wait-only producer tail |
| `sm100.py` | `4e7c4ce1f19f4d470adcbda7052740af36820a99fa74fcf9d01627fb52ff8def` |343–378 optional per-acquire expected bytes |

The copied project `PipelineTmaUmma.producer_acquire` lacks the installed `expected_tx` keyword. The candidate instead uses its exposed public sync objects, preserving the copied pipeline implementation and consumer release semantics.

Public explicit byte arrival, `helpers.py:456–468`:

```python
    @dsl_user_op
    def arrive_and_expect_tx(
        self,
        index: int,
        tx_count: int,
        *,
        loc: Optional[ir.Location] = None,
        ip: Optional[ir.InsertionPoint] = None,
    ) -> None:
        with cute.arch.elect_one(loc=loc, ip=ip):
            cute.arch.mbarrier_arrive_and_expect_tx(
                self.get_barrier(index, loc=loc, ip=ip), tx_count, loc=loc, ip=ip
            )
```

Installed tail, `sm90.py:337–356`:

```python
    @dsl_user_op
    def producer_tail(
        self,
        state: PipelineState,
        *,
        loc: Optional[ir.Location] = None,
        ip: Optional[ir.InsertionPoint] = None,
    ) -> None:
        """
        Make sure the last used buffer empty signal is visible to producer.
        Producer tail is usually executed by producer before exit, to avoid dangling
        mbarrier arrive signals after kernel exit.

        :param state: The pipeline state that points to next useful buffer
        :type state: PipelineState
        """
        # wait on all stage buffers since there is no guaranteed ordering of empty barrier arrives
        for i in range(self.num_stages):
            self.sync_object_empty.wait(state.index, state.phase, loc=loc, ip=ip)
            state.advance(loc=loc, ip=ip)
```

The complete installed `PipelineTmaUmma.producer_acquire(..., expected_tx=...)`, count initialization, and wait excerpts are preserved in [receipt.json](receipt.json). The explicit candidate tail matches the installed wait-only semantics and avoids dependence on older helper variants that armed full phases through `producer_acquire`.

## Validation boundary

The gate at358–362 includes eligible **FC1 and FC2 N16/N32/N64 across supported formats**, not only native NVFP4 N16. Group2 and mixed-format FC1's inline-epilogue path remain excluded. A native N16 exact/timing screen cannot establish correctness or performance across that whole gate. This review establishes source-level consistency only; CuTe lowering, GPU exactness, sanitizer behavior, and performance require their own receipts.
