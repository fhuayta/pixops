from pathlib import Path

from PIL import Image

from pixops.cli import main
from pixops.pipeline import process, process_many


def test_process_writes_webp(tmp_path: Path) -> None:
    src = tmp_path / "in.jpg"
    Image.new("RGB", (400, 200), "orange").save(src, quality=90)
    dest = tmp_path / "out.webp"
    result = process(src, dest, max_side=200, quality=80)
    assert result.output == dest
    assert dest.is_file()
    assert Image.open(dest).size == (200, 100)
    assert result.bytes_written and result.bytes_written > 0


def test_process_many_folder(tmp_path: Path) -> None:
    folder = tmp_path / "shots"
    folder.mkdir()
    Image.new("RGB", (30, 30), "red").save(folder / "a.png")
    Image.new("RGB", (30, 30), "blue").save(folder / "b.png")
    out = tmp_path / "out"
    results = process_many(folder, out, gray=True)
    assert len(results) == 2
    assert (out / "a_pix.png").is_file()


def test_cli_max_side(tmp_path: Path) -> None:
    src = tmp_path / "photo.png"
    Image.new("RGB", (300, 150), "teal").save(src)
    dest = tmp_path / "small.png"
    assert main([str(src), "--max", "150", "-o", str(dest)]) == 0
    assert Image.open(dest).size == (150, 75)


def test_process_crop_then_max(tmp_path: Path) -> None:
    src = tmp_path / "wide.png"
    Image.new("RGB", (400, 200), "orange").save(src)
    dest = tmp_path / "square.png"
    result = process(src, dest, crop="1:1", max_side=100)
    assert Image.open(dest).size == (100, 100)
    assert result.bytes_written and result.bytes_written > 0


def test_cli_crop(tmp_path: Path) -> None:
    src = tmp_path / "photo.png"
    Image.new("RGB", (300, 150), "teal").save(src)
    dest = tmp_path / "square.png"
    assert main([str(src), "--crop", "1:1", "-o", str(dest)]) == 0
    assert Image.open(dest).size == (150, 150)
