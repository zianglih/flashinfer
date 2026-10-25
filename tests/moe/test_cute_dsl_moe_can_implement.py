"""Host checks for the shared blockscaled MoE operand contract.

All SM100 types put channel tiles on M and routed tokens on N.
These checks exercise the existing classmethod hooks without GPU work.
"""

import pytest

cutlass = pytest.importorskip("cutlass")

from flashinfer.fused_moe.cute_dsl.blackwell.blockscaled_contiguous_gather_grouped_gemm_act_fusion import (  # noqa: E501
    BlockScaledContiguousGatherGroupedGemmKernel,
)
from flashinfer.fused_moe.cute_dsl.blackwell.blockscaled_contiguous_grouped_gemm_finalize_fusion import (  # noqa: E501
    Sm100BlockScaledContiguousGroupedGemmFinalizeFusionKernel,
)


def _finalize_ok(
    n,
    mma_tiler_mn,
    cluster_shape_mn,
    *,
    a_dtype=cutlass.Float4E2M1FN,
    b_dtype=cutlass.Float4E2M1FN,
    sf_dtype=cutlass.Float8E4M3FN,
    sf_vec_size=16,
    k=512,
):
    return Sm100BlockScaledContiguousGroupedGemmFinalizeFusionKernel.can_implement(
        a_dtype=a_dtype,
        b_dtype=b_dtype,
        sf_dtype=sf_dtype,
        sf_vec_size=sf_vec_size,
        out_dtype=cutlass.BFloat16,
        final_scale_dtype=cutlass.Float32,
        mma_tiler_mn=mma_tiler_mn,
        cluster_shape_mn=cluster_shape_mn,
        m=1024,
        n=n,
        k=k,
        l=8,
        a_major="k",
        b_major="k",
        out_major="n",
    )


def _gemm1_ok(
    n,
    mma_tiler_mn,
    cluster_shape_mn,
    *,
    a_dtype=cutlass.Float4E2M1FN,
    b_dtype=cutlass.Float4E2M1FN,
    sf_dtype=cutlass.Float8E4M3FN,
    sf_vec_size=16,
    c_dtype=cutlass.Float4E2M1FN,
    k=512,
):
    return BlockScaledContiguousGatherGroupedGemmKernel.can_implement(
        a_dtype=a_dtype,
        b_dtype=b_dtype,
        sf_dtype=sf_dtype,
        sf_vec_size=sf_vec_size,
        c_dtype=c_dtype,
        mma_tiler_mn=mma_tiler_mn,
        cluster_shape_mn=cluster_shape_mn,
        m=1024,
        n=n,
        k=k,
        l=8,
        a_major="k",
        b_major="k",
        c_major="n",
    )


@pytest.mark.parametrize(
    "n,mma,cluster,expect",
    [
        # Output channels form complete M128 tiles; N is routed-token capacity.
        (128, (128, 16), (1, 1), True),
        (256, (128, 32), (1, 1), True),
        (384, (128, 64), (1, 1), True),
        (512, (128, 128), (1, 1), True),
        (256, (128, 256), (1, 1), True),
        # Previous channel-N192 tactics are not routed-token tactics.
        (384, (128, 192), (1, 1), False),
        # Two CTAs jointly issue M256 while retaining one M128 output per CTA.
        (256, (256, 128), (2, 1), True),
        (512, (256, 256), (2, 1), True),
        (384, (256, 256), (2, 1), True),
        (128, (256, 128), (2, 1), True),
        (256, (256, 64), (2, 1), False),
        (128, (128, 128), (1, 2), False),
        (256, (128, 128), (2, 1), False),
        (256, (256, 128), (1, 1), False),
        # Reusing B across two channel tiles is an FC1-only tactic.
        (512, (512, 128), (2, 1), False),
    ],
)
def test_finalize_n_tiling(n, mma, cluster, expect):
    assert _finalize_ok(n, mma, cluster) is expect


@pytest.mark.parametrize(
    "n,mma,expect",
    [
        # The gated epilogue produces 64 channels per physical M128 tile.
        (384, (128, 16), True),
        (512, (128, 64), True),
        # Weight scale storage still requires complete 128-channel atoms.
        (192, (128, 128), False),
    ],
)
def test_gemm1_n_tiling_guard(n, mma, expect):
    # Routed-token N is shared by the two blockscaled GEMMs.
    assert _gemm1_ok(n, mma, (1, 1)) is expect


@pytest.mark.parametrize("op", [_gemm1_ok, _finalize_ok])
def test_w4a8_dtype_contract(op):
    kwargs = dict(
        a_dtype=cutlass.Float8E4M3FN,
        b_dtype=cutlass.Float4E2M1FN,
        sf_dtype=cutlass.Float8E8M0FNU,
        sf_vec_size=32,
        k=128,
    )
    if op is _gemm1_ok:
        kwargs["c_dtype"] = cutlass.Float8E4M3FN
    assert op(256, (128, 128), (1, 1), **kwargs)
    assert not op(
        256,
        (128, 128),
        (1, 1),
        **{
            **kwargs,
            "a_dtype": cutlass.Float4E2M1FN,
            "b_dtype": cutlass.Float8E4M3FN,
        },
    )
    assert not op(
        256,
        (128, 128),
        (1, 1),
        **{**kwargs, "sf_dtype": cutlass.Float8E4M3FN},
    )
    assert not op(256, (128, 128), (1, 1), **{**kwargs, "sf_vec_size": 16})
    assert not op(256, (128, 128), (1, 1), **{**kwargs, "k": 64})


@pytest.mark.parametrize(
    "mma,n,expect",
    [
        ((128, 64), 128, True),
        ((128, 32), 384, True),
        ((128, 64), 192, False),
        ((128, 192), 256, False),
    ],
)
def test_w4a8_finalize_n_tiling(mma, n, expect):
    assert (
        _finalize_ok(
            n,
            mma,
            (1, 1),
            a_dtype=cutlass.Float8E4M3FN,
            b_dtype=cutlass.Float4E2M1FN,
            sf_dtype=cutlass.Float8E8M0FNU,
            sf_vec_size=32,
            k=128,
        )
        is expect
    )


def test_every_rubin_tactic_is_single_cta():
    """No enumerated Rubin tactic may use a multi-CTA cluster.

    ``moe_sort`` leaves tile-metadata entries past ``num_non_exiting_tiles``
    uninitialized, and both GEMMs bound their reads by that exact count. A
    ``cluster_shape_m > 1`` tactic would need the count rounded up to a
    multiple of ``cluster_shape_m`` for barrier uniformity, which widens
    those reads past what routing wrote. Neither the rounding nor the
    matching buffer initialization is implemented, so such a tactic must
    never reach the autotuner.
    """
    from flashinfer.fused_moe.cute_dsl.tuner import ALL_RUBIN_MOE_TACTICS

    assert ALL_RUBIN_MOE_TACTICS, "Rubin tactic list is empty -- nothing asserted"
    for tile_size, gemm1_tactic, gemm2_tactic in ALL_RUBIN_MOE_TACTICS:
        _, _, gemm1_cluster_shape_mn, _ = gemm1_tactic
        _, _, gemm2_cluster_shape_mn, _ = gemm2_tactic
        assert gemm1_cluster_shape_mn[0] == 1, (
            f"gemm1 tactic {gemm1_tactic} at tile_size={tile_size} uses "
            f"cluster_shape_m={gemm1_cluster_shape_mn[0]}"
        )
        assert gemm2_cluster_shape_mn[0] == 1, (
            f"gemm2 tactic {gemm2_tactic} at tile_size={tile_size} uses "
            f"cluster_shape_m={gemm2_cluster_shape_mn[0]}"
        )


@pytest.mark.parametrize(
    "a_dtype,b_dtype,sf_dtype,sf_vec_size,c_dtype",
    [
        (
            cutlass.Float4E2M1FN,
            cutlass.Float4E2M1FN,
            cutlass.Float8E4M3FN,
            16,
            cutlass.Float4E2M1FN,
        ),
        (
            cutlass.Float4E2M1FN,
            cutlass.Float4E2M1FN,
            cutlass.Float8E8M0FNU,
            16,
            cutlass.Float4E2M1FN,
        ),
        (
            cutlass.Float4E2M1FN,
            cutlass.Float4E2M1FN,
            cutlass.Float8E8M0FNU,
            32,
            cutlass.Float4E2M1FN,
        ),
        (
            cutlass.Float8E4M3FN,
            cutlass.Float8E4M3FN,
            cutlass.Float8E8M0FNU,
            32,
            cutlass.Float8E4M3FN,
        ),
        (
            cutlass.Float8E5M2,
            cutlass.Float8E5M2,
            cutlass.Float8E8M0FNU,
            32,
            cutlass.Float8E5M2,
        ),
        (
            cutlass.Float8E4M3FN,
            cutlass.Float4E2M1FN,
            cutlass.Float8E8M0FNU,
            32,
            cutlass.Float8E4M3FN,
        ),
    ],
)
def test_gemm1_logical_m512_geometry(a_dtype, b_dtype, sf_dtype, sf_vec_size, c_dtype):
    kwargs = dict(
        a_dtype=a_dtype,
        b_dtype=b_dtype,
        sf_dtype=sf_dtype,
        sf_vec_size=sf_vec_size,
        c_dtype=c_dtype,
    )
    assert _gemm1_ok(384, (512, 128), (2, 1), **kwargs)
    assert not _gemm1_ok(384, (512, 256), (2, 1), **kwargs)
    assert not _gemm1_ok(384, (512, 128), (1, 1), **kwargs)
    assert not _gemm1_ok(384, (512, 128), (4, 1), **kwargs)
