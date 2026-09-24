import pytest
from PIL import Image

from pixops.exceptions import TransformError
from pixops.ops import canvas, crop, encode_under_bytes, grayscale, resize


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
    assert out.getpixel((0, 0)) == (0, 255, 0)


def test_encode_under_bytes() -> None:
    image = Image.new("RGB", (800, 800), "navy")
    payload = encode_under_bytes(image, "JPEG", 8_000)
    assert len(payload) <= 8_000
    assert payload[:2] == b"\xff\xd8"


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
