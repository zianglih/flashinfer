"""CPU-only shape and rank-layout contracts for the distributed MoE benchmark."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenLayout:
    counts: tuple[int, ...]
    offsets: tuple[int, ...]
    padded_positions: tuple[int, ...]
    valid_mask: tuple[bool, ...]
    per_rank_capacity: int
    padded_tokens: int


def token_layout(num_tokens: int, world_size: int) -> TokenLayout:
    """Map compact global token order to equal-sized, rank-major padded blocks."""
    if type(num_tokens) is not int or num_tokens <= 0:
        raise ValueError("Global token count must be a positive integer")
    if type(world_size) is not int or world_size <= 0:
        raise ValueError("World size must be a positive integer")
    quotient, remainder = divmod(num_tokens, world_size)
    counts = tuple(quotient + int(rank < remainder) for rank in range(world_size))
    offsets = tuple(
        rank * quotient + min(rank, remainder) for rank in range(world_size)
    )
    capacity = max(counts)
    positions = tuple(
        rank * capacity + row
        for rank, count in enumerate(counts)
        for row in range(count)
    )
    mask = tuple(row < count for count in counts for row in range(capacity))
    return TokenLayout(
        counts, offsets, positions, mask, capacity, capacity * world_size
    )


def resolve_megamoe_capacity(
    num_tokens: int, world_size: int, override: int | None
) -> int:
    live_capacity = token_layout(num_tokens, world_size).per_rank_capacity
    if override is None:
        return live_capacity
    if type(override) is not int or override < live_capacity:
        raise ValueError(
            f"MegaMoE capacity must be an integer >= live per-rank tokens ({live_capacity})"
        )
    return override


def model_shape(name: str) -> dict[str, int | float]:
    """Return a fresh profile; these are synthetic shapes, not checkpoint inputs."""
    if name not in ("deepseek-v3", "glm-5.2"):
        raise ValueError(f"Unknown model shape: {name}")
    return {
        "hidden_size": 6144 if name == "glm-5.2" else 7168,
        "intermediate_size": 2048,
        "num_experts": 256,
        "n_group": 1 if name == "glm-5.2" else 8,
        "topk_group": 1 if name == "glm-5.2" else 4,
        "top_k": 8,
        "routed_scaling_factor": 2.5,
    }


def validate_alignment_options(
    *,
    mode: str,
    parallel_modes: list[str],
    variants: list[str],
    ep_communication: str,
    megamoe_capacity: int | None,
) -> None:
    if ep_communication not in ("alltoall", "allgather", "allreduce"):
        raise ValueError(f"Unknown EP communication: {ep_communication}")
    if megamoe_capacity is not None:
        if type(megamoe_capacity) is not int or megamoe_capacity <= 0:
            raise ValueError("--megamoe-max-tokens-per-rank must be positive")
        if "w4a16_megamoe" not in variants or "ep" not in parallel_modes:
            raise ValueError(
                "--megamoe-max-tokens-per-rank requires the EP MegaMoE variant"
            )
    if ep_communication != "alltoall":
        if parallel_modes != ["ep"] or "w4a16" not in variants or "w4a4" in variants:
            raise ValueError(
                "Gather/reduce EP modes require --parallel-modes ep and split w4a16, "
                "optionally w4a16_megamoe; W4A4 is not supported"
            )
        if mode == "profile_ncu":
            raise ValueError(
                "Gather/reduce EP modes do not support the single-process NCU "
                "compute simulation; use profile_nsys for real collectives"
            )


def alignment_worker_arguments(
    shape: str, ep_communication: str, megamoe_capacity: int | None
) -> list[str]:
    arguments = ["--model-shape", shape, "--ep-communication", ep_communication]
    if megamoe_capacity is not None:
        arguments += ["--megamoe-max-tokens-per-rank", str(megamoe_capacity)]
    return arguments
