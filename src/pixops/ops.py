from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps

from pixops.exceptions import TransformError

Fit = str


def parse_hex_color(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6:
        raise TransformError(f"invalid hex color: {value!r}")
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError as exc:
        raise TransformError(f"invalid hex color: {value!r}") from exc


def parse_size(value: str) -> tuple[int, int]:
    parts = value.lower().replace(" ", "").split("x")
    if len(parts) != 2:
        raise TransformError(f"size must look like 1000x1000, got {value!r}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise TransformError(f"size must look like 1000x1000, got {value!r}") from exc
    if width <= 0 or height <= 0:
        raise TransformError("width and height must be positive")
    return width, height


def resize(
    image: Image.Image,
    *,
    max_side: int | None = None,
    width: int | None = None,
    height: int | None = None,
    fit: Fit = "contain",
) -> Image.Image:
    if max_side is not None and max_side <= 0:
        raise TransformError("max_side must be positive")
    if fit not in {"contain", "cover", "stretch"}:
        raise TransformError(f"unknown fit {fit!r}")

    src = image
    if max_side and not width and not height:
        longest = max(src.size)
        if longest <= max_side:
            return src.copy()
        scale = max_side / longest
        size = (max(1, round(src.width * scale)), max(1, round(src.height * scale)))
        return src.resize(size, Image.Resampling.LANCZOS)

    if width and height:
        box = (width, height)
        if fit == "stretch":
            return src.resize(box, Image.Resampling.LANCZOS)
        if fit == "cover":
            return ImageOps.fit(src, box, method=Image.Resampling.LANCZOS)
        fitted = ImageOps.contain(src, box, method=Image.Resampling.LANCZOS)
        return fitted

    if width:
        scale = width / src.width
        size = (width, max(1, round(src.height * scale)))
        return src.resize(size, Image.Resampling.LANCZOS)
    if height:
        scale = height / src.height
        size = (max(1, round(src.width * scale)), height)
        return src.resize(size, Image.Resampling.LANCZOS)
    return src.copy()


def grayscale(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"}:
        alpha = image.getchannel("A")
        gray = ImageOps.grayscale(image.convert("RGB")).convert("RGBA")
        gray.putalpha(alpha)
        return gray
    return ImageOps.grayscale(image)


def canvas(
    image: Image.Image,
    width: int,
    height: int,
    *,
    color: str = "#FFFFFF",
) -> Image.Image:
    if width <= 0 or height <= 0:
        raise TransformError("canvas size must be positive")
    rgb = parse_hex_color(color)
    has_alpha = image.mode in {"RGBA", "LA"}
    mode = "RGBA" if has_alpha else "RGB"
    fill: tuple[int, ...] = (*rgb, 255) if mode == "RGBA" else rgb
    board = Image.new(mode, (width, height), fill)
    fitted = ImageOps.contain(image.convert(mode), (width, height), method=Image.Resampling.LANCZOS)
    x = (width - fitted.width) // 2
    y = (height - fitted.height) // 2
    if has_alpha:
        board.paste(fitted, (x, y), fitted)
    else:
        board.paste(fitted, (x, y))
    return board


def rotate(image: Image.Image, degrees: float) -> Image.Image:
    return image.rotate(-degrees, expand=True, resample=Image.Resampling.BICUBIC)


def flip(image: Image.Image, *, horizontal: bool = False, vertical: bool = False) -> Image.Image:
    out = image
    if horizontal:
        out = ImageOps.mirror(out)
    if vertical:
        out = ImageOps.flip(out)
    return out


def encode_image(
    image: Image.Image,
    fmt: str,
    *,
    quality: int = 85,
) -> bytes:
    fmt = fmt.upper()
    if fmt == "JPG":
        fmt = "JPEG"
    buf = BytesIO()
    to_save = image
    save_kwargs: dict[str, object] = {}

    if fmt == "JPEG":
        if to_save.mode in {"RGBA", "LA"}:
            bg = Image.new("RGB", to_save.size, (255, 255, 255))
            bg.paste(to_save, mask=to_save.split()[-1])
            to_save = bg
        elif to_save.mode != "RGB":
            to_save = to_save.convert("RGB")
        save_kwargs = {"quality": quality, "optimize": True}
    elif fmt == "WEBP":
        save_kwargs = {"quality": quality, "method": 4}
    elif fmt == "PNG":
        save_kwargs = {"optimize": True}
    elif fmt == "AVIF":
        save_kwargs = {"quality": quality}

    to_save.save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def encode_under_bytes(
    image: Image.Image,
    fmt: str,
    max_bytes: int,
    *,
    min_quality: int = 35,
) -> bytes:
    """Drop quality, then scale, until the file fits under max_bytes."""
    if max_bytes <= 0:
        raise TransformError("max_bytes must be positive")

    working = image
    for _ in range(8):
        for quality in range(90, min_quality - 1, -5):
            payload = encode_image(working, fmt, quality=quality)
            if len(payload) <= max_bytes:
                return payload
        next_w = max(1, int(working.width * 0.85))
        next_h = max(1, int(working.height * 0.85))
        if (next_w, next_h) == working.size:
            break
        working = working.resize((next_w, next_h), Image.Resampling.LANCZOS)

    payload = encode_image(working, fmt, quality=min_quality)
    if len(payload) > max_bytes:
        raise TransformError(
            f"could not fit image under {max_bytes} bytes (got {len(payload)})"
        )
    return payload
