from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from pixops.exceptions import OutputError, UnsupportedInputError
from pixops.io import default_output_path, list_images, load_image, parse_bytes


def test_load_image_from_path(tmp_path: Path) -> None:
    path = tmp_path / "photo.png"
    Image.new("RGB", (8, 8), "red").save(path)
    assert load_image(path).size == (8, 8)


def test_load_image_applies_exif_orientation(tmp_path: Path) -> None:
    path = tmp_path / "rotated.jpg"
    image = Image.new("RGB", (20, 10), "navy")
    exif = image.getexif()
    exif[274] = 6
    image.save(path, exif=exif)
    assert load_image(path).size == (10, 20)


def test_load_image_bytes_apply_exif() -> None:
    image = Image.new("RGB", (20, 10), "navy")
    exif = image.getexif()
    exif[274] = 6
    buf = BytesIO()
    image.save(buf, format="JPEG", exif=exif)
    assert load_image(buf.getvalue()).size == (10, 20)


def test_list_images_skips_text(tmp_path: Path) -> None:
    Image.new("RGB", (4, 4), "blue").save(tmp_path / "a.jpg")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")
    assert [p.name for p in list_images(tmp_path)] == ["a.jpg"]


def test_default_output_path_next_to_source(tmp_path: Path) -> None:
    source = tmp_path / "portrait.jpg"
    assert default_output_path(source, None) == tmp_path / "portrait_pix.jpg"


def test_parse_bytes() -> None:
    assert parse_bytes("150kb") == 150_000
    assert parse_bytes("2mb") == 2_000_000
    assert parse_bytes(500) == 500
    with pytest.raises(OutputError):
        parse_bytes("nope")


def test_load_missing(tmp_path: Path) -> None:
    with pytest.raises(UnsupportedInputError):
        load_image(tmp_path / "missing.png")
