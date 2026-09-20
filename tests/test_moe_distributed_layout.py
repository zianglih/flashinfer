"""CPU-only contracts; run with python -S tests/test_moe_distributed_layout.py."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


BENCHMARKS = Path(__file__).resolve().parents[1] / "benchmarks"
sys.path.insert(0, str(BENCHMARKS))

from moe_distributed_layout import (  # noqa: E402
    alignment_worker_arguments,
    model_shape,
    resolve_megamoe_capacity,
    token_layout,
    validate_alignment_options,
)


class TokenLayoutTests(unittest.TestCase):
    def test_fewer_tokens_than_ranks(self):
        layout = token_layout(3, 8)
        self.assertEqual(layout.counts, (1, 1, 1, 0, 0, 0, 0, 0))
        self.assertEqual(layout.offsets, (0, 1, 2, 3, 3, 3, 3, 3))
        self.assertEqual(layout.padded_positions, (0, 1, 2))
        self.assertEqual(layout.valid_mask, (True,) * 3 + (False,) * 5)
        self.assertEqual(layout.per_rank_capacity, 1)
        self.assertEqual(layout.padded_tokens, 8)

    def test_nondivisible_tokens(self):
        layout = token_layout(10, 4)
        self.assertEqual(layout.counts, (3, 3, 2, 2))
        self.assertEqual(layout.offsets, (0, 3, 6, 8))
        self.assertEqual(layout.padded_positions, (0, 1, 2, 3, 4, 5, 6, 7, 9, 10))
        self.assertEqual(layout.valid_mask, (True,) * 8 + (False, True, True, False))
        self.assertEqual(layout.per_rank_capacity, 3)
        self.assertEqual(layout.padded_tokens, 12)

    def test_divisible_and_single_rank_need_no_padding(self):
        for tokens, ranks in ((32, 8), (7, 1), (1, 1)):
            with self.subTest(tokens=tokens, ranks=ranks):
                layout = token_layout(tokens, ranks)
                self.assertEqual(layout.counts, (tokens // ranks,) * ranks)
                self.assertEqual(layout.padded_positions, tuple(range(tokens)))
                self.assertEqual(layout.valid_mask, (True,) * tokens)
                self.assertEqual(layout.padded_tokens, tokens)

    def test_rank_major_padding_restores_compact_tokens(self):
        # Distinct rank and token labels detect a misplaced block or valid row.
        for tokens, ranks in ((1, 8), (3, 8), (10, 4), (17, 8), (32, 8)):
            with self.subTest(tokens=tokens, ranks=ranks):
                layout = token_layout(tokens, ranks)
                compact = [f"token-{index}" for index in range(tokens)]
                padded = []
                for rank, (offset, count) in enumerate(
                    zip(layout.offsets, layout.counts, strict=True)
                ):
                    padded.extend(compact[offset : offset + count])
                    padded.extend(
                        [f"padding-rank-{rank}"] * (layout.per_rank_capacity - count)
                    )
                self.assertEqual(len(padded), layout.padded_tokens)
                self.assertEqual(
                    [padded[index] for index in layout.padded_positions], compact
                )
                self.assertEqual(
                    [
                        row
                        for row, valid in zip(padded, layout.valid_mask, strict=True)
                        if valid
                    ],
                    compact,
                )

    def test_rank_output_slices_exclude_padding_and_empty_ranks(self):
        layout = token_layout(3, 8)
        # Simulate rank-major output after a collective, including poison padding.
        padded_output = ["output-0", "output-1", "output-2"] + ["invalid"] * 5
        local_outputs = [
            padded_output[
                rank * layout.per_rank_capacity : rank * layout.per_rank_capacity
                + count
            ]
            for rank, count in enumerate(layout.counts)
        ]
        self.assertEqual([len(rows) for rows in local_outputs], list(layout.counts))
        self.assertEqual(local_outputs[3:], [[], [], [], [], []])
        self.assertEqual(
            [row for rows in local_outputs for row in rows],
            ["output-0", "output-1", "output-2"],
        )

    def test_invalid_token_count_and_world_size(self):
        for invalid in (0, -1, True, 1.0, "8", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    token_layout(invalid, 8)
                with self.assertRaises(ValueError):
                    token_layout(8, invalid)


class CapacityTests(unittest.TestCase):
    def test_default_is_maximum_live_rank_count(self):
        self.assertEqual(resolve_megamoe_capacity(3, 8, None), 1)
        self.assertEqual(resolve_megamoe_capacity(10, 4, None), 3)

    def test_exact_and_larger_capacity_preserve_requested_value(self):
        self.assertEqual(resolve_megamoe_capacity(10, 4, 3), 3)
        self.assertEqual(resolve_megamoe_capacity(10, 4, 512), 512)

    def test_insufficient_or_noninteger_capacity_rejected(self):
        for invalid in (0, -1, 1, 2, True, 3.0, "3"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                resolve_megamoe_capacity(10, 4, invalid)


class ModelShapeTests(unittest.TestCase):
    def test_original_deepseek_shape(self):
        self.assertEqual(
            model_shape("deepseek-v3"),
            {
                "hidden_size": 7168,
                "intermediate_size": 2048,
                "num_experts": 256,
                "n_group": 8,
                "topk_group": 4,
                "top_k": 8,
                "routed_scaling_factor": 2.5,
            },
        )

    def test_glm_shape_and_routing_groups(self):
        self.assertEqual(
            model_shape("glm-5.2"),
            {
                "hidden_size": 6144,
                "intermediate_size": 2048,
                "num_experts": 256,
                "n_group": 1,
                "topk_group": 1,
                "top_k": 8,
                "routed_scaling_factor": 2.5,
            },
        )

    def test_profiles_are_independent(self):
        for name, hidden_size in (("deepseek-v3", 7168), ("glm-5.2", 6144)):
            with self.subTest(name=name):
                profile = model_shape(name)
                profile["hidden_size"] = -1
                self.assertEqual(model_shape(name)["hidden_size"], hidden_size)

    def test_unknown_shape_rejected(self):
        with self.assertRaises(ValueError):
            model_shape("glm-unknown")


class AlignmentOptionsTests(unittest.TestCase):
    def validate(self, **overrides):
        options = dict(
            mode="benchmark",
            parallel_modes=["ep"],
            variants=["w4a16", "w4a16_megamoe"],
            ep_communication="allgather",
            megamoe_capacity=None,
        )
        options.update(overrides)
        validate_alignment_options(**options)

    def test_original_alltoall_options_remain_supported(self):
        for mode in ("benchmark", "profile_nsys", "profile_ncu"):
            with self.subTest(mode=mode):
                self.validate(
                    mode=mode,
                    parallel_modes=["ep", "tp"],
                    variants=["w4a4", "w4a16"],
                    ep_communication="alltoall",
                )

    def test_gather_reduce_support_split_and_optional_megamoe(self):
        for communication in ("allgather", "allreduce"):
            for mode in ("benchmark", "profile_nsys"):
                for variants in (["w4a16"], ["w4a16", "w4a16_megamoe"]):
                    with self.subTest(
                        communication=communication, mode=mode, variants=variants
                    ):
                        self.validate(
                            ep_communication=communication, mode=mode, variants=variants
                        )

    def test_gather_reduce_reject_tp_or_w4a4_or_missing_split(self):
        for communication in ("allgather", "allreduce"):
            for overrides in (
                {"parallel_modes": ["tp"]},
                {"parallel_modes": ["ep", "tp"]},
                {"variants": ["w4a4", "w4a16"]},
                {"variants": ["w4a16_megamoe"]},
                {"mode": "profile_ncu"},
            ):
                with (
                    self.subTest(communication=communication, **overrides),
                    self.assertRaises(ValueError),
                ):
                    self.validate(ep_communication=communication, **overrides)

    def test_capacity_requires_megamoe_and_positive_integer(self):
        self.validate(megamoe_capacity=1)
        with self.assertRaises(ValueError):
            self.validate(variants=["w4a16"], megamoe_capacity=1)
        for invalid in (0, -1, True, 1.5, "1"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.validate(megamoe_capacity=invalid)

    def test_unknown_communication_rejected(self):
        with self.assertRaises(ValueError):
            self.validate(ep_communication="automatic")


class WorkerArgumentsTests(unittest.TestCase):
    def test_profiler_worker_flag_roundtrip_in_cpu_subprocess(self):
        # Exercise argv transport without importing the CUDA benchmark entrypoint.
        worker = """
import argparse
import json
p = argparse.ArgumentParser()
p.add_argument('--model-shape', required=True)
p.add_argument('--ep-communication', required=True)
p.add_argument('--megamoe-max-tokens-per-rank', type=int)
print(json.dumps(vars(p.parse_args())))
"""
        for shape, communication, capacity in (
            ("deepseek-v3", "alltoall", None),
            ("glm-5.2", "allgather", 512),
            ("glm-5.2", "allreduce", 1),
        ):
            with self.subTest(
                shape=shape, communication=communication, capacity=capacity
            ):
                arguments = alignment_worker_arguments(shape, communication, capacity)
                completed = subprocess.run(
                    [sys.executable, "-S", "-c", worker, *arguments],
                    check=True,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(
                    json.loads(completed.stdout),
                    {
                        "model_shape": shape,
                        "ep_communication": communication,
                        "megamoe_max_tokens_per_rank": capacity,
                    },
                )
                self.assertEqual(
                    "--megamoe-max-tokens-per-rank" in arguments, capacity is not None
                )


if __name__ == "__main__":
    unittest.main()
