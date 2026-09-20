#!/usr/bin/env python3
"""Read d1 tensors on CPU; replay observed reductions without changing acceptance."""

import argparse
import ctypes
import ctypes.util
import hashlib
import itertools
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bits_equal(left, right):
    return left.dtype == right.dtype and left.shape == right.shape and torch.equal(
        left.contiguous().view(torch.uint8), right.contiguous().view(torch.uint8)
    )


def comparison(left, right):
    assert left.shape == right.shape
    diff = (left.float() - right.float()).abs()
    return {
        "elements": left.numel(),
        "bitwise_equal": bits_equal(left, right),
        "numeric_difference_count": int((left != right).sum()),
        "max_abs": float(diff.max()) if diff.numel() else 0.0,
        "left_sha256": hashlib.sha256(bytes(left.contiguous().view(torch.uint8).flatten().tolist())).hexdigest(),
        "right_sha256": hashlib.sha256(bytes(right.contiguous().view(torch.uint8).flatten().tolist())).hexdigest(),
    }


def trees(leaves):
    """All 15 commutative binary trees on four labelled rank partials."""
    if len(leaves) == 1:
        return [leaves[0]]
    result = []
    for count in range(1, len(leaves)):
        for rest in itertools.combinations(leaves[1:], count - 1):
            left = (leaves[0], *rest)
            right = tuple(x for x in leaves if x not in left)
            for a in trees(left):
                for b in trees(right):
                    result.append((a, b))
    return result


def tree_label(tree):
    return str(tree) if isinstance(tree, int) else f"({tree_label(tree[0])}+{tree_label(tree[1])})"


def reduce_tree(tree, partials):
    if isinstance(tree, int):
        return partials[tree]
    return (reduce_tree(tree[0], partials).float() + reduce_tree(tree[1], partials).float()).to(torch.bfloat16)


def replay(terms, weights, owned, fmaf):
    """C99 binary32 fused multiply-add in source K order, then BF16 RN cast."""
    n, k, hidden = terms.shape
    values = terms.float().tolist()
    scales = weights.float().tolist()
    accumulators = []
    for token in range(n):
        slots = [slot for slot in range(k) if bool(owned[token, slot])]
        token_result = []
        for column in range(hidden):
            accumulator = 0.0
            for slot in slots:
                accumulator = fmaf(values[token][slot][column], scales[token][slot], accumulator)
            token_result.append(accumulator)
        accumulators.append(token_result)
    fp32 = torch.tensor(accumulators, dtype=torch.float32)
    return fp32, fp32.to(torch.bfloat16)


def analyze_case(root, n, fmaf, manifests):
    data = []
    for rank in range(4):
        path = root / f"n{n}/rank{rank}.pt"
        sidecar = json.loads(path.with_suffix(".json").read_text())
        digest = sha(path)
        assert digest == sidecar["payload_sha256"]
        assert path.stat().st_size == sidecar["payload_bytes"]
        manifests[str(path.relative_to(root))] = {"sha256": digest, "bytes": path.stat().st_size}
        value = torch.load(path, map_location="cpu", weights_only=True)
        assert sidecar["rank"] == rank and sidecar["global_tokens"] == n
        assert sidecar["local_tokens"] == int(rank < n)
        data.append(value)

    checks = {}
    checks["same_local_hidden_input_bits"] = all(bits_equal(d["split_inputs"]["hidden_states"], d["mega_inputs"]["hidden_states"]) for d in data)
    for field in ("local_logits", "global_logits", "routing_bias"):
        checks["same_" + field + "_bits"] = all(bits_equal(d["split_inputs"][field], d["mega_inputs"][field]) for d in data)
    ids = data[0]["split_activation"]["topk_ids"][:n]
    weights = data[0]["split_activation"]["topk_weights"][:n]
    assert ids.shape == (n, 8) and weights.shape == (n, 8)
    assert weights.dtype == torch.float32
    owners = ids.long() // 64
    assert bool(((ids >= 0) & (ids < 256)).all())
    for rank, d in enumerate(data):
        activation = d["split_activation"]
        checks[f"rank{rank}_same_gathered_input_bits"] = bits_equal(activation["hidden_states_q"], data[0]["split_activation"]["hidden_states_q"])
        checks[f"rank{rank}_same_global_route_ids"] = torch.equal(activation["topk_ids"], data[0]["split_activation"]["topk_ids"])
        checks[f"rank{rank}_same_global_route_weight_bits"] = bits_equal(activation["topk_weights"], data[0]["split_activation"]["topk_weights"])
        expected_valid = torch.zeros((4, 8), dtype=torch.bool)
        expected_valid[:n] = owners == rank
        route = d["split_route_fc2"]
        checks[f"rank{rank}_route_mapping_matches_expert_owner"] = torch.equal(route["valid"], expected_valid)
        checks[f"rank{rank}_invalid_route_terms_zero"] = bool((route["terms"][~expected_valid] == 0).all())
        checks[f"rank{rank}_unpermute_weights_match_activation_bits"] = bits_equal(route["routing_weights"].reshape(4, 8), activation["topk_weights"])
        checks[f"rank{rank}_partial_passed_to_collective_bits"] = bits_equal(route["rank_partial"], d["split_collective"]["rank_partial"])
        checks[f"rank{rank}_saved_reference_matches_collective_bits"] = bits_equal(d["split_saved_reference"], d["split_collective"]["result_with_padding"][:int(rank < n)])
        checks[f"rank{rank}_check_reference_matches_saved_bits"] = bits_equal(d["refcheck"]["reference"], d["split_saved_reference"])
        checks[f"rank{rank}_check_actual_matches_mega_output_bits"] = bits_equal(d["refcheck"]["actual"], d["mega_workspace"]["output"])
        if rank < n:
            checks[f"rank{rank}_mega_input_matches_gathered_bits"] = bits_equal(d["mega_workspace"]["hidden_states"], activation["hidden_states_q"][rank:rank+1])
    mid = torch.cat([d["mega_workspace"]["topk_ids"] for d in data])
    mw = torch.cat([d["mega_workspace"]["topk_weights"] for d in data])
    checks["mega_route_id_values_equal"] = torch.equal(ids.long(), mid.long())
    checks["mega_route_weight_fp32_bits_equal"] = bits_equal(weights, mw)

    # Select the unique owning rank rather than numerically summing disjoint buffers.
    split_terms = torch.empty((n, 8, 6144), dtype=torch.bfloat16)
    for token in range(n):
        for slot in range(8):
            owner = int(owners[token, slot])
            split_terms[token, slot] = data[owner]["split_route_fc2"]["terms"][token, slot]
    mega_terms = torch.cat([d["mega_workspace"]["route_fc2"] for d in data])
    fc2 = comparison(split_terms, mega_terms)
    checks["all_per_route_fc2_bf16_bits_equal"] = fc2["bitwise_equal"]
    actual = torch.cat([d["refcheck"]["actual"] for d in data])
    reference = torch.cat([d["refcheck"]["reference"] for d in data])
    assert actual.dtype == reference.dtype == torch.bfloat16
    error = (actual.float() - reference.float()).abs()
    threshold = 0.01 + 0.01 * reference.float().abs()
    mismatch = (~torch.isfinite(actual)) | (~torch.isfinite(reference)) | (error > threshold)
    saved_mask = torch.cat([d["refcheck"]["mismatch_mask"] for d in data])
    checks["strict_mask_matches_captured"] = torch.equal(mismatch, saved_mask)
    checks["all_inputs_terms_weights_outputs_finite"] = all(bool(torch.isfinite(t).all()) for t in (split_terms, mega_terms, weights, actual, reference))

    mega_fp32, mega_bf16 = replay(mega_terms, weights, torch.ones((n, 8), dtype=torch.bool), fmaf)
    mega_replay = comparison(mega_bf16, actual)
    partials, partial_fp32, partial_replays = [], [], []
    for rank in range(4):
        fp32, bf16 = replay(split_terms, weights, owners == rank, fmaf)
        captured = data[rank]["split_collective"]["rank_partial"][:n]
        partials.append(captured)
        partial_fp32.append(fp32)
        partial_replays.append({"rank": rank, **comparison(bf16, captured)})

    candidates = []
    per_token = {str(token): [] for token in range(n)}
    for tree in trees((0, 1, 2, 3)):
        result = reduce_tree(tree, partials)
        label = tree_label(tree)
        compare = comparison(result, reference)
        candidates.append({"tree": label, **compare})
        for token in range(n):
            if bits_equal(result[token], reference[token]):
                per_token[str(token)].append(label)
    ideal = (split_terms.double() * weights.double()[:, :, None]).sum(dim=1)
    partial_sum = torch.stack(partials).double().sum(dim=0)
    one_final_bf16 = partial_sum.to(torch.bfloat16)
    ideal_bf16 = ideal.to(torch.bfloat16)
    violations = []
    for token, hidden in mismatch.nonzero().tolist():
        ps = [float(t[token, hidden]) for t in partials]
        route_ideal = [float(split_terms[token, slot, hidden].double() * weights[token, slot].double()) for slot in range(8)]
        candidate_values = {tree_label(tree): float(reduce_tree(tree, [p[token, hidden] for p in partials])) for tree in trees((0, 1, 2, 3))}
        violations.append({
            "global_token": token, "source_rank": token, "hidden": hidden,
            "mega_actual": float(actual[token, hidden]), "split_actual": float(reference[token, hidden]),
            "absolute_error": float(error[token, hidden]), "fixed_threshold": float(threshold[token, hidden]),
            "error_over_threshold": float(error[token, hidden] / threshold[token, hidden]),
            "expert_ids": ids[token].tolist(), "expert_owner_ranks": owners[token].tolist(),
            "fp32_route_weights": weights[token].tolist(),
            "shared_bf16_route_fc2": split_terms[token, :, hidden].float().tolist(),
            "weighted_route_terms_fp64": route_ideal,
            "mega_fma32_sum": float(mega_fp32[token, hidden]), "mega_replayed_bf16": float(mega_bf16[token, hidden]),
            "owner_partial_fma32": [float(p[token, hidden]) for p in partial_fp32],
            "owner_partial_actual_bf16": ps,
            "weighted_all_route_sum_fp64": float(ideal[token, hidden]),
            "sum_actual_owner_bf16_partials_fp64": float(partial_sum[token, hidden]),
            "owner_partial_rounding_shift": float(partial_sum[token, hidden] - ideal[token, hidden]),
            "collective_final_shift": float(reference[token, hidden].double() - partial_sum[token, hidden]),
            "full_fp64_sum_cast_once_bf16": float(ideal_bf16[token, hidden]),
            "rounded_partials_sum_cast_once_bf16": float(one_final_bf16[token, hidden]),
            "bf16_tree_candidates_at_element": candidate_values,
            "matching_bf16_tree_candidates_at_element": [label for label, value in candidate_values.items() if value == float(reference[token, hidden])],
        })
    return {
        "global_tokens": n, "world_size": 4, "valid_rows_per_rank": [int(r < n) for r in range(4)],
        "padded_rows_per_rank": 1, "padded_global_rows": 4, "checks": checks,
        "route_fc2": fc2, "mega_k_order_fma_replay": mega_replay,
        "split_owner_k_order_fma_replays": partial_replays,
        "bf16_collective_tree_candidates": candidates,
        "matching_tree_candidates_per_entire_token_row": per_token,
        "fp64_sum_of_bf16_partials_cast_once_vs_actual_collective": comparison(one_final_bf16, reference),
        "fp64_full_weighted_sum_cast_once_vs_mega": comparison(ideal_bf16, actual),
        "fp64_full_weighted_sum_cast_once_vs_split": comparison(ideal_bf16, reference),
        "strict_original_elementwise": {"atol": 0.01, "rtol": 0.01, "elements": actual.numel(), "failed_elements": int(mismatch.sum()), "max_abs": float(error.max()), "max_error_over_threshold": float((error / threshold).max()), "relative_l2": float(torch.linalg.vector_norm(actual.float() - reference.float()) / torch.linalg.vector_norm(reference.float()).clamp_min(1e-12)), "captured_global_statuses": [d["strict_refcheck_status"] for d in data]},
        "violations": violations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root, output = args.capture_root.resolve(), args.output.resolve()
    assert output != root and root not in output.parents and not output.exists()
    expected = {f"n{n}/rank{r}.pt" for n in (1, 3) for r in range(4)}
    assert {str(p.relative_to(root)) for p in root.rglob("*.pt")} == expected
    torch.set_num_threads(4)
    libname = ctypes.util.find_library("m")
    libm = ctypes.CDLL(libname)
    fmaf = libm.fmaf
    fmaf.argtypes = (ctypes.c_float, ctypes.c_float, ctypes.c_float)
    fmaf.restype = ctypes.c_float
    assert libm.fegetround() == 0, "Require round-to-nearest host arithmetic"
    manifests = {}
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(), "capture_root": str(root),
        "helper_sha256": sha(__file__), "execution": "CPU only; torch.load(map_location='cpu', weights_only=True)",
        "torch_version": torch.__version__, "cpu_fma_provider": libname, "rounding": "FE_TONEAREST; libm.fmaf binary32; torch BF16 cast",
        "timing_claim": "None. These are arithmetic reconstructions of saved diagnostic tensors, not GPU measurements.",
        "collective_limit": "Actual NCCL reduction schedule was not captured. Matching candidate trees reproduce observations but do not prove the actual NCCL algorithm/order. FP64 sums are diagnostic references, not a changed acceptance rule.",
        "cases": [analyze_case(root, n, fmaf, manifests) for n in (1, 3)],
        "input_payloads": manifests,
    }
    for relative, identity in manifests.items():
        assert sha(root / relative) == identity["sha256"], "Capture changed during analysis"
    report["input_before_after_sha_equal"] = True
    output.mkdir(parents=True, exist_ok=False)
    (output / "analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    lines = ["# Independent CPU replay of d1 captured numerics", "", "No GPU work or benchmark timing was performed. Original strict tolerance remains atol=rtol=.01. Input payload hashes are checked before and after analysis.", "", "| N | Input/route checks | FC2 terms equal | Mega FMA replay | Split partial replay | Original strict failures |", "|---:|---|---:|---|---|---:|"]
    for case in report["cases"]:
        lines.append(f"| {case['global_tokens']} | {all(case['checks'].values())} | {case['route_fc2']['bitwise_equal']} ({case['route_fc2']['elements']} terms) | {case['mega_k_order_fma_replay']['bitwise_equal']} | {all(p['bitwise_equal'] for p in case['split_owner_k_order_fma_replays'])} | {case['strict_original_elementwise']['failed_elements']} / {case['strict_original_elementwise']['elements']} |")
        lines += ["", f"## N={case['global_tokens']}", "", "Entire-row candidate BF16 sum trees reproducing actual collective output:", "", "```json", json.dumps(case["matching_tree_candidates_per_entire_token_row"], indent=2), "```", ""]
        for value in case["violations"]:
            lines += [f"### Token {value['global_token']}, hidden {value['hidden']}", "", "```json", json.dumps(value, indent=2), "```", ""]
    lines += ["## Interpretation boundary", "", "Per-route FC2/input/route bit equality localizes an observed final-output discrepancy to post-FC2 reduction for these captured executions. Bit-exact CPU FMA replay is checked against the saved GPU outputs and partials; it is not a universal GPU arithmetic guarantee. Intermediate BF16 rank-partial rounding and collective reduction are reported separately. The NCCL order was not logged, so candidate trees are arithmetic explanations rather than an identified transport algorithm.", "", "[Full checks, comparisons, exact violating values and input hashes](analysis.json)", ""]
    (output / "analysis.md").write_text("\n".join(lines))
    manifest = {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in output.iterdir() if p.is_file()}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(output), "cases": [{"n": c["global_tokens"], "input_route_checks": all(c['checks'].values()), "fc2_equal": c['route_fc2']['bitwise_equal'], "mega_replay_equal": c['mega_k_order_fma_replay']['bitwise_equal'], "split_partials_equal": all(p['bitwise_equal'] for p in c['split_owner_k_order_fma_replays']), "strict_failures": c['strict_original_elementwise']['failed_elements']} for c in report['cases']], "helper_sha256": report['helper_sha256']}))


if __name__ == "__main__":
    main()
