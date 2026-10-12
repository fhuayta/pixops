# Usage

Install first (`pip install -e .`). Without `-o`, a single file is written next to the source as `name_pix.ext`.

## Resize

```bash
pixops photo.jpg --max 1200
```

```python
from pixops import process

process("photo.jpg", "photo.webp", max_side=1200)
```

## Crop

Square from the center, then optionally shrink:

```bash
pixops photo.jpg --crop 1:1 --max 1200
```

```python
from pixops import process

process("photo.jpg", "square.webp", crop="1:1", max_side=1200)
```

A pixel box is `left,top,width,height`:

```bash
pixops photo.jpg --crop 10,20,400,300 -o cut.png
```

## Sharpen

Unsharp after resize so downscaled photos stay crisp:

```bash
pixops photo.jpg --max 1200 --sharpen
```

```python
from pixops import process

process("photo.jpg", "photo.webp", max_side=1200, sharpen=True)
```

## Grayscale

```bash
pixops photo.jpg --gray -o photo-gray.png
```

```python
from pixops import process

process("photo.jpg", "photo-gray.png", gray=True)
```

## Catalog canvas

Every product on a 1000×1000 white square:

```bash
pixops shots/ -o tiles/ --canvas 1000x1000 --bg "#FFFFFF"
```

```python
from pixops import process_many

process_many("shots/", "tiles/", canvas_size=(1000, 1000), background="#FFFFFF")
```

A cutout keeps transparent margins on PNG or WebP. JPEG flattens them to white:

```bash
pixops cutout.png --canvas 1000x1000 --bg transparent -o tile.png
```

```python
process("cutout.png", "tile.png", canvas_size=(1000, 1000), background="transparent")
```

## Padding

Add a margin and keep the photo the same size. `40` is every side. `10,20` is vertical, then horizontal. `10,20,10,20` is top, right, bottom, left.

```bash
pixops cutout.png --pad 40 --bg transparent -o padded.png
```

```python
process("cutout.png", "padded.png", pad=40, background="transparent")
```

## Strip metadata

Orientation is fixed on load. Use `--strip` if the output should not keep the remaining EXIF or ICC profile:

```bash
pixops photo.jpg --max 1200 --strip -o clean.jpg
```

```python
process("photo.jpg", "clean.jpg", max_side=1200, strip=True)
```

## Smallest useful file

```bash
pixops photo.jpg --format webp --max-bytes 150kb
```

```python
process("photo.jpg", "photo.webp", fmt="webp", max_bytes="150kb")
```

Quality falls first; if that is not enough the image is scaled down until it fits.

## Scripts in this repo

```bash
python examples/resize_one.py photo.jpg
python examples/catalog_tile.py product.jpg
```
