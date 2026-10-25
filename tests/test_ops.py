import pytest
from PIL import Image

from pixops.exceptions import TransformError
from pixops.ops import (
    blur,
    canvas,
    crop,
    encode_image,
    encode_under_bytes,
    grayscale,
    pad,
    resize,
    sharpen,
    strip_metadata,
)


def test_resize_max_side() -> None:
    image = Image.new("RGB", (2000, 1000), "red")
    out = resize(image, max_side=1000)
    assert out.size == (1000, 500)


def test_resize_skips_when_already_small() -> None:
    image = Image.new("RGB", (100, 80), "red")
    out = resize(image, max_side=1000)
    assert out.size == (100, 80)


def test_grayscale_keeps_alpha() -> None:
    image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
    out = grayscale(image)
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 128


def test_canvas_centers() -> None:
    image = Image.new("RGB", (20, 10), "red")
    out = canvas(image, 40, 40, color="#00FF00")
    assert out.size == (40, 40)
    assert out.mode == "RGB"
    assert out.getpixel((0, 0)) == (0, 255, 0)


def test_canvas_transparent_margins() -> None:
    image = Image.new("RGBA", (20, 10), (255, 0, 0, 255))
    out = canvas(image, 40, 40, color="transparent")
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0)) == (0, 0, 0, 0)
    assert out.getpixel((20, 20)) == (255, 0, 0, 255)


def test_canvas_hex_alpha() -> None:
    image = Image.new("RGB", (20, 10), "red")
    out = canvas(image, 40, 40, color="#00FF0080")
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0)) == (0, 255, 0, 128)
    assert out.getpixel((20, 20)) == (255, 0, 0, 255)


def test_pad_uniform() -> None:
    image = Image.new("RGB", (20, 10), "red")
    out = pad(image, 40, color="#FFFFFF")
    assert out.size == (100, 90)
    assert out.mode == "RGB"
    assert out.getpixel((0, 0)) == (255, 255, 255)
    assert out.getpixel((40, 40)) == (255, 0, 0)


def test_pad_axes_and_transparent() -> None:
    image = Image.new("RGBA", (20, 10), (255, 0, 0, 255))
    out = pad(image, "10,20", color="transparent")
    assert out.size == (60, 30)
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0)) == (0, 0, 0, 0)
    assert out.getpixel((20, 10)) == (255, 0, 0, 255)


def test_pad_rejects_negative() -> None:
    image = Image.new("RGB", (8, 8), "red")
    with pytest.raises(TransformError, match="negative"):
        pad(image, "-4")


def test_canvas_rejects_bad_color() -> None:
    image = Image.new("RGB", (8, 8), "red")
    with pytest.raises(TransformError, match="invalid color"):
        canvas(image, 16, 16, color="red")


def test_encode_under_bytes() -> None:
    image = Image.new("RGB", (800, 800), "navy")
    payload = encode_under_bytes(image, "JPEG", 8_000)
    assert len(payload) <= 8_000
    assert payload[:2] == b"\xff\xd8"


def test_strip_metadata_clears_info() -> None:
    image = Image.new("RGB", (8, 8), "red")
    image.info["exif"] = b"Exif\x00\x00"
    image.info["icc_profile"] = b"profile"
    out = strip_metadata(image)
    assert "exif" not in out.info
    assert "icc_profile" not in out.info
    assert "exif" in image.info


def test_encode_keeps_and_strips_exif() -> None:
    image = Image.new("RGB", (32, 16), "navy")
    exif = image.getexif()
    exif[271] = "TestCam"
    from io import BytesIO

    buf = BytesIO()
    image.save(buf, format="JPEG", exif=exif, quality=90)
    loaded = Image.open(BytesIO(buf.getvalue()))
    loaded.load()

    kept = encode_image(loaded, "JPEG", quality=90, strip=False)
    stripped = encode_image(loaded, "JPEG", quality=90, strip=True)
    assert dict(Image.open(BytesIO(kept)).getexif()).get(271) == "TestCam"
    assert dict(Image.open(BytesIO(stripped)).getexif()) == {}


def test_crop_square_from_landscape() -> None:
    image = Image.new("RGB", (200, 100), "red")
    out = crop(image, "1:1")
    assert out.size == (100, 100)


def test_crop_ratio_tuple() -> None:
    image = Image.new("RGB", (200, 100), "red")
    out = crop(image, (4, 5))
    assert out.size == (80, 100)


def test_crop_box() -> None:
    image = Image.new("RGB", (200, 100), "red")
    image.putpixel((15, 25), (0, 255, 0))
    out = crop(image, "10,20,40,30")
    assert out.size == (40, 30)
    assert out.getpixel((5, 5)) == (0, 255, 0)


def test_crop_box_outside_raises() -> None:
    image = Image.new("RGB", (20, 20), "red")
    with pytest.raises(TransformError, match="outside"):
        crop(image, "10,10,20,20")


def test_blur_softens_a_hard_edge() -> None:
    image = Image.new("RGB", (20, 20), "white")
    for y in range(20):
        image.putpixel((0, y), (0, 0, 0))
    out = blur(image, 2)
    assert out.size == (20, 20)
    assert out.mode == "RGB"
    neighbor = out.getpixel((1, 10))
    assert neighbor != (255, 255, 255)
    assert neighbor != (0, 0, 0)


def test_blur_feathers_alpha() -> None:
    image = Image.new("RGBA", (20, 20), (255, 0, 0, 0))
    image.putpixel((10, 10), (255, 0, 0, 255))
    out = blur(image, 1)
    assert out.mode == "RGBA"
    assert out.getpixel((11, 10))[3] > 0
    assert out.getpixel((10, 10))[3] < 255


def test_blur_rejects_non_positive_radius() -> None:
    image = Image.new("RGB", (8, 8), "red")
    with pytest.raises(TransformError, match="radius"):
        blur(image, 0)


def test_sharpen_keeps_size_and_alpha() -> None:
    image = Image.new("RGBA", (40, 40), (200, 200, 200, 180))
    for x in range(20):
        for y in range(40):
            image.putpixel((x, y), (80, 80, 80, 180))
    out = sharpen(image)
    assert out.size == (40, 40)
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 180
    assert out.tobytes() != image.tobytes()


def test_sharpen_rejects_bad_percent() -> None:
    image = Image.new("RGB", (8, 8), "red")
    with pytest.raises(TransformError, match="percent"):
        sharpen(image, percent=0)
