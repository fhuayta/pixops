from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pixops.exceptions import PixOpsError
from pixops.ops import parse_size
from pixops.pipeline import process_many


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pixops",
        description="Resize, convert, compress, or recolor a photo or a folder of photos.",
        epilog=(
            "examples:\n"
            "  pixops photo.jpg --max 1200\n"
            "  pixops photo.jpg --gray -o photo-gray.png\n"
            "  pixops shots/ -o out/ --max 1000 --canvas 1000x1000 --bg '#FFFFFF'\n"
            "  pixops photo.jpg --format webp --max-bytes 150kb"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="image file or directory")
    parser.add_argument("-o", "--output", help="output file or directory")
    parser.add_argument(
        "--max",
        dest="max_side",
        type=int,
        metavar="PX",
        help="longest side in pixels; keeps aspect ratio",
    )
    parser.add_argument("--width", type=int, help="target width in pixels")
    parser.add_argument("--height", type=int, help="target height in pixels")
    parser.add_argument(
        "--fit",
        choices=("contain", "cover", "stretch"),
        default="contain",
        help="how to fill width x height (default: contain)",
    )
    parser.add_argument(
        "--canvas",
        metavar="WxH",
        help="letterbox onto a fixed canvas, e.g. 1000x1000",
    )
    parser.add_argument(
        "--bg",
        default="#FFFFFF",
        help="hex fill for the canvas (default: #FFFFFF)",
    )
    parser.add_argument("--gray", action="store_true", help="convert to grayscale")
    parser.add_argument("--rotate", type=float, default=0, metavar="DEG")
    parser.add_argument("--flip-x", action="store_true")
    parser.add_argument("--flip-y", action="store_true")
    parser.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality (default: 85)")
    parser.add_argument(
        "--max-bytes",
        metavar="SIZE",
        help="shrink quality (then size) until the file fits, e.g. 150kb",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        help="output format: png, jpg, webp, avif",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="include subdirectories when the input is a folder",
    )
    parser.add_argument(
        "--suffix",
        default="_pix",
        help="filename suffix in batch mode (default: _pix)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    source = Path(args.input)
    if not source.exists():
        parser.error(f"not found: {source}")

    canvas_size = parse_size(args.canvas) if args.canvas else None

    def progress(index: int, total: int, path: Path) -> None:
        print(f"[{index}/{total}] {path}", file=sys.stderr)

    try:
        results = process_many(
            source,
            args.output,
            recursive=args.recursive,
            suffix=args.suffix,
            fmt=args.fmt,
            max_side=args.max_side,
            width=args.width,
            height=args.height,
            fit=args.fit,
            canvas_size=canvas_size,
            background=args.bg,
            gray=args.gray,
            degrees=args.rotate,
            flip_x=args.flip_x,
            flip_y=args.flip_y,
            quality=args.quality,
            max_bytes=args.max_bytes,
            progress=progress if source.is_dir() else None,
        )
    except PixOpsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for result in results:
        if result.output is not None:
            extra = f"  {result.bytes_written}B" if result.bytes_written else ""
            print(f"{result.output}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
