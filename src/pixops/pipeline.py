from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image

from pixops.exceptions import OutputError
from pixops.io import (
    ImageSource,
    default_output_path,
    list_images,
    load_image,
    parse_bytes,
)
from pixops.ops import (
    canvas,
    crop as crop_image,
    encode_image,
    encode_under_bytes,
    flip,
    grayscale,
    resize,
    rotate,
)

ProgressCallback = Callable[[int, int, Path], None]


@dataclass
class ProcessResult:
    image: Image.Image
    source: Path | None = None
    output: Path | None = None
    bytes_written: int | None = None


def _output_format(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    if ext == "jpg":
        return "JPEG"
    return ext.upper() or "PNG"


def process(
    source: ImageSource,
    output: str | Path | None = None,
    *,
    max_side: int | None = None,
    width: int | None = None,
    height: int | None = None,
    fit: str = "contain",
    crop: str | tuple[int, int] | tuple[int, int, int, int] | None = None,
    canvas_size: tuple[int, int] | None = None,
    background: str = "#FFFFFF",
    gray: bool = False,
    degrees: float = 0,
    flip_x: bool = False,
    flip_y: bool = False,
    quality: int = 85,
    max_bytes: int | str | None = None,
    suffix: str = "_pix",
    fmt: str | None = None,
) -> ProcessResult:
    image = load_image(source)
    if crop is not None:
        image = crop_image(image, crop)
    image = resize(image, max_side=max_side, width=width, height=height, fit=fit)
    if canvas_size:
        image = canvas(image, canvas_size[0], canvas_size[1], color=background)
    if gray:
        image = grayscale(image)
    if degrees:
        image = rotate(image, degrees)
    if flip_x or flip_y:
        image = flip(image, horizontal=flip_x, vertical=flip_y)

    src_path = source if isinstance(source, Path) else None
    if isinstance(source, str):
        src_path = Path(source)

    dest: Path | None = None
    if output is not None or src_path is not None:
        dest = default_output_path(
            src_path or Path("image.png"),
            output,
            suffix=suffix,
            ext=fmt,
        )

    written: int | None = None
    if dest is not None:
        codec = fmt or _output_format(dest)
        limit = parse_bytes(max_bytes) if max_bytes is not None else None
        payload = (
            encode_under_bytes(image, codec, limit)
            if limit
            else encode_image(image, codec, quality=quality)
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(payload)
        written = len(payload)

    return ProcessResult(image=image, source=src_path, output=dest, bytes_written=written)


def process_many(
    source: str | Path,
    output: str | Path | None = None,
    *,
    recursive: bool = False,
    suffix: str = "_pix",
    fmt: str | None = None,
    progress: ProgressCallback | None = None,
    **kwargs: object,
) -> list[ProcessResult]:
    paths = list_images(source, recursive=recursive)
    is_batch = Path(source).is_dir()
    if is_batch and output and Path(output).suffix:
        raise OutputError("folder input needs a directory as -o, not a single file")
    results: list[ProcessResult] = []
    for index, path in enumerate(paths, start=1):
        if progress:
            progress(index, len(paths), path)
        dest = default_output_path(
            path,
            output,
            suffix=suffix,
            ext=fmt,
            is_batch=is_batch,
        )
        results.append(process(path, dest, suffix="", fmt=fmt, **kwargs))  # type: ignore[arg-type]
    return results
