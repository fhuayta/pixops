"""Local image utilities: resize, convert, compress, grayscale, canvas."""

from pixops.exceptions import PixOpsError, OutputError, TransformError, UnsupportedInputError
from pixops.io import load_image, save_bytes
from pixops.ops import (
    blur,
    border,
    canvas,
    crop,
    encode_under_bytes,
    grayscale,
    pad,
    resize,
    round_corners,
    sharpen,
    strip_metadata,
)
from pixops.pipeline import ProcessResult, process, process_many

__all__ = [
    "PixOpsError",
    "OutputError",
    "ProcessResult",
    "TransformError",
    "UnsupportedInputError",
    "blur",
    "border",
    "canvas",
    "crop",
    "encode_under_bytes",
    "grayscale",
    "load_image",
    "pad",
    "process",
    "process_many",
    "resize",
    "round_corners",
    "save_bytes",
    "sharpen",
    "strip_metadata",
    "__version__",
]

__version__ = "0.1.8"
