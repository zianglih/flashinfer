"""Source-audited metadata for the public benchmark's distinct result labels."""

from copy import deepcopy

INITIAL_ACTIVATION_QUANTIZATION = {"nvfp4": True, "mxfp": False}

PER_TOKEN_RECIPE = {"e4m3_max": 256, "err_mode": "MSE", "err_use_fast_math": True}
BACKEND_LABELS = {
    "cutedsl": ("CuteDSL W4A4", "CuteDSL W4A16"),
    "cute-dsl-per-token": ("CuteDSL PER-TOKEN",),
    "trtllm-per-token": ("TRTLLM PER-TOKEN",),
    "cutlass": ("CUTLASS",),
    "trtllm-nvfp4": ("TRTLLM NVFP4",),
    "trtllm-bf16": ("TRTLLM BF16",),
    "cute-dsl-w4a8": ("CuteDSL MXFP4x8",),
    "cute-dsl-mxfp8": ("CuteDSL MXFP8",),
    "trtllm-mxfp4": ("TRTLLM MXFP4x8",),
    "trtllm-mxfp8": ("TRTLLM MXFP8",),
}
DEFAULT_LABELS = {
    "nvfp4": ("CuteDSL W4A4", "CuteDSL PER-TOKEN", "CuteDSL W4A16", "TRTLLM NVFP4", "TRTLLM PER-TOKEN", "TRTLLM BF16"),
    "mxfp": ("CuteDSL MXFP4x8", "CuteDSL MXFP8", "TRTLLM MXFP4x8", "TRTLLM MXFP8", "TRTLLM BF16"),
}


def arm_contract(label):
    if label in ("CuteDSL PER-TOKEN", "TRTLLM PER-TOKEN"):
        return {
            "per_token_activation": True,
            "activation_recipe": deepcopy(PER_TOKEN_RECIPE),
            "activation_recipe_wire_code": 23,
            "activation_inverse_global_scale": 1 / (256 * 6),
            "disable_nvfp4_quant_fast_math": True,
            "initial_activation_quantization_timed": True,
            "fc2_activation_quantization_timed": True,
            "weight_recipe": None,
            "weight_disable_nvfp4_quant_fast_math": False,
            "scope": "Activation-only recipe. Initial activation quantization and FC2 requantization are both inside timing. Shared weights use standard NVFP4 outside the scoped activation fast-math setting.",
        }
    if label in ("CuteDSL W4A4", "TRTLLM NVFP4", "CuteDSL W4A16", "CUTLASS"):
        return {
            "per_token_activation": False,
            "activation_recipe": None,
            "disable_nvfp4_quant_fast_math": False,
            "initial_activation_quantization_timed": label in ("CuteDSL W4A4", "TRTLLM NVFP4", "CUTLASS"),
            "weight_recipe": None,
            "weight_disable_nvfp4_quant_fast_math": False,
            "scope": "Standard NVFP4 quantization is timed for quantized-input arms; W4A16 consumes BF16 directly. No per-token activation or 4over6 recipe.",
        }
    if label in ("CuteDSL MXFP4x8", "CuteDSL MXFP8", "TRTLLM MXFP4x8", "TRTLLM MXFP8", "TRTLLM BF16"):
        return {
            "per_token_activation": False,
            "activation_recipe": None,
            "disable_nvfp4_quant_fast_math": None,
            "initial_activation_quantization_timed": False,
            "weight_recipe": None,
            "weight_disable_nvfp4_quant_fast_math": None,
            "scope": "NVFP4 per-token recipe does not apply.",
        }
    raise ValueError(f"Unknown benchmark arm: {label}")

# Source-audited K3 SiTU support on Blackwell. Missing arms are never timed.
UNAVAILABLE_LABELS = {
    "nvfp4": ("TRTLLM PER-TOKEN", "TRTLLM BF16"),
    "mxfp": ("TRTLLM MXFP8", "TRTLLM BF16"),
}


def unavailable_labels(model, family, labels=None):
    if model in ("v3", "v41-flash", "nemo3-ultra"):
        unavailable = ()
    elif model == "kimi-k3":
        unavailable = (*UNAVAILABLE_LABELS[family], "CUTLASS")
    else:
        raise ValueError(f"Unknown model: {model}")
    selected = DEFAULT_LABELS[family] if labels is None else labels
    return tuple(label for label in selected if label in unavailable)


def selected_labels(family, selectors):
    if selectors is None:
        return DEFAULT_LABELS[family]
    labels = tuple(label for selector in selectors.split(",") for label in BACKEND_LABELS[selector])
    if len(labels) != len(set(labels)):
        raise ValueError("Backend selectors overlap")
    return labels
