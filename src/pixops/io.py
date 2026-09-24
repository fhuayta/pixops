from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from PIL import Image, ImageOps

from pixops.exceptions import OutputError, UnsupportedInputError

ImageSource = str | Path | Image.Image | bytes | BinaryIO

IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def _finalize(image: Image.Image) -> Image.Image:
    image.load()
    oriented = ImageOps.exif_transpose(image)
    return (oriented or image).copy()


def load_image(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source.copy()

    if isinstance(source, (bytes, bytearray)):
        with Image.open(BytesIO(source)) as image:
            return _finalize(image)

    if hasattr(source, "read"):
        opened = Image.open(source)
        return _finalize(opened)

    path = Path(source)
    if not path.is_file():
        raise UnsupportedInputError(f"file not found: {path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise UnsupportedInputError(
            f"unsupported format {path.suffix or path.name!r}; "
            f"expected {', '.join(sorted(IMAGE_EXTENSIONS))}"
        )
    with Image.open(path) as image:
        return _finalize(image)


def list_images(source: str | Path, *, recursive: bool = False) -> list[Path]:
    path = Path(source)
    if path.is_file():
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedInputError(f"not a supported image: {path}")
        return [path]
    if not path.is_dir():
        raise UnsupportedInputError(f"path not found: {path}")

    iterator = path.rglob("*") if recursive else path.glob("*")
    images = sorted(
        p for p in iterator if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        raise UnsupportedInputError(f"no images in {path}")
    return images


def default_output_path(
    source: Path,
    output: str | Path | None,
    *,
    suffix: str = "_pix",
    ext: str | None = None,
    is_batch: bool = False,
) -> Path:
    ending = ext if ext else (source.suffix.lower() or ".png")
    if not ending.startswith("."):
        ending = f".{ending}"
    filename = f"{source.stem}{suffix}{ending}"
    if output is None:
        return source.with_name(filename)

    output_path = Path(output)
    if is_batch or output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / filename

    if output_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise OutputError(f"unsupported output extension: {output_path.suffix}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def parse_bytes(value: str | int) -> int:
    if isinstance(value, int):
        if value <= 0:
            raise OutputError("max bytes must be positive")
        return value
    raw = value.strip().lower().replace(" ", "")
    multipliers = {
        "k": 1000,
        "kb": 1000,
        "m": 1_000_000,
        "mb": 1_000_000,
    }
    for suffix, factor in multipliers.items():
        if raw.endswith(suffix):
            number = raw[: -len(suffix)]
            try:
                return int(float(number) * factor)
            except ValueError as exc:
                raise OutputError(f"invalid size: {value!r}") from exc
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise OutputError(f"invalid size: {value!r}") from exc
    if parsed <= 0:
        raise OutputError("max bytes must be positive")
    return parsed


def save_bytes(payload: bytes, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return destination
