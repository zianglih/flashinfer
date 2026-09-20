"""CPU policy tests and optional Torch/CUDA oracle checks; no production kernels."""

import ctypes
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks"))
import w4a16_contract_reference as ref  # noqa: E402

torch = None
if importlib.util.find_spec("torch") is not None:
    import torch


class PolicyTests(unittest.TestCase):
    def options(self):
        return dict(
            refcheck=True,
            mode="benchmark",
            modes=["ep"],
            variants=["w4a16", "w4a16_megamoe"],
            fused=False,
            weighted=False,
        )

    def test_explicit_per_path_contract(self):
        ref.validate_refcheck_policy("per-path", **self.options())

    def test_default_does_not_require_new_policy_constraints(self):
        options = self.options()
        options.update(
            refcheck=False,
            mode="profile_nsys",
            modes=["ep", "tp"],
            variants=["w4a4", "w4a16"],
            fused=True,
        )
        ref.validate_refcheck_policy("cross-pair", **options)

    def test_unsupported_per_path_modes_fail(self):
        for key, value in (
            ("refcheck", False),
            ("mode", "profile_nsys"),
            ("modes", ["ep", "tp"]),
            ("variants", ["w4a16_megamoe", "w4a16"]),
            ("variants", ["w4a4", "w4a16", "w4a16_megamoe"]),
            ("fused", True),
            ("weighted", True),
        ):
            with self.subTest(key=key, value=value):
                options = self.options()
                options[key] = value
                with self.assertRaises(ValueError):
                    ref.validate_refcheck_policy("per-path", **options)

    def test_unknown_policy_fails(self):
        with self.assertRaises(ValueError):
            ref.validate_refcheck_policy("skip", **self.options())

    def test_distinct_collective_contracts(self):
        self.assertEqual(
            ref.reduction_contract("w4a16", "allgather"),
            ref.reduction_contract("w4a16", "allreduce"),
        )
        self.assertNotEqual(
            ref.reduction_contract("w4a16", "alltoall"),
            ref.reduction_contract("w4a16", "allgather"),
        )
        self.assertNotEqual(
            ref.reduction_contract("w4a16", "allgather"),
            ref.reduction_contract("w4a16_megamoe", "allgather"),
        )
        for variant, comm in (("w4a4", "allgather"), ("w4a16", "unknown")):
            with self.assertRaises(ValueError):
                ref.reduction_contract(variant, comm)


@unittest.skipUnless(
    torch is not None, "Torch numerical checks require the runtime environment"
)
class ReductionTests(unittest.TestCase):
    def a2a_fixture(self):
        # EP4: source0 contributes two rows, all other ranks one; received rows
        # from source0 are reversed by atomic compaction. Other rows are padding.
        counts = (2, 1, 1, 1)
        x = torch.arange(1, 6, dtype=torch.bfloat16)[:, None].expand(5, 16).contiguous()
        ids = torch.arange(8, dtype=torch.int32).expand(5, 8).contiguous()
        scores = torch.full((5, 8), 0.125)
        partials = (
            torch.arange(8, dtype=torch.bfloat16)[:, None].expand(8, 16).contiguous()
        )
        reference = ref.ContractReference(
            None, None, partials, x, ids, scores, counts, 2, "alltoall", 8
        )
        rx = torch.zeros((8, 16), dtype=torch.bfloat16)
        ri = torch.full((8, 8), 8, dtype=torch.int32)
        rs = torch.zeros((8, 8))
        mapping = {0: 1, 1: 0, 2: 2, 4: 3, 6: 4}
        for received_row, original_row in mapping.items():
            rx[received_row] = x[original_row]
            ri[received_row] = ids[original_row]
            rs[received_row] = scores[original_row]
        return reference, rx, ri, rs

    def test_a2a_partial_mapping_tracks_atomic_compaction(self):
        reference, x, ids, scores = self.a2a_fixture()
        mapped = ref.a2a_partial_reference(reference, x, ids, scores)
        expected_rows = torch.tensor(
            [1.0, 0.0, 2.0, 0.0, 4.0, 0.0, 6.0, 0.0], dtype=torch.bfloat16
        )
        self.assertTrue(torch.equal(mapped[:, 0], expected_rows))

    def test_a2a_partial_mapping_rejects_drop_duplicate_and_ambiguity(self):
        for kind in ("drop", "duplicate", "ambiguous", "wrong_block", "wrong_bits"):
            with self.subTest(kind=kind):
                reference, x, ids, scores = self.a2a_fixture()
                if kind == "drop":
                    ids[0].fill_(8)
                elif kind == "duplicate":
                    x[0].copy_(x[1])
                elif kind == "ambiguous":
                    reference.hidden_states[0].copy_(reference.hidden_states[1])
                elif kind == "wrong_block":
                    x[2].copy_(x[4])
                else:
                    scores[0, 0] += 0.125
                with self.assertRaises(ValueError):
                    ref.a2a_partial_reference(reference, x, ids, scores)

    def test_all_e2m1_codes_and_scale_ownership(self):
        packed = torch.tensor(
            [[0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]], dtype=torch.uint8
        )
        scales = torch.tensor([[0.5]], dtype=torch.float32).to(torch.float8_e4m3fn)
        expected = torch.tensor(
            [
                [
                    0.0,
                    0.25,
                    0.5,
                    0.75,
                    1.0,
                    1.5,
                    2.0,
                    3.0,
                    -0.0,
                    -0.25,
                    -0.5,
                    -0.75,
                    -1.0,
                    -1.5,
                    -2.0,
                    -3.0,
                ]
            ],
            dtype=torch.bfloat16,
        )
        actual = ref._dequantize(packed, scales)
        self.assertTrue(
            torch.equal(actual.view(torch.int16), expected.view(torch.int16))
        )
        two = torch.cat((packed, packed), dim=1)
        scale_pair = torch.tensor([[0.5, 1.0]], dtype=torch.float32).to(
            torch.float8_e4m3fn
        )
        actual = ref._dequantize(two, scale_pair)
        self.assertTrue(torch.equal(actual[:, :16], expected))
        self.assertTrue(torch.equal(actual[:, 16:], expected * 2))

    def test_ordered_route_and_owner_reductions_against_libm_fmaf(self):
        fma = ctypes.CDLL(None).fmaf
        fma.argtypes = [ctypes.c_float] * 3
        fma.restype = ctypes.c_float
        terms = [
            -1.3125,
            0.390625,
            -0.318359375,
            -3.1875,
            -0.78515625,
            3.84375,
            2.9375,
            0.55859375,
        ]
        weights = [
            0.334473192691803,
            0.32887136936187744,
            0.3028431832790375,
            0.3071669042110443,
            0.31060823798179626,
            0.3129969537258148,
            0.3016016483306885,
            0.30143874883651733,
        ]
        owners = [2, 0, 0, 2, 1, 3, 0, 0]
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tensor = torch.tensor(terms, dtype=torch.bfloat16, device=device).reshape(
            1, 8, 1
        )
        scores = torch.tensor([weights], dtype=torch.float32, device=device)
        acc = ctypes.c_float(terms[0] * weights[0]).value
        for term, score in zip(terms[1:], weights[1:], strict=True):
            acc = fma(term, score, acc)
        expected = torch.tensor([[acc]], dtype=torch.bfloat16)
        actual = ref._ordered_combine(tensor, scores).cpu()
        self.assertTrue(
            torch.equal(actual.view(torch.int16), expected.view(torch.int16))
        )
        for rank in range(4):
            mask = torch.tensor([[owner == rank for owner in owners]], device=device)
            acc = 0.0
            for term, score, owner in zip(terms, weights, owners, strict=True):
                if owner == rank:
                    acc = fma(term, score, acc)
            expected = torch.tensor([[acc]], dtype=torch.bfloat16)
            actual = ref._ordered_combine(tensor, scores, mask).cpu()
            self.assertTrue(
                torch.equal(actual.view(torch.int16), expected.view(torch.int16))
            )

    def test_a2a_uses_first_owner_slot_tree_not_rank_order(self):
        # Rank order gives 2; top-k slot tree gives 0 due to FP32 cancellation.
        # Repeated owners in slots4..7 must contribute zero.
        partials = torch.tensor(
            [2**24, -(2**24), 1.0, 1.0], dtype=torch.bfloat16
        ).reshape(4, 1, 1)
        ids = torch.tensor([[0, 128, 64, 192, 1, 65, 129, 193]], dtype=torch.int32)
        actual = ref._a2a_tree_combine(partials, ids, 64)
        self.assertEqual(actual.item(), 0.0)
        rank_tree = (partials[0].float() + partials[1].float()) + (
            partials[2].float() + partials[3].float()
        )
        self.assertEqual(rank_tree.item(), 2.0)

    def test_empty_outputs_and_strict_failure(self):
        empty = torch.empty((0, 16), dtype=torch.bfloat16)
        report = ref._metrics(empty, empty)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["bitwise_mismatches"], 0)
        actual = torch.zeros((1, 1), dtype=torch.bfloat16)
        expected = torch.ones_like(actual)
        self.assertEqual(ref._metrics(actual, expected)["status"], "FAIL")
        self.assertEqual(
            ref._metrics(actual.fill_(float("nan")), expected)["status"], "FAIL"
        )


@unittest.skipUnless(
    torch is not None and torch.cuda.is_available(),
    "CUDA oracle integration requires a GPU",
)
class CudaExpertReferenceTests(unittest.TestCase):
    def test_independent_expert_math_restores_flags_and_returns_cpu_only(self):
        if not hasattr(
            torch.backends.cuda.matmul, "allow_bf16_reduced_precision_reduction_split_k"
        ):
            self.skipTest("Runtime lacks the required split-K precision control")
        device = "cuda"
        # Every weight is 1(E2M1) * 0.5(E4M3), and x=0.5 gives FC1=4.
        # BF16(4*SiLU(4))=15.6875, then FC2=125.5; eight 1/8 routes retain it.
        weights = SimpleNamespace(
            w13=torch.full((8, 32, 8), 0x22, dtype=torch.uint8, device=device),
            w2=torch.full((8, 16, 8), 0x22, dtype=torch.uint8, device=device),
            w13_scale=torch.full((8, 32, 1), 0.5, device=device).to(
                torch.float8_e4m3fn
            ),
            w2_scale=torch.full((8, 16, 1), 0.5, device=device).to(torch.float8_e4m3fn),
        )
        x = torch.full((2, 16), 0.5, dtype=torch.bfloat16, device=device)
        ids = (
            torch.arange(8, dtype=torch.int32, device=device).expand(2, 8).contiguous()
        )
        scores = torch.full((2, 8), 0.125, device=device)
        matmul = torch.backends.cuda.matmul
        flags = (
            matmul.allow_tf32,
            matmul.allow_bf16_reduced_precision_reduction,
            matmul.allow_bf16_reduced_precision_reduction_split_k,
            torch.backends.cuda.preferred_blas_library(),
        )
        for communication in ("allgather", "allreduce", "alltoall"):
            result = ref.build_reference(x, ids, scores, weights, communication)
            self.assertTrue(
                torch.equal(
                    result.mega, torch.full((2, 16), 125.5, dtype=torch.bfloat16)
                )
            )
            self.assertTrue(torch.equal(result.mega, result.split))
            self.assertTrue(
                all(
                    not value.is_cuda
                    for value in vars(result).values()
                    if torch.is_tensor(value)
                )
            )
        self.assertEqual(
            flags,
            (
                matmul.allow_tf32,
                matmul.allow_bf16_reduced_precision_reduction,
                matmul.allow_bf16_reduced_precision_reduction_split_k,
                torch.backends.cuda.preferred_blas_library(),
            ),
        )


if __name__ == "__main__":
    unittest.main()
