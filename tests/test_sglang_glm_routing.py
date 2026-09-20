"""CPU contracts for the pinned router; GPU parity is a separate calibration."""

import ast
from functools import lru_cache
import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace, ModuleType
import unittest
from unittest.mock import patch


BENCHMARKS = Path(__file__).resolve().parents[1] / "benchmarks"
HELPER = BENCHMARKS / "sglang_glm_routing.py"
TREE = ast.parse(HELPER.read_text())


def function(name, tree=TREE):
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


class Tensor:
    def __init__(self, shape, dtype="fp32", device=None):
        self.shape = shape
        self.ndim = len(shape)
        self.dtype = dtype
        self.device = device or SimpleNamespace(index=0)
        self.is_cuda = True

    def is_contiguous(self):
        return True

    def stride(self, dim):
        return self.shape[1] if dim == 0 else 1


class Kernel:
    def __init__(self):
        self.calls = []

    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            self.calls.append((grid, args, kwargs))

        return launch


def adapter(major=10):
    kernel = Kernel()
    namespace = {
        "lru_cache": lru_cache,
        "torch": SimpleNamespace(
            float32="fp32",
            int32="i32",
            cuda=SimpleNamespace(get_device_capability=lambda index: (major, 0)),
        ),
        "triton": SimpleNamespace(cdiv=lambda a, b: (a + b - 1) // b),
        "_router_triton_kernel": kernel,
    }
    module = ast.Module(
        body=[function("_supports_pdl"), function("route_glm52")], type_ignores=[]
    )
    exec(compile(module, str(HELPER), "exec"), namespace)
    return namespace["route_glm52"], kernel


def inputs(rows):
    return (
        Tensor((rows, 256)),
        Tensor((256,)),
        Tensor((rows, 8)),
        Tensor((rows, 8), "i32"),
    )


class PinnedRouterTests(unittest.TestCase):
    def test_complete_kernel_matches_fixed_source_ast(self):
        # Golden digest is independently computed from SGLang 50eeb742,
        # python/sglang/kernels/ops/moe/moe_fused_gate.py, including decorator.
        kernel = function("_router_triton_kernel")
        self.assertEqual(
            hashlib.sha256(
                ast.dump(kernel, include_attributes=False).encode()
            ).hexdigest(),
            "075eb2d017d66233cb3ac41155ab1ef8105fa1f0c0f81fccea253bd0e94ffe0a",
        )

    def test_adapter_writes_existing_buffers_with_sglang_glm_parameters(self):
        route, kernel = adapter()
        for rows in (1, 3, 17, 64, 513, 1024):
            tensors = inputs(rows)
            route(*tensors, 2.5)
            grid, args, kwargs = kernel.calls[-1]
            self.assertEqual(grid, (rows,))
            self.assertEqual(args[:4], tensors)
            self.assertEqual(args[4:], (rows, 2.5, 0.0))
            self.assertEqual(
                kwargs,
                dict(
                    N=256,
                    K=8,
                    K_ROUTED=8,
                    BLOCK_M=1,
                    BLOCK_N=256,
                    BLOCK_K=8,
                    N_GROUP=1,
                    TOPK_GROUP=1,
                    EXPERTS_PER_GROUP=256,
                    BLOCK_G=1,
                    SCORING_FUNC=0,
                    HAS_SOFTCAP=False,
                    RENORMALIZE=True,
                    APPLY_SCALE=True,
                    HAS_BIAS=True,
                    USE_PDL=True,
                    stride_sm=256,
                    stride_sn=1,
                    stride_wm=8,
                    stride_wk=1,
                    stride_im=8,
                    stride_ik=1,
                    num_warps=1,
                    launch_pdl=True,
                ),
            )

    def test_empty_rows_do_not_launch(self):
        route, kernel = adapter()
        route(*inputs(0), 2.5)
        self.assertEqual(kernel.calls, [])

    def test_pdl_architecture_policy(self):
        for major in (8, 9, 10):
            with self.subTest(major=major):
                route, kernel = adapter(major)
                route(*inputs(1), 2.5)
                kwargs = kernel.calls[-1][2]
                self.assertEqual(kwargs["USE_PDL"], major >= 9)
                self.assertEqual("launch_pdl" in kwargs, major >= 9)

    def test_wrong_precision_or_shape_rejected(self):
        route, kernel = adapter()
        for tensors in (
            (Tensor((1, 128)), *inputs(1)[1:]),
            (inputs(1)[0], Tensor((128,)), *inputs(1)[2:]),
            (*inputs(1)[:2], Tensor((1, 8), "bf16"), inputs(1)[3]),
            (*inputs(1)[:3], Tensor((1, 8), "i64")),
        ):
            with (
                self.subTest(shapes=[t.shape for t in tensors]),
                self.assertRaises(ValueError),
            ):
                route(*tensors, 2.5)
        self.assertEqual(kernel.calls, [])

    def test_glm_dispatch_and_default_deepseek_contract(self):
        benchmark = ast.parse(
            (BENCHMARKS / "bench_cute_dsl_moe_distributed.py").read_text()
        )
        module = ast.Module(
            body=[function("_route_tokens", benchmark)], type_ignores=[]
        )
        calls = []
        fi = ModuleType("flashinfer.fused_moe")
        fi.fused_topk_deepseek = lambda **kwargs: calls.append(("deepseek", kwargs))
        glm = ModuleType("sglang_glm_routing")
        glm.route_glm52 = lambda *args: calls.append(("glm", args))
        for group, kept, expected in ((1, 1, "glm"), (8, 4, "deepseek")):
            namespace = {
                "CFG": SimpleNamespace(
                    n_group=group, topk_group=kept, top_k=8, routed_scaling_factor=2.5
                )
            }
            exec(compile(module, "benchmark_route", "exec"), namespace)
            with patch.dict(
                sys.modules, {"flashinfer.fused_moe": fi, "sglang_glm_routing": glm}
            ):
                tensors = inputs(3)
                namespace["_route_tokens"](*tensors)
                self.assertEqual(calls[-1][0], expected)
                if expected == "deepseek":
                    self.assertEqual(
                        calls[-1][1],
                        dict(
                            scores=tensors[0],
                            bias=tensors[1],
                            n_group=8,
                            topk_group=4,
                            topk=8,
                            routed_scaling_factor=2.5,
                            topk_values=tensors[2],
                            topk_indices=tensors[3],
                        ),
                    )
                else:
                    self.assertEqual(calls[-1][1], (*tensors, 2.5))
                count = len(calls)
                namespace["_route_tokens"](*inputs(0))
                self.assertEqual(len(calls), count)


if __name__ == "__main__":
    unittest.main()
