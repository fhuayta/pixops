# pixops

Local image utilities. Resize, convert, compress, grayscale, or drop a photo onto a fixed canvas. Nothing is uploaded.

Sister library of [cleanbg](https://github.com/fhuayta/cleanbg) (background removal). This package is only [Pillow](https://python-pillow.org/) — no ONNX models, no GPU.

## Install

Python 3.11+.

```bash
pip install -e .
```

Later, from PyPI:

```bash
pip install pixops
```

## CLI

```bash
pixops photo.jpg --max 1200
pixops photo.jpg --gray -o photo-gray.png
pixops photo.jpg --format webp --quality 80
pixops photo.jpg --max-bytes 150kb --format webp
pixops product.jpg --canvas 1000x1000 --bg "#FFFFFF" -o product.png
pixops shots/ -o out/ --max 1000
```

Without `-o`, a single file is written next to the source as `photo_pix.jpg`. `python -m pixops` does the same as the CLI.

## Library

```python
from pixops import process

result = process("photo.jpg", "photo.webp", max_side=1200, quality=80)
print(result.output, result.bytes_written)
```

`source` can be a path, `Path`, `PIL.Image`, bytes, or an open file. Skip `output` if you only want the image object.

A folder does not need a model — each file is cheap:

```python
from pixops import process_many

for item in process_many("shots/", "out/", max_side=1000, gray=True):
    print(item.source, "->", item.output)
```

Catalog tile (subject fitted, white square):

```python
process(
    "product.jpg",
    "tile.png",
    canvas_size=(1000, 1000),
    background="#FFFFFF",
)
```

## What it does

| Flag / argument | Effect |
| --- | --- |
| `--max` / `max_side` | longest side, keep aspect |
| `--width` `--height` `--fit` | box with contain, cover, or stretch |
| `--canvas` / `canvas_size` | letterbox onto WxH |
| `--bg` / `background` | hex fill for the canvas |
| `--gray` / `gray` | black and white |
| `--format` / `fmt` | png, jpg, webp, avif |
| `--quality` | JPEG/WebP quality |
| `--max-bytes` | drop quality, then scale, until it fits |
| `--rotate` `--flip-x` `--flip-y` | geometry |
| `-r` / `--suffix` | recurse folders; default filename suffix `_pix` |

Phone JPEGs are rotated from EXIF before any transform.

Copy-paste recipes: [USAGE.md](USAGE.md). Runnable scripts live in `examples/`.

## How it works

`pixops` is a thin API over Pillow. It loads the photo, applies the transforms you asked for (resize, canvas, grayscale, rotate, flip), then encodes PNG, JPEG, WebP, or AVIF. `--max-bytes` lowers quality first and scales the image only if it still does not fit. Everything runs on your machine.

## License

MIT © [Franz Huayta Quevedo](https://github.com/fhuayta).
