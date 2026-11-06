# MegaMoE NVFP4 descriptor bit 31

2026-10-08. Independent review of FlashInfer b730 and installed CuTe DSL 4.7.1.
The runtime ORs preserve a zero K-size bit for the two native W4A4 MegaMoE AUTO
tiles. This conclusion now includes the actual DSL scale-layout offsets,
rather than relying only on static descriptor field positions.

No GPU allocation, JIT compilation, or kernel launch was performed for this
review. The query ran with `CUDA_VISIBLE_DEVICES=''`, constructed static MLIR
layouts in memory, and retained only local evidence. Generated PTX/SASS from
the separate native export study remains an independent confirmation step.

## The signed shift concern is real in the general helper

`dynamic_mainloop.py:147–152` computes:

```python
idesc = static_base | (n_dim_value << 17)
sfa_top = Int32(sfa_addr) & Int32(0xC0000000)
sfb_top = Int32(sfb_addr) & Int32(0xC0000000)
idesc |= sfa_top >> 1
idesc |= sfb_top >> 26
```

Installed `base_dsl/typing.py:975–989` preserves integer signedness, and
`_mlir_helpers/arith.py:901–904` selects `arith.shrsi` for signed operands.
For an arbitrary input such as `0x80000000`, the first shift would produce
`0xC0000000`. Therefore field positions alone are insufficient; the actual
scale atom addresses must have their upper subword bits clear.

## Actual DSL scale atom offsets

The native candidate tiles are `(256,128,256)` and `(256,256,256)`. The kernel
uses E2M1 operands, E4M3 scale factors, scale-vector16, and a K64 MMA atom.
Both phases share this configuration. The mainloop selects
`sfa_tensor[(None,0,k_inner)]` and `sfb_tensor[(None,0,k_inner)]` for
`k_inner=0,1,2,3` (`dynamic_mainloop.py:280–295`).

The CPU query calls the same installed `make_blockscaled_trivial_tiled_mma`,
`make_smem_layout_sfa/sfb`, and `make_tmem_layout_sfa/sfb` used by the kernel,
then evaluates the origin offset of each selected atom. It does not substitute
a hand-written layout. SMEM stage counts 1, 2, and 4 give identical results
after the native stage-zero slice.

| Staging tile | Scale tensor | Atom offsets, E4M3 elements | TMEM word offsets | Subword IDs |
|---|---|---|---|---|
| 256/128/256 | SFA | 0,16,32,48 | 0,4,8,12 | 0,0,0,0 |
| 256/128/256 | SFB | 0,16,32,48 | 0,4,8,12 | 0,0,0,0 |
| 256/256/256 | SFA | 0,16,32,48 | 0,4,8,12 | 0,0,0,0 |
| 256/256/256 | SFB | 0,32,64,96 | 0,8,16,24 | 0,0,0,0 |

All atom offsets are divisible by four. The largest within-atom strides in the
full printed layouts are not the atom-origin offsets consumed by the MMA;
the `None` coordinate leaves those internal elements in the fragment while its
iterator points to the selected atom's origin.

Evidence:

- `evidence/glm5-mma-instruction-audit/query_tmem_layout_cpu.py`
- `evidence/glm5-mma-instruction-audit/static-tmem-layout-query.json`

The receipt includes the installed DSL version, exact layouts and offsets,
and hashes of relevant installed Python, pinned CUTLASS headers, and scheduler
source. The helper requires GPUs to be hidden before importing the DSL. Ruff
and Python syntax checks pass.

## Why these offsets cannot sign-extend into bit 31

The kernel obtains its base TMEM pointer as FP32, adds accumulator/SFA column
counts in that full-word type, and only then recasts the SFA/SFB pointers to
E4M3 (`kernel_fc12.py:2158–2186`). This produces full-word-aligned scale bases.
The special N64 SFB offset branch is not selected by either native AUTO tile.
Both FC phases reuse these bases; K stages refill them without introducing a
new subword base offset.

The pinned CUTLASS submodule is `b46b16d003484063bca4ed365e44095c4c6ed633`.
Its [TMEM pointer definition](https://github.com/NVIDIA/cutlass/blob/b46b16d003484063bca4ed365e44095c4c6ed633/include/cute/pointer.hpp#L273)
documents word addressing and physical address mask `0x007F01FF`.
For an 8-bit pointer, element offsets rotate right by two, placing the offset's
low two bits in address bits 30–31 (`:283–311`); pointer recasting preserves
the raw address (`:351–357`). The queried atom-origin offsets have low two
bits zero, so they advance whole TMEM columns and introduce no subword-ID bits.
The valid physical base and resulting column addresses also have those upper
bits clear. Thus `sfa_top = sfb_top = 0`, and both signed shifts operate on zero.

This agrees with the [PTX scale-factor layout contract, §9.7.18.10.7.2.3](https://docs.nvidia.com/cuda/parallel-thread-execution/):
K64/block16 consumes four scale bytes per row, with scale data ID zero. The
argument above establishes the actual atom alignment instead of assuming that
contract alone proves a particular pointer value.

The source comment that each K iteration advances the SF-ID high bits is not
an accurate description of these particular layouts: their atom origins
advance whole columns while the IDs remain zero.

## Runtime N field and final descriptor

`fc1_fc2_fuse_sched.py:1212–1217` clamps the valid token count between zero and
the CTA token tile size. With these swap-AB candidates that size is at most
256. Consequently `align16(valid_tokens) >> 3` is between 0 and 32; shifting
it left by 17 reaches at most bit 22 and cannot set bit 31.

Both candidates use M256, giving static descriptor `0x10000480`, including
K-size bit 31 equal to zero. With zero SF-ID terms, the full descriptor is:

```text
0x10000480 | (n_dim << 17),  0 <= n_dim <= 32
```

Its maximum value is `0x10400480`, always below `0x80000000`. The runtime
descriptor therefore retains K64 for valid native layouts in both FC phases.
This covers both AUTO staging tiles, not an arbitrary caller of the general
`compute_idesc` helper or a future scale-vector/layout change.
