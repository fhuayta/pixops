from PIL import Image

from pixops.ops import canvas, encode_under_bytes, grayscale, resize


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
