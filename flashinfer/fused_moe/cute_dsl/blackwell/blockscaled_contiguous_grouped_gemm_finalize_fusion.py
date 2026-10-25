# Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""SM100 blockscaled MoE with weights on M and routed activations on runtime N.

FC1 and FC2 share native NVFP4, MXFP4, MXFP8, and mixed MXFP4/MXFP8
mainloops. TMA loads prepared weights and activation rows; cp.async loads
activation scale factors. M128 uses one CTA; M256 uses two CTAs with 128
channels each. Allocation uses the tactic width while each MMA descriptor
rounds the live routed-token count to 16 columns.
"""

from typing import Optional

import cuda.bindings.driver as cuda
import cutlass
import cutlass.cute as cute
import cutlass.pipeline as pipeline
import cutlass.utils as utils
import cutlass.utils.blackwell_helpers as sm100_utils
import cutlass.utils.blockscaled_layout as blockscaled_utils
from cutlass.cute.nvgpu import cpasync, tcgen05
from cutlass._mlir import ir
from cutlass._mlir.dialects import builtin, llvm
from cutlass._mlir.dialects import cute as _cute_ir
from cutlass._mlir.dialects import cute_nvgpu as _cute_nvgpu_ir
from cutlass.cute.typing import AddressSpace
from cutlass.cutlass_dsl import dsl_user_op

from flashinfer.tllm_enums import (
    ActivationType,
    DEFAULT_SWIGLU_ALPHA,
    DEFAULT_SWIGLU_BETA,
    DEFAULT_SWIGLU_LIMIT,
)
from .custom_pipeline import PipelineCpAsyncUmma, PipelineTmaUmma, PipelineUmmaAsync
from .utils import (
    Sm100BlockScaledMoeEpilogue,
    griddepcontrol_launch_dependents,
    griddepcontrol_wait,
)


@dsl_user_op
def _blockscaled_tma_gather4(
    atom, destination, mbarrier, k, r0, r1, r2, r3, cta_group, loc=None, ip=None
):
    """Issue four 128-byte activation rows into the native K-major B layout."""
    executable = _cute_nvgpu_ir.atom_make_exec_tma(atom._trait.value, loc=loc, ip=ip)
    descriptor_type = _cute_ir.PtrType.get(
        _cute_nvgpu_ir.TmaDescriptorTiledType.get(), AddressSpace.generic, 64
    )
    descriptor = _cute_nvgpu_ir.get_tma_desc_addr(
        descriptor_type, executable, loc=loc, ip=ip
    )
    barrier = cutlass.Int32(mbarrier.toint())
    if cta_group == 2:
        # Clear the peer-CTA bit so both CTAs signal the leader's barrier.
        barrier = barrier & cutlass.Int32(-16777217)
    elif cta_group != 1:
        raise ValueError("Unsupported TMA CTA group")
    llvm.inline_asm(
        None,
        [
            cutlass.Int32(destination.toint()).ir_value(loc=loc, ip=ip),
            descriptor.toint().ir_value(loc=loc, ip=ip),
            barrier.ir_value(loc=loc, ip=ip),
            cutlass.Int32(k).ir_value(loc=loc, ip=ip),
            cutlass.Int32(r0).ir_value(loc=loc, ip=ip),
            cutlass.Int32(r1).ir_value(loc=loc, ip=ip),
            cutlass.Int32(r2).ir_value(loc=loc, ip=ip),
            cutlass.Int32(r3).ir_value(loc=loc, ip=ip),
            cutlass.Int64(0).ir_value(loc=loc, ip=ip),
        ],
        "cp.async.bulk.tensor.2d.shared::cta.global.tile::gather4."
        f"mbarrier::complete_tx::bytes.cta_group::{cta_group}.L2::cache_hint "
        "[$0], [$1, {$3, $4, $5, $6, $7}], [$2], $8;",
        "r,l,r,r,r,r,r,r,l",
        has_side_effects=True,
        is_align_stack=False,
        asm_dialect=llvm.AsmDialect.AD_ATT,
        loc=loc,
        ip=ip,
    )


@dsl_user_op
def _blockscaled_dynamic_mma(
    acc,
    a,
    b,
    sfa,
    sfb,
    valid_tokens,
    k_tile,
    instruction,
    descriptor,
    cta_group,
    loc=None,
    ip=None,
):
    """Issue four native blockscaled MMAs with a runtime token-width descriptor."""
    i32 = ir.IntegerType.get_signless(32)
    i64 = ir.IntegerType.get_signless(64)
    n_bits = (((cutlass.Int32(valid_tokens) + 15) & -16) >> 3) << 17
    for inner_k in range(4):
        a_atom = a[(None, 0, inner_k)]
        b_atom = b[(None, 0, inner_k)]
        sfa_atom = sfa[(None, 0, inner_k)]
        sfb_atom = sfb[(None, 0, inner_k)]
        acc_atom = acc[(None, 0, 0)]
        a_value = (
            a_atom.iterator.value
            if hasattr(a_atom.iterator, "value")
            else a_atom.iterator
        )
        a_desc = builtin.unrealized_conversion_cast([i64], [a_value])
        b_value = (
            b_atom.iterator.value
            if hasattr(b_atom.iterator, "value")
            else b_atom.iterator
        )
        b_desc = builtin.unrealized_conversion_cast([i64], [b_value])
        a_sf = builtin.unrealized_conversion_cast([i32], [sfa_atom.iterator.value])
        b_sf = builtin.unrealized_conversion_cast([i32], [sfb_atom.iterator.value])
        dst = builtin.unrealized_conversion_cast([i32], [acc_atom.iterator.value])
        desc = cutlass.Int32(descriptor) | n_bits
        desc = desc | (((cutlass.Int32(a_sf) >> 30) & 3) << 29)
        desc = desc | (((cutlass.Int32(b_sf) >> 30) & 3) << 4)
        accumulate = k_tile != 0 if inner_k == 0 else True
        with cute.arch.elect_one():
            llvm.inline_asm(
                None,
                [
                    dst,
                    a_desc,
                    b_desc,
                    desc.ir_value(),
                    cutlass.Int32(cutlass.Boolean(accumulate)).ir_value(),
                    a_sf,
                    b_sf,
                ],
                "{ .reg .pred p; setp.ne.b32 p, $4, 0; "
                f"tcgen05.mma.cta_group::{cta_group}.kind::{instruction} "
                "[$0], $1, $2, $3, [$5], [$6], p; }",
                "r,l,l,r,r,r,r",
                has_side_effects=True,
                is_align_stack=False,
                asm_dialect=llvm.AsmDialect.AD_ATT,
                loc=loc,
                ip=ip,
            )


@cute.jit
def _blockscaled_sf_offset(
    row, channel, padded_channels, sf_vec_size: cutlass.Constexpr
):
    """Offset in the prepared 128-row, 4-scale blockscaled layout."""
    return (
        (row // 128) * (padded_channels // (4 * sf_vec_size)) * 512
        + (channel // (4 * sf_vec_size)) * 512
        + (row % 32) * 16
        + ((row % 128) // 32) * 4
        + (channel % (4 * sf_vec_size)) // sf_vec_size
    )


class Sm100BlockScaledGroupedGemmKernel:
    """Persistent one/two-CTA grouped GEMM shared by the split MoE phases."""

    def __init__(
        self,
        activation_dtype,
        weight_dtype,
        sf_dtype,
        sf_vec_size,
        mma_tiler_mnk=(128, 128, 256),
        activation_type=None,
        top_k=1,
        swiglu_alpha=DEFAULT_SWIGLU_ALPHA,
        swiglu_beta=DEFAULT_SWIGLU_BETA,
        swiglu_limit=DEFAULT_SWIGLU_LIMIT,
        situ_beta=None,
        situ_linear_beta=None,
        use_per_token_scale=False,
        use_fused_finalize=False,
        enable_pdl=False,
        output_dtype=cutlass.BFloat16,
        final_scale_dtype=cutlass.Float32,
        max_active_clusters=1,
        generate_sfc=False,
    ):
        if not self.is_valid_dtypes(
            activation_dtype, weight_dtype, sf_dtype, sf_vec_size
        ):
            raise ValueError("Unsupported SM100 blockscaled operand/scale types")
        self.activation_dtype = activation_dtype
        self.weight_dtype = weight_dtype
        self.sf_dtype = sf_dtype
        self.sf_vec_size = sf_vec_size
        both_fp4 = (
            activation_dtype is cutlass.Float4E2M1FN
            and weight_dtype is cutlass.Float4E2M1FN
        )
        self.tile_k = 256 if both_fp4 else 128
        self.unpack_weights = weight_dtype.width < activation_dtype.width
        self.a_storage_dtype = cutlass.Int8 if self.unpack_weights else weight_dtype
        self.mma_m = mma_tiler_mnk[0]
        if self.mma_m not in (128, 256) or mma_tiler_mnk[2] != self.tile_k:
            raise ValueError(
                "Blockscaled split MoE requires M128 or M256 and four native MMA K steps"
            )
        if mma_tiler_mnk[1] not in (16, 32, 64, 128, 256):
            raise ValueError("Unsupported routed-token tile")
        if self.mma_m == 256 and mma_tiler_mnk[1] not in (128, 256):
            raise ValueError("Two-CTA blockscaled MoE requires N128 or N256")
        self.cta_group_size = self.mma_m // 128
        self.cta_group = (
            tcgen05.CtaGroup.ONE if self.cta_group_size == 1 else tcgen05.CtaGroup.TWO
        )
        if both_fp4:
            if sf_vec_size == 16:
                self.instruction = "mxf4nvf4.block_scale.block16"
            elif sf_vec_size == 32:
                self.instruction = "mxf4.block_scale.block32"
            else:
                raise ValueError("Unsupported FP4 scale vector size")
            self.descriptor = (self.mma_m << 20) | 0x480
        else:
            formats = {
                cutlass.Float8E4M3FN: 0,
                cutlass.Float8E5M2: 1,
                cutlass.Float4E2M1FN: 5,
            }
            self.instruction = "mxf8f6f4.block_scale.block32"
            self.descriptor = (
                (self.mma_m << 20)
                | (formats[weight_dtype] << 7)
                | (formats[activation_dtype] << 10)
            )
        if sf_dtype is cutlass.Float8E8M0FNU:
            self.descriptor |= 1 << 23
        self.mma_tiler = mma_tiler_mnk
        self.route_tile = mma_tiler_mnk[1]
        # The epilogue transposes 32-column chunks even for a 16-row tile.
        self.allocated_n = max(32, self.route_tile)
        self.physical_tiler = (self.mma_m, self.allocated_n, self.tile_k)
        self.b_rows = self.allocated_n // self.cta_group_size
        self.sf_block_k = 4 * sf_vec_size
        self.sf_stage_bytes = 128 * self.tile_k // sf_vec_size
        # Group-2 S2T reads each CTA's local scales: SFB remains full-N even
        # though each CTA stores only its half of the B activation tile.
        self.sfb_row_blocks = max(1, self.allocated_n // 128)
        self.sfb_stage_bytes = self.sfb_row_blocks * self.sf_stage_bytes
        self.activation_type = activation_type
        self.top_k = top_k
        self.use_per_token_scale = use_per_token_scale
        self.use_fused_finalize = use_fused_finalize
        self.enable_pdl = enable_pdl
        self.output_dtype = output_dtype
        self.max_active_clusters = max_active_clusters
        if max_active_clusters < self.cta_group_size:
            raise ValueError("The launch needs at least one complete CTA group")
        if self.cta_group_size == 2:
            self.num_stages = 5
        elif self.route_tile == 256:
            self.num_stages = 3 if activation_type is not None else 4
        elif self.route_tile == 128:
            self.num_stages = 4
        elif self.route_tile in (16, 32, 64):
            self.num_stages = 5
        else:
            raise ValueError("Unsupported routed-token tile")
        # Dedicated epilogue warps let small tiles load the next tile while
        # storing results. Mixed-format FC1 keeps the smaller warp group.
        self.overlap_epilogue = activation_type is None or (
            not self.unpack_weights
            and (self.route_tile < 128 or self.cta_group_size == 2)
        )
        self.threads_per_cta = 288 if self.overlap_epilogue else 160
        self.acc_cols = self.allocated_n
        self.acc_stages = 2 if self.overlap_epilogue and self.allocated_n <= 128 else 1
        self.sf_cols = 16
        self.sfb_cols = self.sf_cols * self.sfb_row_blocks
        self.tmem_cols = (
            1
            << (
                self.acc_stages * self.acc_cols + self.sf_cols + self.sfb_cols - 1
            ).bit_length()
        )
        self.epilogue = Sm100BlockScaledMoeEpilogue(
            mma_tiler_mnk=(128, mma_tiler_mnk[1], mma_tiler_mnk[2]),
            activation_type=activation_type,
            swiglu_alpha=swiglu_alpha,
            swiglu_beta=swiglu_beta,
            swiglu_limit=swiglu_limit,
            situ_beta=situ_beta,
            situ_linear_beta=situ_linear_beta,
            use_per_token_scale=use_per_token_scale,
            use_fused_finalize=use_fused_finalize,
            top_k=top_k,
            output_dtype=output_dtype,
            final_scale_dtype=final_scale_dtype,
            sf_vec_size=sf_vec_size,
            sf_dtype=sf_dtype,
            generate_sfc=generate_sfc,
        )

    @staticmethod
    def is_valid_dtypes(activation_dtype, weight_dtype, sf_dtype, sf_vec_size):
        supported = (cutlass.Float4E2M1FN, cutlass.Float8E4M3FN, cutlass.Float8E5M2)
        if activation_dtype not in supported or weight_dtype not in supported:
            return False
        if activation_dtype is not weight_dtype:
            return (
                activation_dtype is cutlass.Float8E4M3FN
                and weight_dtype is cutlass.Float4E2M1FN
                and sf_dtype is cutlass.Float8E8M0FNU
                and sf_vec_size == 32
            )
        if sf_vec_size == 16:
            return activation_dtype is cutlass.Float4E2M1FN and sf_dtype in (
                cutlass.Float8E4M3FN,
                cutlass.Float8E8M0FNU,
            )
        if sf_vec_size == 32:
            return sf_dtype is cutlass.Float8E8M0FNU
        return False

    @staticmethod
    def can_implement(
        m,
        n,
        k,
        output_dtype,
        mma_tiler_mn,
        cluster_shape_mn,
        activation_dtype,
        weight_dtype,
        sf_dtype,
        sf_vec_size,
    ):
        """M is output channels; N is allocated routed-token capacity."""
        if not Sm100BlockScaledGroupedGemmKernel.is_valid_dtypes(
            activation_dtype, weight_dtype, sf_dtype, sf_vec_size
        ):
            return False
        if output_dtype not in (
            cutlass.Float4E2M1FN,
            cutlass.Float8E4M3FN,
            cutlass.Float8E5M2,
            cutlass.Float32,
            cutlass.BFloat16,
            cutlass.Float16,
        ):
            return False
        if len(mma_tiler_mn) != 2:
            return False
        tile_m, tile_n = mma_tiler_mn
        if tile_m == 128:
            if cluster_shape_mn != (1, 1) or tile_n not in (16, 32, 64, 128, 256):
                return False
        elif tile_m == 256:
            if cluster_shape_mn != (2, 1) or tile_n not in (128, 256):
                return False
        else:
            return False
        if m <= 0 or n <= 0 or k <= 0:
            return False
        return m % 128 == 0 and k % (4 * sf_vec_size) == 0 and n % tile_n == 0

    @cute.jit
    def wrapper(
        self,
        weight_ptr: cute.Pointer,
        weight_sf_ptr: cute.Pointer,
        activation_ptr: cute.Pointer,
        activation_sf_ptr: cute.Pointer,
        output_ptr: cute.Pointer,
        output_sf_ptr: Optional[cute.Pointer],
        alpha_ptr: cute.Pointer,
        norm_const_ptr: Optional[cute.Pointer],
        token_mapping_ptr: cute.Pointer,
        expert_idx_ptr: cute.Pointer,
        mn_limit_ptr: cute.Pointer,
        num_tiles_ptr: cute.Pointer,
        token_final_scales_ptr: Optional[cute.Pointer],
        per_token_scale_ptr: Optional[cute.Pointer],
        num_channels: cutlass.Int64,
        num_routes: cutlass.Int64,
        reduction_size: cutlass.Int64,
        num_experts: cutlass.Int64,
        num_tokens: cutlass.Int64,
        stream: cuda.CUstream,
    ):
        num_channels = cute.assume(num_channels, divby=128)
        reduction_size = cute.assume(reduction_size, divby=self.sf_block_k)
        gated = self.activation_type is not None and self.activation_type != int(
            ActivationType.Relu2
        )
        out_channels = cute.assume(num_channels // (2 if gated else 1), divby=16)
        source_rows = num_tokens if self.activation_type is not None else num_routes
        output_rows = num_routes
        if cutlass.const_expr(self.activation_type is None):
            output_rows = (
                num_tokens if self.use_fused_finalize else num_tokens * self.top_k
            )
        weights = cute.make_tensor(
            weight_ptr,
            cute.make_layout(
                (num_channels, reduction_size, num_experts),
                stride=(reduction_size, 1, num_channels * reduction_size),
            ),
        )
        activations = cute.make_tensor(
            activation_ptr,
            cute.make_layout((source_rows, reduction_size), stride=(reduction_size, 1)),
        )
        weights_sf = cute.make_tensor(
            weight_sf_ptr,
            cute.make_layout(
                (
                    cute.ceil_div(num_channels, 128)
                    * 128
                    * cute.ceil_div(reduction_size, self.sf_block_k)
                    * 4
                    * num_experts,
                )
            ),
        )
        activations_sf = cute.make_tensor(
            activation_sf_ptr,
            cute.make_layout(
                (
                    cute.ceil_div(source_rows, 128)
                    * 128
                    * cute.ceil_div(reduction_size, self.sf_block_k)
                    * 4,
                )
            ),
        )
        output = cute.make_tensor(
            output_ptr,
            cute.make_layout((output_rows, out_channels), stride=(out_channels, 1)),
        )
        output_sf = None
        if cutlass.const_expr(output_sf_ptr is not None):
            sf_layout = blockscaled_utils.tile_atom_to_shape_SF(
                (cute.ceil_div(num_routes, 128) * 128, out_channels, 1),
                self.sf_vec_size,
            )
            output_sf = cute.make_tensor(output_sf_ptr, sf_layout)[(None, None, 0)]
        alpha = cute.make_tensor(alpha_ptr, cute.make_layout((num_experts,)))
        norm_const = None
        if cutlass.const_expr(norm_const_ptr is not None):
            norm_const = cute.make_tensor(norm_const_ptr, cute.make_layout((1,)))
        token_mapping = cute.make_tensor(
            token_mapping_ptr, cute.make_layout((num_routes,))
        )
        expert_idx = cute.make_tensor(
            expert_idx_ptr, cute.make_layout((num_routes // self.route_tile,))
        )
        mn_limit = cute.make_tensor(mn_limit_ptr, expert_idx.layout)
        num_tiles = cute.make_tensor(num_tiles_ptr, cute.make_layout((1,)))
        token_final_scales = None
        if cutlass.const_expr(token_final_scales_ptr is not None):
            token_final_scales = cute.make_tensor(
                token_final_scales_ptr,
                cute.make_layout((num_tokens, self.top_k), stride=(self.top_k, 1)),
            )
        per_token_scale = None
        if cutlass.const_expr(per_token_scale_ptr is not None):
            per_token_scale = cute.make_tensor(
                per_token_scale_ptr, cute.make_layout((source_rows,))
            )
        self(
            weights,
            activations,
            weights_sf,
            activations_sf,
            output,
            output_sf,
            alpha,
            norm_const,
            token_mapping,
            expert_idx,
            mn_limit,
            num_tiles,
            token_final_scales,
            per_token_scale,
            stream,
        )

    @cute.jit
    def __call__(
        self,
        weights,
        activations,
        weights_sf,
        activations_sf,
        output,
        output_sf,
        alpha,
        norm_const,
        token_mapping,
        expert_idx,
        mn_limit,
        num_tiles,
        token_final_scales,
        per_token_scale,
        stream,
    ):
        tiled_mma = sm100_utils.make_blockscaled_trivial_tiled_mma(
            self.weight_dtype,
            self.activation_dtype,
            tcgen05.OperandMajorMode.K,
            tcgen05.OperandMajorMode.K,
            self.sf_dtype,
            self.sf_vec_size,
            self.cta_group,
            (self.mma_m, self.allocated_n),
        )
        cluster_layout = cute.tiled_divide(
            cute.make_layout((self.cta_group_size, 1, 1)), (tiled_mma.thr_id.shape,)
        )
        self.a_layout = sm100_utils.make_smem_layout_a(
            tiled_mma, self.physical_tiler, self.a_storage_dtype, self.num_stages
        )
        self.b_layout = sm100_utils.make_smem_layout_b(
            tiled_mma, self.physical_tiler, self.activation_dtype, self.num_stages
        )
        self.sfa_layout = blockscaled_utils.make_smem_layout_sfa(
            tiled_mma, self.physical_tiler, self.sf_vec_size, self.num_stages
        )
        self.sfb_layout = blockscaled_utils.make_smem_layout_sfb(
            tiled_mma, self.physical_tiler, self.sf_vec_size, self.num_stages
        )
        self.acc_layout = tiled_mma.make_fragment_C(
            tiled_mma.partition_shape_C((self.mma_m, self.allocated_n))
        ).layout

        tma_atom_a, tma_weights = cute.nvgpu.make_tiled_tma_atom_A(
            cpasync.CopyBulkTensorTileG2SOp(self.cta_group),
            weights,
            cute.slice_(self.a_layout, (None, None, None, 0)),
            self.physical_tiler,
            tiled_mma,
            cluster_layout.shape,
            internal_type=self.a_storage_dtype if self.unpack_weights else None,
        )

        weight_sf_tensor = cute.make_tensor(
            weights_sf.iterator,
            blockscaled_utils.tile_atom_to_shape_SF(weights.shape, self.sf_vec_size),
        )
        tma_atom_sfa, tma_weights_sf = cute.nvgpu.make_tiled_tma_atom_A(
            cpasync.CopyBulkTensorTileG2SOp(self.cta_group),
            weight_sf_tensor,
            cute.slice_(self.sfa_layout, (None, None, None, 0)),
            self.physical_tiler,
            tiled_mma,
            cluster_layout.shape,
            internal_type=cutlass.Int16,
        )
        tma_atom_b, tma_activations = None, None
        if cutlass.const_expr(self.activation_type is None):
            tma_atom_b, tma_activations = cute.nvgpu.make_tiled_tma_atom_B(
                cpasync.CopyBulkTensorTileG2SOp(self.cta_group),
                activations,
                cute.slice_(self.b_layout, (None, None, None, 0)),
                self.physical_tiler,
                tiled_mma,
                cluster_layout.shape,
            )

        else:
            # Keep both dimensions dynamic so token-count one still has a 2D
            # descriptor. Every supported B mode has one 128-byte row per K tile.
            gather_source = cute.make_tensor(
                activations.iterator,
                cute.make_layout(
                    (
                        cutlass.Int32(activations.shape[0]),
                        cutlass.Int32(activations.shape[1]),
                    ),
                    stride=activations.stride,
                ),
            )
            gather_layout = cute.make_composed_layout(
                cute.make_swizzle(3, 4, 3),
                0,
                cute.make_layout((1, self.tile_k), stride=(self.tile_k, 1)),
            )
            tma_atom_b, _ = cpasync.make_tiled_tma_atom(
                cpasync.CopyBulkTensorTileG2SOp(),
                gather_source,
                gather_layout,
                (1, self.tile_k),
            )

        @cute.struct
        class SharedStorage:
            a_barriers: cute.struct.MemRange[cutlass.Int64, self.num_stages * 2]
            ab_barriers: cute.struct.MemRange[cutlass.Int64, self.num_stages * 2]
            acc_barriers: cute.struct.MemRange[cutlass.Int64, 2 * self.acc_stages]
            relay_barriers: cute.struct.MemRange[cutlass.Int64, self.num_stages * 2]
            tmem_holding: cutlass.Int32
            epilogue_scratch: cute.struct.Align[
                cute.struct.MemRange[cutlass.Float32, 128], 128
            ]
            tmem_dealloc_mbar: cutlass.Int64
            a: cute.struct.Align[
                cute.struct.MemRange[
                    self.a_storage_dtype, cute.cosize(self.a_layout.outer)
                ],
                128,
            ]
            b: cute.struct.Align[
                cute.struct.MemRange[
                    self.activation_dtype, cute.cosize(self.b_layout.outer)
                ],
                128,
            ]
            sfa: cute.struct.Align[
                cute.struct.MemRange[self.sf_dtype, cute.cosize(self.sfa_layout)],
                128,
            ]
            sfb: cute.struct.Align[
                cute.struct.MemRange[self.sf_dtype, cute.cosize(self.sfb_layout)],
                128,
            ]

        self.storage_type = SharedStorage
        self.kernel(
            tiled_mma,
            cluster_layout,
            self.a_layout,
            self.b_layout,
            self.sfa_layout,
            self.sfb_layout,
            self.acc_layout,
            tma_atom_a,
            tma_weights,
            tma_atom_b,
            tma_activations,
            tma_atom_sfa,
            tma_weights_sf,
            activations,
            weights_sf,
            activations_sf,
            output,
            output_sf,
            alpha,
            norm_const,
            token_mapping,
            expert_idx,
            mn_limit,
            num_tiles,
            token_final_scales,
            per_token_scale,
        ).launch(
            grid=(
                self.max_active_clusters // self.cta_group_size * self.cta_group_size,
                1,
                1,
            ),
            cluster=(self.cta_group_size, 1, 1),
            block=(self.threads_per_cta, 1, 1),
            smem=SharedStorage.size_in_bytes(),
            stream=stream,
            min_blocks_per_mp=1,
            use_pdl=self.enable_pdl,
        )

    def _s2t_partition(self, source, target):
        source = cute.filter_zeros(source)
        target = cute.filter_zeros(target)
        atom = cute.make_copy_atom(tcgen05.Cp4x32x128bOp(self.cta_group), self.sf_dtype)
        copy = tcgen05.make_s2t_copy(atom, target)
        thr = copy.get_slice(0)
        source = tcgen05.get_s2t_smem_desc_tensor(copy, thr.partition_S(source))
        return copy, source, thr.partition_D(target)

    @cute.jit
    def _copy_tile(self, atom, source_ptr, destination_ptr, count, valid):
        source = cute.make_tensor(source_ptr, cute.make_layout((count,)))
        destination = cute.make_tensor(destination_ptr, cute.make_layout((count,)))
        predicate = cute.make_rmem_tensor((1,), cutlass.Boolean)
        predicate[0] = valid
        cute.copy_atom_call(atom, source, destination, pred=predicate)

    @cute.kernel
    def kernel(
        self,
        tiled_mma,
        cluster_layout,
        a_layout,
        b_layout,
        sfa_layout,
        sfb_layout,
        acc_layout,
        tma_atom_a,
        weights,
        tma_atom_b,
        tma_activations,
        tma_atom_sfa,
        tma_weights_sf,
        activations,
        weights_sf,
        activations_sf,
        output,
        output_sf,
        alpha,
        norm_const,
        token_mapping,
        expert_idx,
        mn_limit,
        num_tiles,
        token_final_scales,
        per_token_scale,
    ):
        tidx, _, _ = cute.arch.thread_idx()
        warp = tidx // 32
        block, _, _ = cute.arch.block_idx()
        grid, _, _ = cute.arch.grid_dim()
        cta_rank = cute.arch.make_warp_uniform(cute.arch.block_idx_in_cluster())
        block = block // self.cta_group_size
        grid = grid // self.cta_group_size
        storage = utils.SmemAllocator().allocate(self.storage_type)
        a_pipe = PipelineTmaUmma.create(
            barrier_storage=storage.a_barriers.data_ptr(),
            num_stages=self.num_stages,
            producer_group=pipeline.CooperativeGroup(
                pipeline.Agent.Thread, 4 if self.activation_type is not None else 1
            ),
            consumer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread),
            cta_layout_vmnk=cluster_layout,
            tx_count=self.cta_group_size
            * (
                128 * self.tile_k * self.weight_dtype.width // 8
                + self.sf_stage_bytes
                + self.b_rows * self.tile_k * self.activation_dtype.width // 8
            )
            // (4 if self.activation_type is not None else 1),
        )
        ab = PipelineCpAsyncUmma.create(
            barrier_storage=storage.ab_barriers.data_ptr(),
            num_stages=self.num_stages,
            producer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread, 128),
            consumer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread),
            defer_sync=True,
            cta_layout_vmnk=cluster_layout,
        )
        # cp.async completion is CTA-local. Both MMA warps relay that local
        # completion before the leader issues a group-2 MMA.
        relay = None
        if cutlass.const_expr(self.cta_group_size == 2):
            relay = pipeline.PipelineAsyncUmma.create(
                barrier_storage=storage.relay_barriers.data_ptr(),
                num_stages=self.num_stages,
                producer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread, 64),
                consumer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread),
                defer_sync=True,
                cta_layout_vmnk=cluster_layout,
            )
        acc_pipe = PipelineUmmaAsync.create(
            barrier_storage=storage.acc_barriers.data_ptr(),
            num_stages=self.acc_stages,
            producer_group=pipeline.CooperativeGroup(pipeline.Agent.Thread),
            consumer_group=pipeline.CooperativeGroup(
                pipeline.Agent.Thread, 128 * self.cta_group_size
            ),
            cta_layout_vmnk=cluster_layout,
        )
        tmem = utils.TmemAllocator(
            storage.tmem_holding.ptr,
            barrier_for_retrieve=pipeline.NamedBarrier(
                barrier_id=3, num_threads=self.threads_per_cta
            ),
            allocator_warp_id=0,
            is_two_cta=self.cta_group_size == 2,
            two_cta_tmem_dealloc_mbar_ptr=storage.tmem_dealloc_mbar.ptr
            if self.cta_group_size == 2
            else None,
        )
        if cutlass.const_expr(self.cta_group_size == 2):
            cute.arch.cluster_arrive_relaxed()
            cute.arch.cluster_wait()
        tmem.allocate(self.tmem_cols)
        tmem.wait_for_alloc()
        tmem_ptr = tmem.retrieve_ptr(cutlass.Float32)
        sA = storage.a.get_tensor(a_layout.outer, swizzle=a_layout.inner)
        sB = storage.b.get_tensor(b_layout.outer, swizzle=b_layout.inner)
        sSFA = storage.sfa.get_tensor(sfa_layout)
        sSFB = storage.sfb.get_tensor(sfb_layout)
        gA = cute.local_tile(weights, (self.mma_m, self.tile_k), (None, None, None))
        tCgA = tiled_mma.get_slice(cta_rank).partition_A(gA)
        tAsA, tAgA = cpasync.tma_partition(
            tma_atom_a,
            0,
            cute.make_layout(1),
            cute.group_modes(sA, 0, 3),
            cute.group_modes(tCgA, 0, 3),
        )
        gSFA = cute.local_tile(
            tma_weights_sf, (self.mma_m, self.tile_k), (None, None, None)
        )
        tCgSFA = tiled_mma.get_slice(cta_rank).partition_A(gSFA)
        tAsSFA, tAgSFA = cpasync.tma_partition(
            tma_atom_sfa,
            0,
            cute.make_layout(1),
            cute.group_modes(sSFA, 0, 3),
            cute.group_modes(tCgSFA, 0, 3),
        )
        tAsSFA = cute.filter_zeros(tAsSFA)
        tAgSFA = cute.filter_zeros(tAgSFA)
        griddepcontrol_wait()
        total_m_tiles = cute.ceil_div(weights.shape[0], self.mma_m)
        total_tiles = num_tiles[0] * total_m_tiles
        k_tiles = cute.ceil_div(weights.shape[1], self.tile_k)
        padded_k = cute.ceil_div(weights.shape[1], self.sf_block_k) * self.sf_block_k

        if warp < 4:
            copy_sf = cute.make_copy_atom(
                cpasync.CopyG2SOp(), self.sf_dtype, num_bits_per_copy=32
            )
            producer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Producer, self.num_stages
            )
            consumer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Consumer, self.acc_stages
            )
            for tile in cutlass.range(block, total_tiles, grid):
                route_idx = tile // total_m_tiles
                channel_start = (tile % total_m_tiles) * self.mma_m + cta_rank * 128
                route_start = route_idx * self.route_tile
                expert = expert_idx[route_idx]
                valid = cutlass.min(self.route_tile, mn_limit[route_idx] - route_start)
                if cutlass.const_expr(self.activation_type is None):
                    # N16 routing tiles can start halfway through a physical N32 tile.
                    gB = cute.local_tile(
                        cute.domain_offset(
                            (
                                route_start
                                + cta_rank
                                * (
                                    ((valid + 15) & -16) // self.cta_group_size
                                    - self.allocated_n // self.cta_group_size
                                ),
                                0,
                            ),
                            tma_activations,
                        ),
                        (self.allocated_n, self.tile_k),
                        (0, None),
                    )
                    tCgB = tiled_mma.get_slice(cta_rank).partition_B(gB)
                    tBsB, tBgB = cpasync.tma_partition(
                        tma_atom_b,
                        0,
                        cute.make_layout(1),
                        cute.group_modes(sB, 0, 3),
                        cute.group_modes(tCgB, 0, 3),
                    )
                if cutlass.const_expr(self.activation_type is not None):
                    # Each warp owns interleaved eight-row runs. Hoist vectorized
                    # routing-index loads before K and retain invalid rows as OOB.
                    gather_row_ids = cute.make_rmem_tensor(
                        (self.b_rows // 4,), cutlass.Int32
                    )
                    index_atom = cute.make_copy_atom(
                        cute.nvgpu.CopyUniversalOp(),
                        cutlass.Int32,
                        num_bits_per_copy=128,
                    )
                    for run in cutlass.range_constexpr(self.b_rows // 32):
                        row_base = (warp + 4 * run) * 8
                        source_row_base = row_base + cta_rank * (
                            ((valid + 15) & -16) // self.cta_group_size
                        )
                        if source_row_base < valid:
                            index_source = cute.make_tensor(
                                token_mapping.iterator
                                + cute.assume(route_start + source_row_base, divby=8),
                                cute.make_layout((8,)),
                            )
                            index_target = cute.make_tensor(
                                gather_row_ids.iterator + run * 8,
                                cute.make_layout((8,)),
                            )
                            cute.copy(index_atom, index_source, index_target)
                        for j in cutlass.range_constexpr(8):
                            if source_row_base + j < valid:
                                gather_row_ids[run * 8 + j] = (
                                    gather_row_ids[run * 8 + j] // self.top_k
                                )
                            else:
                                gather_row_ids[run * 8 + j] = cutlass.Int32(
                                    activations.shape[0]
                                )
                # Give each lane a different SMEM bank for its four scale bytes.
                sf_row = 8 * warp + 32 * ((tidx % 32) // 8) + tidx % 8
                activation_sf_offsets = cute.make_rmem_tensor(
                    (self.sfb_row_blocks,), cutlass.Int64
                )
                for row_block in cutlass.range_constexpr(self.sfb_row_blocks):
                    row = sf_row + row_block * 128
                    sf_source_row = cutlass.Int32(0)
                    if row < valid:
                        if cutlass.const_expr(self.activation_type is not None):
                            sf_source_row = (
                                token_mapping[route_start + row] // self.top_k
                            )
                        else:
                            sf_source_row = route_start + row
                    if cutlass.const_expr(self.activation_type is not None):
                        activation_sf_offsets[row_block] = sf_source_row * (
                            weights.shape[1] // self.sf_vec_size
                        )
                    else:
                        activation_sf_offsets[row_block] = _blockscaled_sf_offset(
                            sf_source_row, 0, padded_k, self.sf_vec_size
                        )
                shared_sf_offset = (sf_row % 32) * 16 + (sf_row // 32) * 4
                for k_tile in cutlass.range(k_tiles):
                    ab.producer_acquire(producer)
                    if cutlass.const_expr(self.activation_type is not None):
                        a_pipe.producer_acquire(producer)
                    if warp == 0:
                        # TMA copy lowering elects internally; keep the whole warp active.
                        if cutlass.const_expr(self.activation_type is None):
                            a_pipe.producer_acquire(producer)
                        cute.copy(
                            tma_atom_a,
                            tAgA[(None, tile % total_m_tiles, k_tile, expert)],
                            tAsA[(None, producer.index)],
                            tma_bar_ptr=a_pipe.producer_get_barrier(producer),
                        )
                        cute.copy(
                            tma_atom_sfa,
                            tAgSFA[(None, tile % total_m_tiles, k_tile, expert)],
                            tAsSFA[(None, producer.index)],
                            tma_bar_ptr=a_pipe.producer_get_barrier(producer),
                        )
                        if cutlass.const_expr(self.activation_type is None):
                            cute.copy(
                                tma_atom_b,
                                tBgB[(None, k_tile)],
                                tBsB[(None, producer.index)],
                                tma_bar_ptr=a_pipe.producer_get_barrier(producer),
                            )
                    if cutlass.const_expr(self.activation_type is not None):
                        # Four arrivals jointly register the transaction count;
                        # each warp can issue its Gather4 loads after its arrival.
                        for run in cutlass.range_constexpr(self.b_rows // 32):
                            row_base = (warp + 4 * run) * 8
                            for half in cutlass.range_constexpr(2):
                                offset = cute.assume(
                                    (producer.index * self.b_rows + row_base + half * 4)
                                    * self.tile_k,
                                    divby=4 * self.tile_k,
                                )
                                first = run * 8 + half * 4
                                with cute.arch.elect_one():
                                    _blockscaled_tma_gather4(
                                        tma_atom_b,
                                        sB.iterator + offset,
                                        a_pipe.producer_get_barrier(producer),
                                        k_tile * self.tile_k,
                                        gather_row_ids[first],
                                        gather_row_ids[first + 1],
                                        gather_row_ids[first + 2],
                                        gather_row_ids[first + 3],
                                        self.cta_group_size,
                                    )
                    # Four contiguous SF bytes form one prepared scale-factor block.
                    for row_block in cutlass.range_constexpr(self.sfb_row_blocks):
                        row = sf_row + row_block * 128
                        for sf_block in cutlass.range_constexpr(
                            self.tile_k // self.sf_block_k
                        ):
                            channel = k_tile * self.tile_k + sf_block * self.sf_block_k
                            shared_offset = (
                                producer.index * self.sfb_stage_bytes
                                + row_block * self.sf_stage_bytes
                                + sf_block * 512
                                + shared_sf_offset
                            )
                            if cutlass.const_expr(self.activation_type is not None):
                                activation_offset = (
                                    activation_sf_offsets[row_block]
                                    + channel // self.sf_vec_size
                                )
                            else:
                                activation_offset = (
                                    activation_sf_offsets[row_block]
                                    + (channel // self.sf_block_k) * 512
                                )
                            self._copy_tile(
                                copy_sf,
                                activations_sf.iterator
                                + cute.assume(activation_offset, divby=4),
                                sSFB.iterator + cute.assume(shared_offset, divby=4),
                                4,
                                (row < valid) & (channel < weights.shape[1]),
                            )
                    ab.producer_commit(producer)
                    producer.advance()
                if cutlass.const_expr(not self.overlap_epilogue):
                    acc_pipe.consumer_wait(consumer)
                    norm = cutlass.Float32(1.0)
                    if cutlass.const_expr(norm_const is not None):
                        norm = norm_const[0]
                    epi_accumulator = cute.make_tensor(
                        tmem_ptr
                        + cute.assume(consumer.index * self.acc_cols, divby=32),
                        acc_layout,
                    )
                    self.epilogue.run(
                        tiled_mma,
                        epi_accumulator,
                        output,
                        output_sf,
                        alpha[expert],
                        norm,
                        per_token_scale,
                        token_mapping,
                        token_final_scales,
                        channel_start,
                        route_start,
                        valid,
                        expert,
                        tidx,
                        storage.epilogue_scratch.data_ptr(),
                    )
                    cute.arch.fence_view_async_tmem_load()
                    acc_pipe.consumer_release(consumer)
                    consumer.advance()
            # Each tail advances its state through all stages.
            ab.producer_tail(producer.clone())
            if warp == 0:
                a_pipe.producer_tail(producer)
        elif warp < (8 if self.overlap_epilogue else 4):
            consumer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Consumer, self.acc_stages
            )
            for tile in cutlass.range(block, total_tiles, grid):
                route_idx = tile // total_m_tiles
                channel_start = (tile % total_m_tiles) * self.mma_m + cta_rank * 128
                route_start = route_idx * self.route_tile
                expert = expert_idx[route_idx]
                valid = cutlass.min(self.route_tile, mn_limit[route_idx] - route_start)
                acc_pipe.consumer_wait(consumer)
                norm = cutlass.Float32(1.0)
                if cutlass.const_expr(norm_const is not None):
                    norm = norm_const[0]
                epi_accumulator = cute.make_tensor(
                    tmem_ptr + cute.assume(consumer.index * self.acc_cols, divby=32),
                    acc_layout,
                )
                self.epilogue.run(
                    tiled_mma,
                    epi_accumulator,
                    output,
                    output_sf,
                    alpha[expert],
                    norm,
                    per_token_scale,
                    token_mapping,
                    token_final_scales,
                    channel_start,
                    route_start,
                    valid,
                    expert,
                    tidx - 128,
                    storage.epilogue_scratch.data_ptr(),
                )
                cute.arch.fence_view_async_tmem_load()
                acc_pipe.consumer_release(consumer)
                consumer.advance()
        else:
            tSFA = cute.make_tensor(
                cute.recast_ptr(
                    tmem_ptr + self.acc_stages * self.acc_cols, dtype=self.sf_dtype
                ),
                blockscaled_utils.make_tmem_layout_sfa(
                    tiled_mma,
                    self.physical_tiler,
                    self.sf_vec_size,
                    cute.slice_(sfa_layout, (None, None, None, 0)),
                ),
            )
            tSFB = cute.make_tensor(
                cute.recast_ptr(
                    tmem_ptr + self.acc_stages * self.acc_cols + self.sf_cols,
                    dtype=self.sf_dtype,
                ),
                blockscaled_utils.make_tmem_layout_sfb(
                    tiled_mma,
                    self.physical_tiler,
                    self.sf_vec_size,
                    cute.slice_(sfb_layout, (None, None, None, 0)),
                ),
            )
            copy_a, source_a, target_a = self._s2t_partition(sSFA, tSFA)
            copy_b, source_b, target_b = self._s2t_partition(sSFB, tSFB)
            fragment_a = tiled_mma.make_fragment_A(sA)
            fragment_b = tiled_mma.make_fragment_B(sB)
            consumer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Consumer, self.num_stages
            )
            producer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Producer, self.acc_stages
            )
            relay_producer = pipeline.make_pipeline_state(
                pipeline.PipelineUserType.Producer, self.num_stages
            )
            for tile in cutlass.range(block, total_tiles, grid):
                route_idx = tile // total_m_tiles
                route_start = route_idx * self.route_tile
                valid = cutlass.min(self.route_tile, mn_limit[route_idx] - route_start)
                mma_accumulator = cute.make_tensor(
                    tmem_ptr + cute.assume(producer.index * self.acc_cols, divby=32),
                    acc_layout,
                )
                if cta_rank == 0:
                    acc_pipe.producer_acquire(producer)
                for k_tile in cutlass.range(k_tiles):
                    ab.consumer_wait(consumer)
                    if cutlass.const_expr(self.cta_group_size == 2):
                        relay.producer_acquire(relay_producer)
                        cute.arch.fence_proxy("async.shared", space="cta")
                        relay.producer_commit(relay_producer)
                    if cta_rank == 0:
                        if cutlass.const_expr(self.cta_group_size == 2):
                            relay.consumer_wait(consumer)
                        a_pipe.consumer_wait(consumer)
                        sf_stage = (None, None, None, None, consumer.index)
                        cute.copy(copy_a, source_a[sf_stage], target_a)
                        cute.copy(copy_b, source_b[sf_stage], target_b)
                        _blockscaled_dynamic_mma(
                            mma_accumulator,
                            fragment_a[(None, None, None, consumer.index)],
                            fragment_b[(None, None, None, consumer.index)],
                            tSFA,
                            tSFB,
                            valid,
                            k_tile,
                            self.instruction,
                            self.descriptor,
                            self.cta_group_size,
                        )
                        ab.consumer_release(consumer)
                        a_pipe.consumer_release(consumer)
                        if cutlass.const_expr(self.cta_group_size == 2):
                            relay.consumer_release(consumer)
                    relay_producer.advance()
                    consumer.advance()
                if cta_rank == 0:
                    acc_pipe.producer_commit(producer)
                producer.advance()
            if cutlass.const_expr(self.cta_group_size == 2):
                relay.producer_tail(relay_producer)
            if cta_rank == 0:
                acc_pipe.producer_tail(producer)
        pipeline.NamedBarrier(
            barrier_id=1, num_threads=self.threads_per_cta
        ).arrive_and_wait()
        if warp < 4:
            tmem.relinquish_alloc_permit()
            pipeline.NamedBarrier(barrier_id=2, num_threads=128).arrive_and_wait()
            tmem.free(tmem_ptr, num_columns=self.tmem_cols)
        griddepcontrol_launch_dependents()


class Sm100BlockScaledContiguousGroupedGemmFinalizeFusionKernel(
    Sm100BlockScaledGroupedGemmKernel
):
    """FC2 capability adapter retaining the public logical activation/weight API."""

    @classmethod
    def can_implement(
        cls,
        a_dtype,
        b_dtype,
        sf_dtype,
        sf_vec_size,
        out_dtype,
        final_scale_dtype,
        mma_tiler_mn,
        cluster_shape_mn,
        m,
        n,
        k,
        l,
        a_major,
        b_major,
        out_major,
    ):
        if a_major != "k" or b_major != "k" or out_major != "n" or l <= 0:
            return False
        if final_scale_dtype not in (
            cutlass.Float32,
            cutlass.BFloat16,
            cutlass.Float16,
        ):
            return False
        if out_dtype not in (cutlass.Float32, cutlass.BFloat16, cutlass.Float16):
            return False
        if a_dtype is not b_dtype and out_dtype is not cutlass.BFloat16:
            return False
        return Sm100BlockScaledGroupedGemmKernel.can_implement(
            n,
            m,
            k,
            out_dtype,
            mma_tiler_mn,
            cluster_shape_mn,
            a_dtype,
            b_dtype,
            sf_dtype,
            sf_vec_size,
        )
