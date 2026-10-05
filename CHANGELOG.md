# Changelog

## 0.1.3

- Canvas fill can be `transparent` or an 8-digit hex (`#RRGGBBAA`). Opaque `#RRGGBB` is unchanged. Use PNG or WebP if the margins should stay transparent.

## 0.1.2

- Unsharp mask after transforms (`--sharpen` / `sharpen=True`). Useful after resize.

## 0.1.1

- Center crop by ratio (`--crop 1:1`) or box (`--crop 10,20,400,300`). Crop runs before resize.

## 0.1.0

- First release: resize, grayscale, canvas, format conversion, quality, and max-bytes encode.
- CLI `pixops` and batch folders. EXIF orientation on load.
