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
